# VyOS OpenSource Router

Источник: [VyOS OpenSource Router](https://habr.com/ru/articles/435568/)

В этой статье я хотел поднять не стандартную для меня тему о сетевом маршрутизаторе VyOS. Впервые я познакомился с этим проектом благодаря Нилу Андерсону (Neil Anderson) который составил [гайд как у себя дома развернуть мини-лабораторию с NetApp симулятором и VyOS](https://www.flackbox.com/netapp-simulator).

![](/images/f232255696dd6f6615ceabaf824ea0fb.png)

## Ключевые проекты

[VyOS ](https://vyos.io)это opensource проект на базе Debian Linux, который родился как [форк от проекта Vyatta Core Edition](https://en.wikipedia.org/wiki/VyOS) of the Vyatta Routing software. Как и любой роутер VyOS оперирует на третьем уровне OSI и маршрутизирует North-South трафик. VyOS включает в себя следующие ключевые проекты:

  * Debian 8, ядро 4.19
  * FRRouting (в версии 1.1 и более древних использовался Quagga)
  * ISC-DHCP
  * Keepalived
  * StrongSwan
  * OpenVPN
  * PowerDNS
  * Wireguard
  * OpenNHRP
  * Accel-ppp
  * xL2tpd
  * Squid
  * mDNS-repeater
  * IGMP-Proxy
  * iPerf
  * [более детальный список в Release notes](https://wiki.vyos.net/wiki/1.2.0/release_notes)

## Поддерживаемые платформы

VyOS можно разворачивать на большинстве популярных платформах в виде виртуальной машины, на голом железе или в облаке, образ занимает около 300 МБ.

### Платформы виртуализации

Как виртуальную машину VyOS можно развернуть в окружении:

  * KVM
  * RHEV
  * VirtualBox
  * Nutanix AHV
  * VMWare ESXi 5.1+
  * Citrix XenServer в режиме HVM
  * Microsoft Hyper-V for Windows Server
  * OpenStack (в планах)

### Голое железо

Роутер можно установить на голое железо, кастомные образы (в планах):

  * Dell
  * SuperMicro
  * EdgeCore

### Облака

Как виртуальную машину в облаках:

  * Amazon EC2 (Amazon Machine image on Amazon Web Services)
  * Ravello
  * Packet Cloud
  * Microsoft Azure
  * Google Cloud Platform (в планах)
  * Alibaba Cloud (в планах)

### Командная строка

Как и с маршрутизаторами Cisco и Juniper в которых традиционно не используют графический интерфейс, так и VyOS управляется из командной строки. Командная строка VyOS очень напоминает синтаксис JunOS:

```text
vyos@vyos# run show ip route forward

default via 203.0.113.1 dev eth1 proto static metric 20 onlink
192.168.56.0/24 dev eth0 proto kernel scope link src 192.168.56.13
203.0.113.1 dev eth1 proto static metric 20
```

## Функционал и возможности

Функционал VyOS достаточно большой и серьёзный несмотря на то, что это Opensource проект:

  * VPN: Dynamic Multipoint VPN (DMVPN), GRE, IPSec, IPSec VTI, OpenVPN (server и client) и WireGuard
  * Может выступать в роли VPN Remote Access Server используя L2TP или OpenVPN
  * Туннели: L2TP, L2TPv3, VXLAN, PPTP, GRE, IPIP, SIT, IPIP, IPIP6, IP6IP6
  * Интерфейсы L2/L3: Ethernet Bridge, 802.1Q VLAN, QinQ, Агрегация портов (LACP и статическая)
  * API для работы из консоли, Python, и Perl скриптов
  * Адресация маршрутизация IPv4 & IPv6:
  * BGP, OSPF, OSPFv3, RIP, RIPng протоколов динамической маршрутизации
  * Статическая маршрутизация и Policy-Based Routing (PBR)
  * QoS для приоритизации трафика
  * VyOS может работать как L2TPv3 роутер для Layer 2 связности между сайтами
  * Высокая доступность: VRRP, WAN load-balancing, Conntrack-Sync, Clustering
  * И естественно стандартный набор: DHCP (Сервер, Клиент и Relay), DNS recursive server, Network Address Translation (source and destination, port-address, one-to-many, many-to-many), IGMP-Proxy, NTP сервер и клиент, LLDP сервер и клиент, mDNS repeater, PPPoE server, proxy server с кэшем и фильтрацией, TFTP сервер
  * Фильтрация трафика: Zone-based firewall, stateful firewall
  * Политики: Shaping, Rate limiting, Priority-based queues
  * Встроенный архив конфигурационных файлов

## Пример поддерживаемых схем подключения и использования

### Branch

Одна из наиболее часто используемых схем использования VyOS это объединение нескольких отделений компании между собой, соединение с облачными провайдерами или объединение нескольких облачных провайдеров в одну сеть.

![](/images/5f47ecd6dd6001a4d8dbc341fba08a98.png)

### SMB Edge

Может служить как SMB маршрутизатор предоставляя стабильный и повышенной доступности к глобальной сети Интернет благодаря. VyOS поддерживает NAT, DHCP и VRRP для повышения доступности вашего дефолтного шлюза.

![](/images/c393592d52ba526846ab64a65c11bf37.png)

### Boarder Router

VyOS может быть использован как Enterprise Border Router (BGP), один из, если не самый развитый среди динамических протоколов маршрутизации. Для этих целей VyOS может служить как внешним, так и внутренним BGP узлом (BGP-peer) предоставляя высокую стабильность и доступность в вашей сети.

![](/images/2229c039c42eb796112753658d02ad45.png)

### VPN Gateway

VyOS предоставляет доступ по IPSec VPN: IPSec/GRE, IPSec VTI, Dynamic Multipoint VPN (DMVPN) и OpenVPN. Site-To-Site конфигурация позволит вам соединить несколько сайтов напрямую в облако через частую защищённую сеть поверх глобальной сети Интернет, позволяя вашим пользователям и серверам взаимодействовать друг с другом. VyOS может работать как L2TPv3 маршрутизатор создав L2 сеть между сайтами.

![](/images/633a57d95a9958433b430fbfa0a9640d.png)

### VPN RA Server

VyOS может быть использован как удалённый VPN сервер. Для этого вы можете использовать L2TP over IPSec так как он присутствует почти во всех современных ОС. Другой вариант использовать OpenVPN, который также интегрирован в VyOS. Использование файрволла повысит безопасность и гранулярность доступа к вашей сети.

![](/images/34507a9edfbce6dd542281b9c40e4308.png)

## Системные требования

Минимальные требования VyOS к ресурсам:

  * CPU: одно или несколько ядер 64-bit x86 (зависит от пропускной способности и используемого функционала). Также поддерживается ClearFog ARM платформа
  * Память: 512 MB или больше (зависит от пропускной способности и используемого функционала и главным образом от размера таблиц маршрутизации)
  * Сетевые интерфейсы: минимум один, максимум (столько сколько поддерживает платформа, на которой работает VyOS)
  * Для достижения максимальной производительности рекомендуется использовать сетевые карты с аппаратным offloading и поддерживающие множественные очереди

## Менеджмент и мониторинг

Управления и мониторинг:

  * Разворачивание и управление: Secure Shell (SSH), Cloud-Init, python library для удалённого управления
  * Управление и траблшутинг: Simple Network Management Protocol (SNMP), Syslog, NetFlow, sFlow
  * Автоматизация Ansible, SaltStack
  * Планировщик задач, event handling, scripting
  * Встроенный архив версий конфигураций

## Образы

VyOS можно собрать самому из исходного кода или скачать в виде собранного и оттестированного образа для вашей платформы. Начиная с версии 1.2 скачивание GA образа перестало быть бесплатным, потому что проект нужно развивать на какие-то деньги. [Rolling релизы](http://downloads.vyos.io/?dir=rolling/current/amd64) как и раньше остаются бесплатными. Но [для школ, колледжей, университетов, поликлиник и других подобных некоммерческих организаций предоставляется бесплатный доступ к GA релизам](https://blog.vyos.io/last-rc-early-production-access-and-announcement-of-educational-and-non-profit-access-subscriptions). Для контрибьютеров также предоставляется бесплатный доступ к готовым GA образам, не обязательно быть программистом, даже если вы помогаете с документацией это тоже помощь проекту. Так что получить бесплатный доступ к образам достаточно просто и легко, особенное если у вас есть бейдж Мейнтейнера, Контрибутора или Евангелиста VyOS.

Бейджи
VyOS выпустил [цифровые сертификаты](https://blog.vyos.io/contributors-contributions-and-badges?utm_content=84167604) для:

  * Мейнтейнеров проекта
  * Контрибуторов
  * Евангелистов
  * и Сетевых инженеров

## Выводы

VyOS это проект, который построен на базе современных программ и утилит для сетевой маршрутизации, которую можно легко дополнить и изменить благодаря тому, что он является полностью 100% OpenSource. Богатый функционал и современные протоколы маршрутизации позволяют его использовать не только в домашних условиях для продвинутых пользователей, а также для больших компаний и огромных сервис провайдеров.

### Полезные ресурсы

[blog.vyos.io](http://blog.vyos.io)
[wiki.vyos.net](https://wiki.vyos.net)
[Issue tracker](https://phabricator.vyos.net/)
[slack.vyos.io](https://slack.vyos.io)
[forum.vyos.io](https://forum.vyos.io)
[github.com/vyos](https://github.com/vyos)
[twitter.com/vyos_dev](https://twitter.com/vyos_dev)
[LinkedIn](https://www.linkedin.com/company/vyos)
[Facebook](https://www.facebook.com/vyosofficial/)
[YouTube](https://www.youtube.com/channel/UCEjJx6j87szaiqtKDrMVb2Q)
[VyOS Roadmap](https://trello.com/b/KhGDOsmr/vyos-public-roadmap)
[Rolling Релизы](http://downloads.vyos.io/?dir=rolling/current/amd64)

### Другие статьи на Хабре

[Программная маршрутизация с VyOS](https://habr.com/ru/company/selectel/blog/248907/)
[Эмулятор UNetLab — революционный прыжок](https://habr.com/ru/post/262027/)
[Vyatta: Linux-based firewall and router](https://habr.com/ru/post/40648/)
[Интернет на теплоходе: спутниковая тарелка + модемы + балансировщик + Wi-Fi](https://habr.com/ru/company/beeline/blog/128701/)
[Ubiquiti EdgeRouter X](https://habr.com/ru/company/comptek/blog/255391/)

Сообщения по ошибкам в тексте прошу направлять в ЛС. Замечания, дополнения и вопросы по статье напротив, прошу в комментарии.
  *[ЛС]: Личное сообщение

**********

[vyos](/tags/vyos.md)
