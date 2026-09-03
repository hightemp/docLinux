# Resolve IP адресов в Linux: понятное и детальное описание

Источник: [Resolve IP адресов в Linux: понятное и детальное описание](https://habr.com/ru/articles/352300/)

Настройка сетевого взаимодействия сервисов не самая простая задача и часто осуществляется без глубокого понимания как требуется настраивать систему и какие настройки на что влияют. После миграции сервисов в docker контейнерах с centos 6 на centos 7 я столкнулся со странным поведением вебсервера: он пытался присоединиться к сервису по IPv6, а сервис же слушал только IPv4 адрес. Стандартный совет в такой ситуации — отключить поддержку IPv6. Но это не поможет в ряде случаев. Каких? В этой статье я задался целью собрать и детально объяснить как приложения `resolve`'ят адреса.

Публикация будет полезна начинающим администраторам и разработчикам.

> Прочитав эту статью, вы узнаете:
>
>
>
>   * какой алгоритм в Linux для резолва хостнеймов;
>   * как переопределить логику определения хостнеймов;
>   * какие функции и библиотеки использует ОС;
>   * какие ловушки существуют при конфигурировании и как их не допускать;
>

>

![](/images/8414b232a7e5573383d559fa6c6e0d80.png)

У операционной системы Linux есть несколько источников для определения адреса по hostname. Весь необходимый функционал для определения находится в [GNU C Library (glibc)](https://www.gnu.org/software/libc/). glibc является по-сути фреймворком и реализовывает множество полезных функций для разработчика, предоставляя свой API для упрощения разработки. Среди прочего, glibc имплементирует [POSIX](http://pubs.opengroup.org/onlinepubs/9699919799/). Такие функции как `open`, `read`, `write`, `malloc`, `printf`, `getaddrinfo`, `dlopen`, `pthread_create`, `crypt`, `login`, `exit` для Linux систем предоставляет именно glibc.

Известные многим утилиты `host`, `dig` и `nslookup` используют glibc, но поставляются отдельно.

> А еще я веду телеграм канал [Об IT без галстуков](https://t.me/noTieInIT) и [блог](http://dmenshikov.com). На канале рассказываю о проблемах менеджмента и как их решать, пишу о принципах мышления при решении бизнес задач, о том как стать эффективным и высокоплачиваемым специалистом.

Теперь, когда у разработчика есть возможность вызвать функцию семейства `getaddrinfo` из glibc для определения адреса, то возникает потребность конфигурировать возвращаемые значения. Например, использовать ли сперва `/etc/hosts` или запрос к DNS-серверу. В glibc подобное конфигурирование производится с помощью схемы под названием _Name Service Switch_ (NSS).

Если объяснять на пальцах, то NSS позволяет задавать базы данных и очередность поиска в этих базах для предоставления сервиса. В нашем случае, сервис — это поиск по hostname, а базой данных может выступать `/etc/hosts` или DNS сервер. Это не единственный сервис настраиваемый посредством NSS, предоставляются сервисы mail алиасов, сервис поиска пользователей и групп. Ознакомится со списком можно [в руководстве](https://www.gnu.org/software/libc/manual/html_node/NSS-Basics.html).

Благодаря NSS можно без пересборки приложений, в рантайме, конфигурировать упомянутые базы данных. Производится конфигурирование в файле `/etc/nsswitch.conf`. Ниже пример конфига из стандартного `/etc/nsswitch.conf` в Centos 7.

```bash
$ grep ^hosts /etc/nsswitch.conf
hosts:      files dns myhostname
```

**files** , **dns** и **myhostname** являются алиасами баз данных для поиска. **files** на большинстве систем подразумевает использование `/etc/hosts`, **dns** база — это DNS-сервер к которому будет осуществляться запрос поиска hostname, а **myhostname** — это самая необычная база, о существовании которой мало кто знает и она не является частью стандартной поставки в glibc. В некоторых дистрибутивах присутствует еще и база **mdns4_minimal**. Ниже по тексту предоставлен разбор этих баз данных.

Базы используются в том порядке в котором они обьявлены в `/etc/nsswitch.conf` и если в текущей базе запись найдена, то происходит выход из цепочки и возврат результата. При отсутствии результата происходит переход к следующей базе в списке. Если ни в одной базе не найден результат, то такой ответ и дается на запрос glibc функции `getaddrinfo`. Поведение перехода к следующей базе и условия такого перехода можно дополнительно конфигурировать, например, при недоступности DNS (не путать с отсутствием записи) завершить цепочку. Понятное и простое объяснение принципа настройки условий для `/etc/nsswitch.conf` даны [в этой статье](http://searchitchannel.techtarget.com/feature/Using-nsswitchconf-to-find-Linux-system-information).

База **files** , а в частности `/etc/hosts`, из коробки в Centos 7 выглядит следующим образом:

```bash
$ cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
```

Можно отметить, что для _localhost_ имеются две записи: IPv4 и IPv6 адрес. Это может сыграть злую шутку и в конце материала я расскажу почему.

База **dns** при определении адреса использует name server указанный в конфиге `/etc/resolv.conf`. Вот пример моего `/etc/resolv.conf` на хост системе:

```bash
$ cat /etc/resolv.conf
# Generated by NetworkManager
nameserver 127.0.0.1
nameserver 192.168.100.1
```

Name server'а используются тоже по цепочке и в порядке их объявления. В моем случае, первым выступает локальный DNS сервер (я использую _dnsmasq_) для задания локальных адресов `.priv` зон. Если находится совпадение, то возвращается адрес из локальной сети. Все остальные запросы отправляются на основной DNS сервер с адресом `192.168.100.1`.

База **myhostname** присутствует в поставке Centos и Ubuntu, но не является частью `glibc`. Не зная этого факта я потратил много времени пытаясь выяснить почему мне возвращаются IPv6 адреса для определения хоста. Он работает следующим образом:

  * При запросе локального хостнейма (того что возвращает команда `hostname`) плагин возвращает все IP адреса публичных интерфейсов (т.е. все кроме loopback), при отсутствии таких интерфейсов возвращается IPv4 адрес `127.0.0.2` и IPv6 адрес `::1`;
  * При запросе хостнейма **localhost** или **localhost.localdomain** возвращает IPv4 адрес `127.0.0.1` и IPv6 адрес `::1`;
  * При запросе хостнейма оканчивающегося на **.localhost** или **.localhost.localdomain** возвращает IPv4 адрес `127.0.0.1` и IPv6 адрес `::1`;

[В мануале](https://www.freedesktop.org/software/systemd/man/nss-myhostname.html) еще пишут про особую логику с обработкой хостнейма __gateway_ , но видимо это какой-то патч, так как с Centos 7 у меня он не завелся.

База **mdns4_minimal** или же **mdns_minimal** требуется для корректной работы Avahi. При необходимости можно обратиться к [документации Arch по Avahi](https://wiki.archlinux.org/index.php/avahi), где коротко и понятно дана информация
по использованию.

Теперь, когда дана информация по базам и принципам их работы стоит отметить отличия в определении адресов в разных инструментах, что приводит к проблемам в рантайме.

Обычно администраторы проверяют хостнейм используя команду _host_. Это некорректно, так host, как и dig, используют только DNS резолвинг, но не используют NSS. Nginx, например, использует функцию [getaddrinfo](http://man7.org/linux/man-pages/man3/getaddrinfo.3.html), а она использует NSS. Это приводит к тому, что вбитый в `/etc/hosts` хостнейм может работать с nginx, но не резолвится иными способами. Куда хуже, когда в `/etc/hosts` вбиты IPv6 адрес для хостнейма, а в настройках DNS возвращается только IPv4 адрес. В этом случае, администратор может проверить что команда host возвращает только IPv4 адрес и успокоится, а потом приложение использующее `getaddrinfo` из glibc запустится и найдет для того же хостнейма IPv4 и IPv6 адрес. Источник ошибок…

Для проверки результатов возвращаемой каждой из баз документация рекомендует воспользоваться утилитой [getent](http://man7.org/linux/man-pages/man1/getent.1.html).

Ниже немного примеров работы с `getent` с включенным IPv6.

В `/etc/nsswitch.conf` содержится следующая цепочка баз:

```text
hosts:      files dns myhostname
```

В `/etc/hosts` содержится следующее инфо

```bash
$ cat /etc/hosts
127.0.0.1    localhost
::1          localhost ip6-localhost ip6-loopback
```

Команда `getent ahosts <hostname>` покажет список всех адресов которые удалось найти. С такими настройками она выведет следующее:

```bash
$ getent ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW
```

Команда позволяет точечно опросить конкретную базу и выяснить что срезолвит база. Рассмотрим для каждой базы возвращаемые значения:

```bash
$ getent -s hosts:files ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW

$ getent -s hosts:dns ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW

$ getent -s hosts:myhostname ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW
```

Если убрать из `/etc/hosts` строки для localhost, то вывод видоизменится:

```bash
$ getent -s hosts:files ahosts localhost

$ getent -s hosts:dns ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW

$ getent -s hosts:myhostname ahosts localhost
::1             STREAM localhost
::1             DGRAM
::1             RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW
```

Теперь база **dns** и **myhostname** возвращает ответы, а база **files** не содержит данных. Для DNS запросов используется неймсервер конфигурируемый в `/etc/resolv.conf` в моем контейнере, например

```bash
$ cat /etc/resolv.conf
nameserver 127.0.0.11
options ndots:0
```

На хост машине установлен _dnsmasq_ который проксирует и кэширует ответы DNS серверов. Ответ от DNS будет зависеть от настроек DNS сервера к которому поступил запрос. [RFC 1912](https://www.ietf.org/rfc/rfc1912.txt) рекомендует в пункте 4.1 сконфигурировать DNS сервера таким образом, чтобы localhost указывал на 127.0.0.1.

> Certain zones should always be present in nameserver configurations:
>
>
>
>
>            primary         localhost               localhost
>            primary         0.0.127.in-addr.arpa    127.0
>            primary         255.in-addr.arpa        255
>            primary         0.in-addr.arpa          0
>
>
>
>
>
>  These are set up to either provide nameservice for "special"
>  addresses, or to help eliminate accidental queries for broadcast or
>  local address to be sent off to the root nameservers. All of these
>  files will contain NS and SOA records just like the other zone files
>  you maintain, the exception being that you can probably make the SOA
>  timers very long, since this data will never change.
>
>  The "localhost" address is a "special" address which always refers to
>  the local host. It should contain the following line:
>
>
>
>
>       localhost.      IN      A       127.0.0.1
>
>
>
>
>

В моем случае, dnsmasq из коробки содержит записи для localhost, как и рекомендует RFC.

```bash
$ dig +noall +answer localhost ANY @127.0.0.1
localhost.      0   IN  A       127.0.0.1
localhost.      0   IN  AAAA    ::1
```

Отключается это либо удалением записей из `/etc/hosts` на самом DNS сервере, либо же включением опции `no-hosts` в `/etc/dnsmasq.conf`.

После включения опции getent для базы **myhostname** вернет непустой результат, но как и отмечалось выше, с включенным **myhostname** будет возвращаться IPv4 и IPv6 адрес. На системах со статическими IP адресами можно смело выключить **myhostname** плагин и конфигурировать локальные хосты с использованием `/etc/hosts`. Альтернативный вариант — это отключение IPv6.

Статус IPv6 на сервере можно получить из параметров ядра. Значение 0 возвращается при включенном IPv6, а 1 при выключенном.

```bash
$ sysctl net.ipv6.conf.all.disable_ipv6 net.ipv6.conf.default.disable_ipv6
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
```

В выводе _ifconfig_ интерфейсы слушающие IPv6 содержат строчку _inet6_. Ниже пример вывода с выключенным и включенным IPv6 соответственно:

```bash
# diabled
$ ifconfig -a
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.101.5  netmask 255.255.255.0  broadcast 0.0.0.0
        ether 02:42:c0:a8:65:05  txqueuelen 0  (Ethernet)
        RX packets 15789549  bytes 2553533549 (2.3 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 9783999  bytes 1318627420 (1.2 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1  (Local Loopback)
        RX packets 606047  bytes 67810892 (64.6 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 606047  bytes 67810892 (64.6 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

# enabled
$ ifconfig -a
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.101.5  netmask 255.255.255.0  broadcast 0.0.0.0
        inet6 fe80::42:c0ff:fea8:6505  prefixlen 64  scopeid 0x20<link>
        ether 02:42:c0:a8:65:05  txqueuelen 0  (Ethernet)
        RX packets 15787641  bytes 2553216408 (2.3 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 9782965  bytes 1318487919 (1.2 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1  (Local Loopback)
        RX packets 605949  bytes 67799887 (64.6 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 605949  bytes 67799887 (64.6 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Выключить IPv6 можно вызовом

```bash
$ sysctl -w net.ipv6.conf.all.disable_ipv6=1
$ sysctl -w net.ipv6.conf.default.disable_ipv6=1
```

Что изменится после выключения? Я откатил все конфиги на стандартные: в `/etc/hosts` присутствует localhost с адресами IPv4 и IPv6, в dnsmasq выключена опция `no-hosts`. Отключил IPv6 командами выше и вывод getent стал следующим:

```bash
$ getent -s hosts:files ahosts localhost
127.0.0.1       STREAM localhost
127.0.0.1       DGRAM
127.0.0.1       RAW
127.0.0.1       STREAM
127.0.0.1       DGRAM
127.0.0.1       RAW

$ getent -s hosts:dns ahosts localhost
127.0.0.1       STREAM localhost
127.0.0.1       DGRAM
127.0.0.1       RAW

$ getent -s hosts:myhostname ahosts localhost
127.0.0.1       STREAM localhost
127.0.0.1       DGRAM
127.0.0.1       RAW
```

Воу, в первом выводе у нас дублируется адрес 127.0.0.1. Чтобы разобраться почему так происходит стоит обратиться к исходному коду glibc и к коду утилиты getent. Ниже кусок кода утилиты getent.

```c
/* This is for hosts, but using getaddrinfo */
static int
ahosts_keys_int (int af, int xflags, int number, char *key[])
{
  // ...
  hint.ai_flags = (AI_V4MAPPED | AI_ADDRCONFIG | AI_CANONNAME
           | idn_flags | xflags);
  hint.ai_family = af;
```

```c
  for (i = 0; i < number; ++i)
    {
      struct addrinfo *res;
```

```c
      if (getaddrinfo (key[i], NULL, &hint, &res) != 0)
    result = 2;
      else
    {
      struct addrinfo *runp = res;
```

```c
      while (runp != NULL)
        {
          // printf goes here
        }
```

```text
      freeaddrinfo (res);
    }
    }

  return result;
```

Флаг [AI_V4MAPPED функции getaddrinfo](http://man7.org/linux/man-pages/man3/getaddrinfo.3.html) производит маппинг IPv6 адресов на IPv4 если не были найдены IPv6 адреса в результате опроса базы. Флаг AI_ADDRCONFIG вынудит getaddrinfo проверить наличие IPv6/IPv4 адресов сконфигурированных в системе и в случае отсутствия хотя бы одного IPv6/IPv4 адреса не будет возвращаться IPv6/IPv4 независимо от того что ответит конкретная база.

Поскольку у getent включены оба флага, а в `/etc/hosts` присуствуетя для localhost адреса `127.0.0.1` и `::1`, то getaddrinfo получит из NSS базы **hosts** (в примере выше мы обсуждали именно эту базу), адреса `127.0.0.1` и `::1`, затем не обнаружив ни одного IPv6 адреса в системе (выключены параметрами ядра) и произведет маппинг `::1` -> `127.0.0.1`.

Чтобы лучше понять эту концепцию, приведу примеры с выводом getaddrinfo на той же системе, с разными настройками _ai_flags_ и _ai_family_. В `/etc/hosts` включены для localhost IPv4 и IPv6 адреса.
Исходный код можно найти [на моем github](https://gist.github.com/WoZ/70f90bc053d2718d6311682525430b72).

```text
# ./getaddrinfo localhost
IP addresses for localhost:

[AF_INET] AI_V4MAPPED
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_INET] AI_V4MAPPED AI_ALL
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_INET] AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_INET] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_INET] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
--------------

[AF_INET6] AI_V4MAPPED
  IPv6: ::1
[AF_INET6] AI_V4MAPPED AI_ALL
  IPv6: ::ffff:127.0.0.1
  IPv6: ::ffff:127.0.0.1
  IPv6: ::1
[AF_INET6] AI_ADDRCONFIG
getaddrinfo: Name or service not known
[AF_INET6] AI_V4MAPPED AI_ADDRCONFIG
getaddrinfo: Name or service not known
[AF_INET6] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
getaddrinfo: Name or service not known
--------------

[AF_UNSPEC] AI_V4MAPPED
  IPv4: 127.0.0.1
  IPv6: ::1
[AF_UNSPEC] AI_V4MAPPED AI_ALL
  IPv4: 127.0.0.1
  IPv6: ::1
[AF_UNSPEC] AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_UNSPEC] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
[AF_UNSPEC] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 127.0.0.1
  IPv4: 127.0.0.1
--------------
```

Из вывода видно, что с _ai _family_ равным _AI _UNSPEC_ (возвращать и IPv4, и IPv6) и без AI_ADDRCONFIG флага `getaddrinfo` возвращает два адреса, IPv4 и IPv6, что многие администраторы не ожидают увидеть. Это происходит независимо от того выключен ли IPv6 в параметрах ядра. Если в `/etc/hosts` убрать адрес `::1`, то из вывода `getaddrinfo` (с флагом `AF_UNSPEC`) вовсе исчезнут IPv6 адреса.

С включенным IPv6 и наличием `::1` в `/etc/hosts` будет возвращаться IPv4 и IPv6. Для предотвращения возврата адреса IPv6 требуется закомментировать IPv6 адрес в `/etc/hosts`. Если адреса будут найдены в `/etc/hosts`, то в **dns** и **myhostname** базу glibc не полезет.

Осталось проверить как ведет себя `getaddrinfo` для **dns** базы. Для этого оставлю в `/etc/nsswitch.conf` для **hosts** только **dns** базу и порезолвлю google.com. Вывод ниже с включенным IPv6.

```bash
$ sysctl -w net.ipv6.conf.default.disable_ipv6=0
$ sysctl -w net.ipv6.conf.all.disable_ipv6=0

$ ./getaddrinfo google.com
IP addresses for google.com:

[AF_INET] AI_V4MAPPED
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ALL
  IPv4: 216.58.215.78
[AF_INET] AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 216.58.215.78
--------------

[AF_INET6] AI_V4MAPPED
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_V4MAPPED AI_ALL
  IPv6: ::ffff:216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_ADDRCONFIG
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_V4MAPPED AI_ADDRCONFIG
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv6: ::ffff:216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
--------------

[AF_UNSPEC] AI_V4MAPPED
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_V4MAPPED AI_ALL
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_ADDRCONFIG
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
--------------
```

А вот вывод с выключенным IPv6:

```bash
$ sysctl -w net.ipv6.conf.all.disable_ipv6=1
$ sysctl -w net.ipv6.conf.default.disable_ipv6=1

$ ./getaddrinfo google.com
IP addresses for google.com:

[AF_INET] AI_V4MAPPED
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ALL
  IPv4: 216.58.215.78
[AF_INET] AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_INET] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 216.58.215.78
--------------

[AF_INET6] AI_V4MAPPED
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_V4MAPPED AI_ALL
  IPv6: ::ffff:216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_INET6] AI_ADDRCONFIG
getaddrinfo: Name or service not known
[AF_INET6] AI_V4MAPPED AI_ADDRCONFIG
getaddrinfo: Name or service not known
[AF_INET6] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
getaddrinfo: Name or service not known
--------------

[AF_UNSPEC] AI_V4MAPPED
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_V4MAPPED AI_ALL
  IPv4: 216.58.215.78
  IPv6: 2a00:1450:401b:806::200e
[AF_UNSPEC] AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_UNSPEC] AI_V4MAPPED AI_ADDRCONFIG
  IPv4: 216.58.215.78
[AF_UNSPEC] AI_V4MAPPED AI_ALL AI_ADDRCONFIG
  IPv4: 216.58.215.78
--------------
```

Как видно, ситуация с AI_ADDRCONFIG очень похожа.

Напоследок приведу пример как не учитывая все вышесказанное вляпаться в проблемы. IPv6 включен, `/etc/nsswitch.conf` стандартный.

```bash
$ cat /etc/hosts
127.0.0.1   localhost
::1         localhost ip6-localhost ip6-loopback

$ grep hosts /etc/nsswitch.conf
hosts:      files dns myhostname

$ cat /etc/resolv.conf
nameserver 127.0.0.11
options ndots:0

$ sysctl net.ipv6.conf.all.disable_ipv6 net.ipv6.conf.default.disable_ipv6
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
```

Что вернет `host localhost` или `dig ANY localhost`? Что вернет `getaddrinfo`, например, с флагами как у nginx?

```bash
$ dig +noall +answer ANY localhost @127.0.0.11
localhost.      0   IN   A    127.0.0.1

$ host localhost
localhost has address 127.0.0.1

$ ./getaddrinfo localhost
IP addresses for localhost:

[AF_UNSPEC] AI_ADDRCONFIG
  IPv6: ::1
  IPv4: 127.0.0.1
```

nginx будет пытаться подключаться к двум адресам: `127.0.0.1` и `::1`, а приложение может и не ожидать такого. Источник для ошибок.

![](/images/0ee8705bbbc2606399213f65670bbb9d.png)

Какой можно сделать вывод из всего написанного?

  1. Если вы разрабатываете приложение работающее с сетью, то учитывайте, что IPv6 может быть отключен;
  2. При настройке сервера учитывайте наличие NSS и очередности проверок, используйте getent или мой код для проверки;
  3. Если неизвестно как работает приложение, то при наличии исходных кодов можно посмотреть с какими флагами резолвятся
адреса и сверить с настройками системы;
  4. Если исходных кодов нет, то можно по поведению в выводе strace сделать предположение об используемых флагах.

P.S. Подписывайся на мой канал [Об IT без галстуков](https://t.me/noTieInIT). Я рассказываю о фундаментальных проблемах в IT бизнесе и способах их решения, о запросе повышений и о построении карьеры до управленца или собственного бизнеса.

**********

[Linux](/tags/linux.md)
[dns](/tags/dns.md)
