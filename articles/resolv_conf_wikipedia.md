# resolv.conf

Источник: [resolv.conf](https://en.wikipedia.org/wiki/Resolv.conf)

Из Википедии, свободной энциклопедии

**resolv.conf** — это [файл](https://en.wikipedia.org/wiki/Computer_file "Computer file"), используемый в различных операционных системах для настройки системного [резолвера](https://en.wikipedia.org/wiki/Resolver_(DNS) "Resolver (DNS)") [DNS (Domain Name System)](https://en.wikipedia.org/wiki/Domain_Name_System "Domain Name System"). Файл представляет собой текстовый файл в формате [plain-text](https://en.wikipedia.org/wiki/Plain-text "Plain-text"), обычно создаваемый сетевым администратором или приложениями, которые управляют задачами конфигурирования системы. Программа [resolvconf](https://en.wikipedia.org/wiki/Resolvconf "Resolvconf") — одна из таких программ на [FreeBSD](https://en.wikipedia.org/wiki/FreeBSD "FreeBSD") или других [Unix](https://en.wikipedia.org/wiki/Unix "Unix")-машинах, которая управляет файлом resolv.conf.

В большинстве [Unix-подобных](https://en.wikipedia.org/wiki/Unix-like "Unix-like") [операционных систем](https://en.wikipedia.org/wiki/Operating_system "Operating system") и других, реализующих библиотеку [резолвера](https://en.wikipedia.org/wiki/Resolver_(DNS) "Resolver (DNS)") [BIND](https://en.wikipedia.org/wiki/BIND "BIND") [DNS](https://en.wikipedia.org/wiki/Domain_Name_System "Domain Name System"), [конфигурационный файл](https://en.wikipedia.org/wiki/Configuration_file "Configuration file") _resolv.conf_ содержит информацию, определяющую рабочие параметры резолвера DNS. Резолвер DNS позволяет приложениям, работающим в операционной системе, преобразовывать удобные для человека [доменные имена](https://en.wikipedia.org/wiki/Domain_name "Domain name") в числовые [IP-адреса](https://en.wikipedia.org/wiki/IP_address "IP address"), которые необходимы для доступа к ресурсам [локальной сети](https://en.wikipedia.org/wiki/Local_area_network "Local area network") или [интернета](https://en.wikipedia.org/wiki/Internet "Internet"). Процесс определения IP-адресов по доменным именам называется [разрешением адресов](https://en.wikipedia.org/wiki/Domain_Name_System "Domain Name System") (address resolution).

## Содержимое и расположение

Файл _resolv.conf_ обычно содержит директивы _search_, которые задают домены поиска по умолчанию ([search domains](https://en.wikipedia.org/wiki/Search_domain "Search domain")), используемые для дополнения данного имени запроса до [полностью определённого доменного имени](https://en.wikipedia.org/wiki/Fully_qualified_domain_name "Fully qualified domain name") (FQDN), когда не указан доменный суффикс. Например, _search example.com local.test_ настраивает резолвер так, чтобы он дополнительно пробовал _somehost.example.com_ и _somehost.local.test_.

Он также содержит список IP-адресов [серверов имён](https://en.wikipedia.org/wiki/Nameserver "Nameserver") для разрешения имён. Например, _nameserver 1.1.1.1_ настраивает резолвер отправлять запросы к серверу имён с IP-адресом [1.1.1.1](https://en.wikipedia.org/wiki/1.1.1.1 "1.1.1.1"). Дополнительные директивы _nameserver_ после первой используются только когда первый или последний использованный сервер недоступен. Пример файла:

```text
search example.com local.test
nameserver 10.0.0.17
nameserver 10.1.0.12
nameserver 10.16.0.7
```

_resolv.conf_ обычно располагается в каталоге [/etc](https://en.wikipedia.org/wiki//etc "/etc") [файловой системы](https://en.wikipedia.org/wiki/File_system "File system"). Файл либо ведётся вручную, либо, когда используется [DHCP](https://en.wikipedia.org/wiki/DHCP "DHCP"), обычно обновляется утилитой [resolvconf](https://en.wikipedia.org/wiki/Resolvconf "Resolvconf").

В дистрибутивах Linux на базе [systemd](https://en.wikipedia.org/wiki/Systemd "Systemd"), использующих systemd-resolved.service, _/etc/resolv.conf_ является симлинком на _/run/systemd/resolve/stub-resolv.conf_ [[1]](https://en.wikipedia.org/wiki/Resolv.conf#cite_note-1).

См. также:

*   [Hosts (файл)](https://en.wikipedia.org/wiki/Hosts_(file) "Hosts (file)")
*   [nsswitch.conf](https://en.wikipedia.org/wiki/Nsswitch.conf#nsswitch.conf "Nsswitch.conf")
*   [resolved.conf](https://en.wikipedia.org/wiki/Systemd "Systemd") [[2]](https://en.wikipedia.org/wiki/Resolv.conf#cite_note-2)
*   [systemd-resolved](https://en.wikipedia.org/wiki/Systemd "Systemd")

Примечания:

1.  [↑](https://en.wikipedia.org/wiki/Resolv.conf#cite_ref-1 "Jump up") [“DebuggingSystemd — Ubuntu Wiki”](https://wiki.ubuntu.com/DebuggingSystemd).
2.  [↑](https://en.wikipedia.org/wiki/Resolv.conf#cite_ref-2 "Jump up") [“Resolved.conf(5) — systemd — Debian testing — Debian Manpages”](https://manpages.debian.org/testing/systemd/resolved.conf.5.en.html).

Внешние ссылки:

*   [“resolv.conf”](https://wiki.archlinux.org/index.php/Resolv.conf) в вики [Arch Linux](https://en.wikipedia.org/wiki/Arch_Linux "Arch Linux")
*   [“resolv.conf”](https://wiki.gentoo.org/wiki/Resolv.conf) в вики [Gentoo Linux](https://en.wikipedia.org/wiki/Gentoo_Linux "Gentoo Linux")
*   `resolv.conf(5)` — [Linux](https://en.wikipedia.org/wiki/Linux "Linux") Programmer's [Manual](https://en.wikipedia.org/wiki/Man_page "Man page") — File Formats from Manned.org
*   `resolv.conf(5)` — [FreeBSD](https://en.wikipedia.org/wiki/FreeBSD "FreeBSD") File Formats [Manual](https://en.wikipedia.org/wiki/Man_page "Man page")
*   `resolv.conf(5)` — [OpenBSD](https://en.wikipedia.org/wiki/OpenBSD "OpenBSD") File Formats [Manual](https://en.wikipedia.org/wiki/Man_page "Man page")

---

[dns](/tags/dns.md)
[linux](/tags/linux.md)
[systemd](/tags/systemd.md)
