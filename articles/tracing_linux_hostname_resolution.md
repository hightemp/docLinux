# Трассировка разрешения имён хостов в Linux

Источник: [Tracing Linux Hostname Resolution](https://www.kickflop.net/blog/2011/01/02/tracing-linux-hostname-resolution/)

Jeff Blaine · 2 января 2011

_Этот пост — «живой документ». Обновления, появившиеся после изначальной даты публикации, помечены прямо в тексте._

_Обновление от 11.01.2011: почти вся эта статья теперь неактуальна, так как выяснилось, что разработчики GNU libc считают getent (основа всего написанного ниже) всего лишь инструментом отладки. Соответственно, он делает нестандартные вещи. Я предложил отметить это на man-странице. Итак, вот она …_

Давайте в воскресенье вечером разберём разрешение имён хостов на машине с RHEL 5.5. Вдохновение пришло две недели назад от прочтения статьи [Down the 'ls' Rabbit Hole](http://sysadvent.blogspot.com/2010/12/day-15-down-ls-rabbit-hole.html). Подозреваю, что любой другой современный дистрибутив Linux даст почти идентичные результаты.

Краткое резюме:

1. Прочитать /etc/resolv.conf
2. Попробовать использовать nscd
3. Попробовать использовать nscd снова
4. Прочитать /etc/nsswitch.conf
5. Загрузить libnss_files.so
6. Прочитать /etc/host.conf
7. Попробовать найти IPv6-адрес в /etc/hosts
8. Загрузить libnss_dns.so
9. Загрузить libresolv.so
10. Выполнить DNS-запрос IPv6 'AAAA'
11. Попробовать найти IPv4-адрес в /etc/hosts
12. Выполнить DNS-запрос IPv4 'A'

Читайте дальше полную трассировку с комментариями.

```text
strace -f getent hosts www.puppetlabs.com
...
open("/etc/resolv.conf", O_RDONLY)      = 3
...
close(3)                                = 0
```

Если посмотреть на исходники [GNU libc](http://ftp.gnu.org/gnu/glibc/) 2.5 (именно она установлена на этой машине), видно, что /etc/resolv.conf загружается в resolv/res_init.c, и там даётся такое объяснение:

```c
/*
 * Resolver state default settings.
 */

/*
 * Set up default settings.  If the configuration file exist, the values
 * there will have precedence.  Otherwise, the server address is set to
 * INADDR_ANY and the default domain name comes from the gethostname().
 *
 * An interrim version of this code (BIND 4.9, pre-4.4BSD) used 127.0.0.1
 * rather than INADDR_ANY ("0.0.0.0") as the default name server address
 * since it was noted that INADDR_ANY actually meant ``the first interface
 * you "ifconfig"'d at boot time'' and if this was a SLIP or PPP interface,
 * it had to be "up" in order for you to reach your own name server.  It
 * was later decided that since the recommended practice is to always
 * install local static routes through 127.0.0.1 for all your network
 * interfaces, that we could solve this problem without a code change.
 *
 * The configuration file should always be used, since it is the only way
 * to specify a default domain.  If you are running a server on your local
 * machine, you should say "nameserver 0.0.0.0" or "nameserver 127.0.0.1"
 * in the configuration file.
 *
 * Return 0 if completes successfully, -1 on error
 */
```

Ладно, допустим. Идём дальше.

```text
...
socket(PF_FILE, SOCK_STREAM, 0)         = 3
fcntl(3, F_SETFL, O_RDWR|O_NONBLOCK)    = 0
connect(3, {sa_family=AF_FILE, path="/var/run/nscd/socket"...}, 110) = -1 ENOENT
(No such file or directory)
close(3)                                = 0
socket(PF_FILE, SOCK_STREAM, 0)         = 3
fcntl(3, F_SETFL, O_RDWR|O_NONBLOCK)    = 0
connect(3, {sa_family=AF_FILE, path="/var/run/nscd/socket"...}, 110) = -1 ENOENT
(No such file or directory)
close(3)                                = 0
```

Почему ты проверил nscd дважды?

GNU libc nscd/nscd_helper.c — единственное место с вызовом connect(), ссылающимся на /var/run/nscd/socket (он же _PATH_NSCDSOCKET, как определено в nscd/nscd-client.h). connect() находится в open_socket(), на который ссылаются в двух местах:

Первое:

```c
/* Try to get a file descriptor for the shared memory segment
   containing the database.  */
static struct mapped_database *
get_mapping (request_type type, const char *key,
             struct mapped_database **mappedp)
```

Второе:

```c
/* Create a socket connected to a name. */
int
__nscd_open_socket (const char *key, size_t keylen, request_type type,
                    void *response, size_t responselen)
```

Тут я взялся попытаться собрать код GNU libc, на который ссылался. Я думал собрать его с отладочными символами и запустить getent снова под gdb. Сборка с CFLAGS=-g выдала ошибку о том, что он _обязан_ собираться с оптимизацией. С этим не вышло, но я хотя бы добавил несколько вызовов syslog(). Во-первых, обе попытки connect() к nscd-сокету выше действительно идут из обеих упомянутых функций.

_Обновление от 11.01.2011: это показывает мой недостаток знаний gdb. Чтобы увидеть то, что я хотел, не нужно собирать библиотеку с отладочными символами. Комментатор Dave W. ниже показывает это на своих трассировках._

```text
Jan  3 03:57:33 new-host-2 getent: get_mapping() trying to open nscd socket with
open_socket()
Jan  3 03:57:33 new-host-2 getent: __nscd_open_socket() trying to open nscd socket
with open_socket() with open_socket()
```

Корректно ли это поведение? Можно ли лучше? Понятия не имею. Я лишь довожу это до такого уровня, но идеальным это не кажется.

```text
...
open("/etc/nsswitch.conf", O_RDONLY)    = 3
...
close(3)                                = 0
```

Вот мы наконец куда-то продвинулись. По крайней мере, на этом этапе мы читаем правильный конфигурационный файл.

Это генерируется из GNU libc nss/nsswitch.c

```c
int
__nss_database_lookup (const char *database, const char *alternate_name,
                       const char *defconfig, service_user **ni)
{
...
    service_table = nss_parse_file (_PATH_NSSWITCH_CONF);
```

Ладно, дальше.

```text
open("/lib64/libnss_files.so.2", O_RDONLY) = 3
...
close(3)                                = 0
```

Это из-за того, что "files" идёт первым в /etc/nsswitch.conf. Нормально.

```text
...
open("/etc/host.conf", O_RDONLY)        = 3
...
close(3)                                = 0
```

Какого чёрта? Ты уже нашёл валидный /etc/nsswitch.conf. Зачем запрашивать этот глупый старый легаси-файл?

nss/getXXbyYY_r.c вызывает это чтение /etc/host.conf

```c
#ifdef NEED__RES_HCONF
          if (!_res_hconf.initialized)
            _res_hconf_init ();
#endif /* need _res_hconf */
```

Выясняется, что это жёстко зашито в код и никак не управляется и не переопределяется через configure.

```text
[jblaine@new-host-2 glibc-2.5]$ grep "#define NEED__RES_HCONF" */*
inet/gethstbyad_r.c:#define NEED__RES_HCONF     1
inet/gethstbynm2_r.c:#define NEED__RES_HCONF    1
inet/gethstbynm_r.c:#define NEED__RES_HCONF     1
```

**???** — не стесняйтесь прокомментировать это ниже. Я не понимаю нужды в этом сегодня, когда у нас есть /etc/nsswitch.conf.

```text
...
open("/etc/hosts", O_RDONLY)            = 3
...
close(3)                                = 0
```

Наконец-то логично — по крайней мере, если это результат следования тому, что сказано в нашем /etc/nsswitch.conf ("files dns").

_Обновление от 11.01.2011: как ни странно, это _первое_ открытие /etc/hosts происходит из-за попытки разрешить www.puppetlabs.com через IPv6-адрес._

```text
open("/lib64/libnss_dns.so.2", O_RDONLY) = 3
...
close(3)                                = 0
...
open("/lib64/libresolv.so.2", O_RDONLY) = 3
...
close(3)                                = 0
```

Ладно.

```text
socket(PF_INET, SOCK_DGRAM, IPPROTO_IP) = 3
connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("192.168.1.1")}, 28) = 0
...
sendto(3, "uw\1\0\0\1\0\0\0\0\0\0\3www\npuppetlabs\3com\0"..., 36, MSG_NOSIGNAL, NULL, 0) = 36
...
recvfrom(3, "uw\201\200\0\1\0\1\0\1\0\0\3www\npuppetlabs\3com\0"..., 1024, 0,
{sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("192.168.1.1")}, [16]) = 120
close(3)                                = 0
```

DNS-трафик, наконец-то.

_Обновление от 10.01.2011: вернувшись вечером к этому маленькому упражнению с Wireshark, я обнаружил, что этот DNS-запрос — про IPv6-запись "AAAA". Комментатор Dave W. подтвердил это ниже. Меня всё ещё удивляет, что сначала пробуется IPv6._

```text
open("/etc/hosts", O_RDONLY)            = 3
...
close(3)                                = 0
```

Почему? Что сделало это и какова причина?

_Обновление от 11.01.2011: это попытка поиска адреса как IPv4. Отсутствие ожидаемого вывода syslog() ниже, впрочем, остаётся слегка загадочным._

Открытие /etc/hosts происходит в 2 функциях GNU libc:

Первая:

```c
void
_sethtent(f)
        int f;
{
        if (!hostf)
                hostf = fopen(_PATH_HOSTS, "r" );
        else
                rewind(hostf);
        stayopen = f;
}
```

Вторая:

```c
struct hostent *
_gethtent()
{
...
        if (!hostf && !(hostf = fopen(_PATH_HOSTS, "r" ))) {
                __set_h_errno (NETDB_INTERNAL);
                return (NULL);
        }
...
```

Предположим, наша «проблема» — _gethtent(). На него ссылаются из 3 мест:

Первое:

```c
struct hostent *
_gethtbyname2(name, af)
        const char *name;
        int af;
```

Второе:

```c
struct hostent *
_gethtbyaddr(addr, len, af)
        const char *addr;
        size_t len;
        int af;
```

Третье:

```c
struct hostent *
gethostent()
```

Как ни странно, при множестве вызовов syslog() в _sethtent() и _gethtent() вокруг мест, где происходит fopen() /etc/hosts, я не могу добиться, чтобы они срабатывали. Это странное открытие /etc/hosts остаётся загадкой.

Идём дальше.

```text
...
socket(PF_INET, SOCK_DGRAM, IPPROTO_IP) = 3
connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("192.168.1.1")}, 28) = 0
...
sendto(3, "\256\261\1\0\0\1\0\0\0\0\0\0\3www\npuppetlabs\3com\0"..., 36, MSG_NOSIGNAL, NULL, 0) = 36
...
recvfrom(3, "\256\261\201\200\0\1\0\2\0\0\0\0\3www\npuppetlabs\3com\0"..., 1024, 0,
{sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("192.168.1.1")}, [16]) = 66
close(3)                                = 0
...
write(1, "74.207.250.144  puppetlabs.com w"..., 5074.207.250.144  puppetlabs.com
www.puppetlabs.com) = 50
exit_group(0)                           = ?
```

Ещё один DNS-запрос перед выводом на экран и завершением getent. **Почему?**

_Обновление от 11.01.2011: это наконец IPv4-запрос записи "A"._

Не стесняйтесь подключаться к обсуждению.

## Комментарии

**David W** · 10 января 2011:

Jeff: наткнулся на твой блог, отлаживая твою маленькую головоломку ;-) Надеюсь, ты не против, если я опубликую ответ:

при первом fopen /etc/hosts получаем такую трассировку:

```text
#4 0x00007f3e3e901b07 in gethostbyname2 (name=0x7fff62c898cd "www.google.com", af=0xa)
at ../nss/getXXbyYY.c:117
```

_обрати внимание на af=0xa_

бэктрейс второго fopen:

```text
#4 0x00007f3e3e901b07 in gethostbyname2 (name=0x7fff62c898cd "www.google.com", af=0x2)
at ../nss/getXXbyYY.c:117
```

_обрати внимание на af=0x2_

Теперь проверяем:

```text
$ grep -Ri AF_INET *
bits/socket.h:#define AF_INET PF_INET
bits/socket.h:#define AF_INET6 PF_INET6
```

и продолжаем:

```text
bits/socket.h:#define PF_INET 2 /* IP protocol family. */
bits/socket.h:#define PF_INET6 10 /* IP version 6. */
```

что соответствует 0x2 и 0xa в бэктрейсах.

**JB** (автор) · 11 января 2011:

Спасибо, Dave.

Почти вся эта статья теперь неактуальна, так как выяснилось, что разработчики GNU libc считают getent (основа всего написанного ниже) всего лишь инструментом отладки. Соответственно, он делает нестандартные вещи. Я предложил отметить это на man-странице.

**[Armin C](https://www.ekoru.org)** · 8 июня 2022:

Привет, Jeff,

спасибо, что оставил это как каркас, даже если getent за эти годы изменился (почти уверен, что это всё ещё актуально при настройке и отладке LDAP и NIS).

Хотел упомянуть об использовании /etc/hosts при таких запросах… Возможно, ты уже это выяснил, но причина в том, что порядок разрешения имён управляется через /etc/nsswitch.conf.

Вот примерный фрагмент (неизменённый из стокового файла):

```text
#####
#hosts: db files nisplus nis dns
hosts: files dns myhostname
#####
```

Первая строка — стоковый пример, показывающий доступные варианты для строки hosts (формат во всём остальном файле такой же, как ты увидишь).

Вторая строка говорит, что первым источником для поиска любого имени хоста будет файл (в данном случае /etc/hosts). Если /etc/hosts не разрешает имя хоста, будет предпринята попытка обратиться к настроенному DNS-серверу (статически или через DHCP), и в конце проверяется собственное имя хоста системы (по моему опыту, этот способ упоминается редко).

Если хочешь, чтобы твоя система вообще не проверяла /etc/hosts (чего я лично избегал бы), можно удалить 'files' из этой строки ИЛИ просто поставить 'dns' перед 'files':

```text
#####
hosts: dns files myhostname
#####
```

Надеюсь, это кому-нибудь где-нибудь когда-нибудь поможет :)

С уважением,
Armin C

**********

[linux](/tags/linux.md)
[dns](/tags/dns.md)
[networking](/tags/networking.md)