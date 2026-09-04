# Анатомия DNS-запроса в Linux. Часть I

Источник: [Anatomy of a Linux DNS Lookup – Part I](https://zwischenzugs.com/2018/06/08/anatomy-of-a-linux-dns-lookup-part-i/)

Автор: [imiell](https://zwischenzugs.com/author/imiell/) · 8 июня 2018

Поскольку я [много](https://zwischenzugs.com/2017/10/31/a-complete-chef-infrastructure-on-your-laptop/) [работаю](https://zwischenzugs.com/2017/03/04/a-complete-openshift-cluster-on-vagrant-step-by-step/) [с](https://zwischenzugs.com/2017/03/04/migrating-an-openshift-etcd-cluster/) [кластеризованными](https://zwischenzugs.com/2017/03/04/1-minute-multi-node-vm-setup/) [виртуальными](https://zwischenzugs.com/2017/03/18/clustered-vm-testing-how-to/) [машинами](https://zwischenzugs.com/2017/10/27/ten-things-i-wish-id-known-before-using-vagrant/), я в итоге провёл много времени, пытаясь понять, как работают [DNS-запросы](https://zwischenzugs.com/2017/10/21/openshift-3-6-dns-in-pictures/). Какое-то время я применял «исправления» своих проблем со StackOverflow, не особо понимая, почему они работают (или не работают).

В конце концов меня это достало, и я решил разобраться, как всё это устроено. Я не смог найти полного руководства по этой теме где-либо в интернете, а разговоры с коллегами показали, что они тоже не знают такового (и в деталях не представляют, что происходит).

Поэтому я пишу это руководство сам.

Оказалось, что во фразе «Linux делает DNS-запрос» скрыто весьма немало…

**********

**Другие посты серии:**

**[Anatomy of a Linux DNS Lookup – Part II](http://zwischenzugs.com/2018/06/18/anatomy-of-a-linux-dns-lookup-part-ii/)**

**[Anatomy of a Linux DNS Lookup – Part III](http://zwischenzugs.com/2018/07/06/anatomy-of-a-linux-dns-lookup-part-iii/)**

**[Anatomy of a Linux DNS Lookup – Part IV](http://zwischenzugs.com/2018/08/06/anatomy-of-a-linux-dns-lookup-part-iv/)**

**[Anatomy of a Linux DNS Lookup – Part V – Two Debug Nightmares](http://zwischenzugs.com/2018/09/13/anatomy-of-a-linux-dns-lookup-part-v-two-debug-nightmares/)**

**********

![linux-dns-0](https://ianmiell.com/wp-content/uploads/2018/06/linux-dns-0.png)

_**«Насколько же это может быть сложно?»**_

**********

**Эти посты призваны разобрать, как программа решает, каким образом получить IP-адрес на Linux-хосте, и какие компоненты могут быть в этом задействованы.** Без понимания того, как эти части стыкуются вместе, отладка и исправление проблем с (например) `dnsmasq`, `vagrant landrush` или `resolvconf` может быть абсолютно сбивающей с толку.

Это также ценная иллюстрация того, как нечто настолько простое со временем может стать таким сложным. Пытаясь понять, что происходит, я пока изучил более десятка разных технологий и их «археологию».

Я даже написал [код автоматизации](https://github.com/ianmiell/shutit-linux-dns/blob/master/linux_dns.py), чтобы экспериментировать в виртуальной машине. Вклад/исправления приветствуются.

**Обратите внимание: это не пост о том, «как работает DNS».** Речь обо всём вплоть до вызова реального DNS-сервера, настроенного на linux-хосте (в предположении, что он вообще вызывает DNS-сервер — как вы увидите, это не обязательно), и о том, как он может выяснить, к какому серверу идти, или как получить IP каким-то другим способом.

**********

# 1) Не существует вызова «DNS Lookup»

**********

![linux-dns-1](https://ianmiell.com/wp-content/uploads/2018/06/linux-dns-1.png)

**_Так это НЕ работает_**

**********

**Первое, что нужно усвоить: в Linux нет единственного способа выполнить DNS-запрос.** Это не системный вызов ядра с чистым интерфейсом.

Однако есть стандартный вызов библиотеки C, который используют многие программы: `[getaddrinfo](http://man7.org/linux/man-pages/man3/getaddrinfo.3.html)`. Но не все приложения его используют!

Возьмём две простые стандартные программы: `ping` и `host`:

```console
root@linuxdns1:~# ping -c1 bbc.co.uk | head -1
PING bbc.co.uk (151.101.192.81) 56(84) bytes of data.
```

```console
root@linuxdns1:~# host bbc.co.uk | head -1
bbc.co.uk has address 151.101.192.81
```

Обе получают одинаковый результат, значит, они делают одно и то же, верно?

Неверно.

Вот файлы, которые `ping` просматривает на моём хосте и которые относятся к DNS:

```console
root@linuxdns1:~# strace -e trace=open -f ping -c1 google.com
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
open("/lib/x86_64-linux-gnu/libcap.so.2", O_RDONLY|O_CLOEXEC) = 3
open("/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
open("/etc/resolv.conf", O_RDONLY|O_CLOEXEC) = 4
open("/etc/resolv.conf", O_RDONLY|O_CLOEXEC) = 4
open("/etc/nsswitch.conf", O_RDONLY|O_CLOEXEC) = 4
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 4
open("/lib/x86_64-linux-gnu/libnss_files.so.2", O_RDONLY|O_CLOEXEC) = 4
open("/etc/host.conf", O_RDONLY|O_CLOEXEC) = 4
open("/etc/hosts", O_RDONLY|O_CLOEXEC)  = 4
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 4
open("/lib/x86_64-linux-gnu/libnss_dns.so.2", O_RDONLY|O_CLOEXEC) = 4
open("/lib/x86_64-linux-gnu/libresolv.so.2", O_RDONLY|O_CLOEXEC) = 4
PING google.com (216.58.204.46) 56(84) bytes of data.
open("/etc/hosts", O_RDONLY|O_CLOEXEC)  = 4
64 bytes from lhr25s12-in-f14.1e100.net (216.58.204.46): icmp_seq=1 ttl=63 time=13.0 ms
[...]
```

и то же для `host`:

```console
$ strace -e trace=open -f host google.com
[...]
[pid  9869] open("/usr/share/locale/en_US.UTF-8/LC_MESSAGES/libdst.cat", O_RDONLY) = -1 ENOENT (No such file or directory)
[pid  9869] open("/usr/share/locale/en/libdst.cat", O_RDONLY) = -1 ENOENT (No such file or directory)
[pid  9869] open("/usr/share/locale/en/LC_MESSAGES/libdst.cat", O_RDONLY) = -1 ENOENT (No such file or directory)
[pid  9869] open("/usr/lib/ssl/openssl.cnf", O_RDONLY) = 6
[pid  9869] open("/usr/lib/x86_64-linux-gnu/openssl-1.0.0/engines/libgost.so", O_RDONLY|O_CLOEXEC) = 6[pid  9869] open("/etc/resolv.conf", O_RDONLY) = 6
google.com has address 216.58.204.46
[...]
```

Видно, что мой `ping` смотрит в `nsswitch.conf`, а `host` — нет. И оба смотрят в `/etc/resolv.conf`.

Мы разберём эти два файла `.conf` по очереди.

**********

# 2) NSSwitch и `/etc/nsswitch.conf`

Мы установили, что приложения могут делать что хотят, когда решают, к какому DNS-серверу идти. Многие приложения (как `ping` выше) могут обращаться (в зависимости от реализации **(*)**) к NSSwitch через его конфигурационный файл `/etc/nsswitch.conf`.

###### (*) Существует удивительная степень различий между реализациями ping. Это та кроличья нора, в которую мне _не_ хотелось проваливаться.

NSSwitch — это не только для DNS-запросов. Он также используется, например, для паролей и информации о поиске пользователей.

NSSwitch изначально был создан как часть ОС Solaris, чтобы позволить приложениям не хардкодить, в каком файле или службе они ищут эти вещи, а делегировать их в другое конфигурируемое централизованное место, о котором им не нужно заботиться.

Вот мой `nsswitch.conf`:

```text
passwd:         compat
group:          compat
shadow:         compat
gshadow:        files
hosts: files dns myhostname
networks:       files
protocols:      db files
services:       db files
ethers:         db files
rpc:            db files
netgroup:       nis
```

Нас интересует строка 'hosts'. Мы показали, что `ping` зависит от `nsswitch.conf`, так что давайте пошевелим его и посмотрим, как можно помешать `ping`.

* ### Установить в `nsswitch.conf` только 'files'

Если установить строку `hosts` в `nsswitch.conf` в «только» `files`:

`hosts: files`

то `ping` по google.com теперь завершится ошибкой:

```console
$ ping -c1 google.com
ping: unknown host google.com
```

но `localhost` всё ещё работает:

```console
$ ping -c1 localhost
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.039 ms
```

а использование `host` по-прежнему отлично работает:

```console
$ host google.com
google.com has address 216.58.206.110
```

поскольку, как мы видели, ему всё равно на `nsswitch.conf`

* ### Установить в `nsswitch.conf` только 'dns'

Если установить строку `hosts` в `nsswitch.conf` в «только» dns:

`hosts: dns`

то `ping` по google.com снова заработает:

```console
$ ping -c1 google.com
PING google.com (216.58.198.174) 56(84) bytes of data.
64 bytes from lhr25s10-in-f174.1e100.net (216.58.198.174): icmp_seq=1 ttl=63 time=8.01 ms
```

Но `localhost` в этот раз не найден:

```console
$ ping -c1 localhost
ping: unknown host localhost
```

Вот диаграмма того, что происходит с NSSwitch по умолчанию в отношении поиска `hosts`:

**********

![linux-dns-2 (1)](https://ianmiell.com/wp-content/uploads/2018/06/linux-dns-2-11.png)

_**Моя конфигурация '`hosts:`' по умолчанию в `nsswitch.conf`**_

**********

## 3) `/etc/resolv.conf`

Теперь мы видели, что и `host`, и `ping` смотрят в файл `/etc/resolv.conf`.

Вот как выглядит мой `/etc/resolv.conf`:

```text
# Dynamic resolv.conf(5) file for glibc resolver(3) generated by resolvconf(8)
#     DO NOT EDIT THIS FILE BY HAND -- YOUR CHANGES WILL BE OVERWRITTEN
nameserver 10.0.2.3
```

Игнорируйте первые две строки — мы вернёмся к ним позже (они значимы, но вы ещё не готовы к этому клубку).

Строки `nameserver` указывают DNS-серверы, в которых искать хост.

Если закомментировать эту строку:

```text
#nameserver 10.0.2.3
```

и запустить:

```console
$ ping -c1 google.com
ping: unknown host google.com
```

команда завершится ошибкой, потому что нет nameserver, к которому идти (*).

###### * Ещё одна кроличья нора: `host`, судя по всему, откатывается к 127.0.0.1:53, если nameserver не указан.

Этот файл принимает и другие опции. Например, если добавить эту строку в файл `resolv.conf`:

```text
search com
```

и затем выполнить `ping google` (так, без домена):

```console
$ ping google
PING google.com (216.58.204.14) 56(84) bytes of data.
```

он автоматически попробует за вас домен `.com`.

## Конец Части I

Это конец Части I. Следующая часть начнёт с рассмотрения того, как этот resolv.conf создаётся и обновляется.

Вот что вы узнали выше:

* В ОС нет вызова «DNS lookup»
* Разные программы выясняют IP адреса по-разному
  * Например, `ping` использует `nsswitch`, который в свою очередь использует (или может использовать) `/etc/hosts`, `/etc/resolv.conf` и собственное имя хоста, чтобы получить результат
* `/etc/resolv.conf` помогает решить:
  * какие адреса вызываются
  * какой DNS-сервер запрашивать

Если вам показалось это сложным, пристегните ремни…

**********

[dns](/tags/dns.md)
[networking](/tags/networking.md)
[linux](/tags/linux.md)