# VyOS с нуля: маршрутизация и VPS

Источник: [VyOS from Scratch: Routing and VPS Edition](https://blog.kroy.io/2021/06/23/vyos-from-scratch-routing-and-vps-edition/)

Kroy (blog.kroy.io) · 23 июня 2021 · рубрики Routing, vpn, VyOS

![VyOS from Scratch: Routing and VPS Edition](/images/7470f68c5f3e712d7a437c135d965929.png)

Уже давно я хотел задокументировать более сложную настройку маршрутизации с [VyOS](https://vyos.io/), и вот она. Маршрутизация с BGP, WireGuard к VPS и маршрутизация на основе политик (Policy Based Routing)?

Это будет весело.

* * *

Маршрутизация легко стала одним из моих любимых занятий в лабе. Особенно если учесть, что когда-то это была для меня невероятно загадочная вещь.

Так что честное предупреждение. Статья будет длинной.

Я собираюсь:

* Настроить VPS и внутренний домашний маршрутизатор.
* Использовать WireGuard для соединения VPS и внутреннего домашнего маршрутизатора.
* Настроить ещё несколько внутренних маршрутизаторов и запустить трафик.
* Маршрутизировать трафик с обычного десктопа через VPS, всё по BGP.

## Маршрутизация

Маршрутизация, если выразиться максимально просто, — это «где мне найти этот IP-адрес, который я ищу».

Так что если хост/сервер/устройство хочет добраться до какого-то IP, ему нужно знать путь туда. И оно может общаться только с устройствами, с которыми соединено локально, то есть с устройством в том же локальном интерфейсе/подсети.

> Есть два основных типа маршрутизации, о которых я буду говорить.
>
> Статическая — это «эй, я знаю, какие подсети где находятся, и я всё размечу вручную», и динамическая — «я установлю отношения с другими маршрутизаторами и буду узнавать всё автоматически».

BGP, или Border Gateway Protocol, — это тип динамической маршрутизации, который я здесь использую.

* * *

Разберём основную таблицу маршрутизации одного из моих основных маршрутизаторов (`show ip route` в VyOS):

```text
B>* 0.0.0.0/0 [20/0] via 10.245.245.9, eth0.508, weight 1, 00:00:08
C * 10.0.11.0/24 is directly connected, eth0.11, 01w0d22h
C>* 10.0.11.0/24 is directly connected, eth0.11, 01w0d22h
C>* 10.0.35.0/30 is directly connected, eth0.35, 01w0d22h
C * 10.3.1.0/24 is directly connected, eth0.3, 01w0d22h
C>* 10.3.1.0/24 is directly connected, eth0.3, 01w0d22h
C * 10.9.1.0/24 is directly connected, eth0.9, 01w0d22h
C>* 10.9.1.0/24 is directly connected, eth0.9, 01w0d22h
C * 10.10.8.0/24 is directly connected, eth0.8, 01w0d22h
C>* 10.10.8.0/24 is directly connected, eth0.8, 01w0d22h
C * 10.10.51.0/24 is directly connected, eth0.51, 01w0d22h
C>* 10.10.51.0/24 is directly connected, eth0.51, 01w0d22h
C * 10.20.20.0/24 is directly connected, eth0.20, 01w0d22h
C>* 10.20.20.0/24 is directly connected, eth0.20, 01w0d22h
C * 10.21.21.0/24 is directly connected, eth0.21, 01w0d22h
C>* 10.21.21.0/24 is directly connected, eth0.21, 01w0d22h
C * 10.22.22.0/24 is directly connected, eth0.22, 01w0d22h
C>* 10.22.22.0/24 is directly connected, eth0.22, 01w0d22h
B>* 10.53.53.53/32 [20/0] via 10.3.1.252, eth0.3, weight 1, 01w0d22h
  *                       via 10.3.1.254, eth0.3, weight 1, 01w0d22h
B>* 10.53.53.54/32 [20/0] via 10.3.1.252, eth0.3, weight 1, 01w0d22h
  *                       via 10.3.1.254, eth0.3, weight 1, 01w0d22h
C>* 10.245.245.8/30 is directly connected, eth0.508, 01w0d22h
```

Здесь происходит много всего, но, надеюсь, большая часть довольно очевидна:

* `B>* 0.0.0.0/0`: этот маршрут получен от моего основного граничного маршрутизатора через BGP. Это [CIDR](https://www.keycdn.com/support/what-is-cidr#:~:text=CIDR%2C%20which%20stands%20for%20Classless,the%20growth%20of%20routing%20tables.), представляющий «все адреса интернета». Это значит, что любой IP или подсетью, о которой этот сервер не знает, будет перенаправлено устройству `10.245.245.9`.
* `C> * ...` и `C *` — всё это «directly connected» (непосредственно подключённые). То есть это подсети, существующие прямо на этом маршрутизаторе. Здесь несколько записей, потому что я использую [VRRP](https://docs.vyos.io/en/equuleus/configuration/highavailability/index.html?highlight=vrrp), и этот маршрутизатор сейчас держит статус _MASTER_ для резервного IP:

![](/images/14fd37e75d332bad1c26e0d888d304ab.png)

* У меня здесь две особые записи: `10.53.53.53/32` и `10.53.53.54/32`. Обе получены от моих DNS-серверов через BGP для своего рода «anycast DNS». Это значит: если хост 252 недоступен, 10.53.53.53 и 10.53.53.54 всё равно будут отвечать на DNS-запросы, обслуживаемые с хоста 254. И наоборот с хостом 254. Я могу поднять дополнительные DNS-серверы с нулевыми усилиями, и они всё равно будут отвечать на мои кастомные DNS-IP. В какой-то момент мой DNS-диапазон был `10.3.1.248-254`, то есть у меня было ОЧЕНЬ много DNS-серверов, отвечающих на одни и те же два IP. Это предотвращает странности в том, как разные ОС обрабатывают основной и резервный DNS.
* И наконец, ещё один непосредственно подключённый маршрут. Это `/30`, который общается с моим основным граничным маршрутизатором.

* * *

### Поговорим о CIDR

CIDR — очень важное понятие в маршрутизации. Они представляют собой `/24` после сети в описаниях выше. Чем меньше число CIDR, тем больше IP-адресов представляет эта сеть.

У большинства подсетей есть адрес сети и широковещательный адрес, и ни один из них нельзя использовать для хостов в этой подсети.

По моему мнению, инструмент вроде `sipcalc` делает всё предельно ясным:

* Обычный `/24`. Это то, что люди обычно используют для LAN-подсетей. Хороший диапазон из 254 пригодных адресов. Многие ставят свой маршрутизатор на `10.3.1.1` или `10.3.1.254` и резервируют DHCP-диапазон где-то посередине. Адреса .0 и .255 зарезервированы под адрес сети и широковещательный соответственно.

```text
❯ sipcalc 10.3.1.0/24
-[ipv4 : 10.3.1.0/24] - 0

[CIDR]
Host address            - 10.3.1.0
Host address (decimal)  - 167969024
Host address (hex)      - A030100
Network address         - 10.3.1.0
Network mask            - 255.255.255.0
Network mask (bits)     - 24
Network mask (hex)      - FFFFFF00
Broadcast address       - 10.3.1.255
Cisco wildcard          - 0.0.0.255
Addresses in network    - 256
Network range           - 10.3.1.0 - 10.3.1.255
Usable range            - 10.3.1.1 - 10.3.1.254
```

* `/30`. Часто используется для соединений «точка-точка». Представлено четыре адреса, но доступны только два средних — опять же из-за адресов сети/широковещания.

```text
❯ sipcalc 10.245.245.8/30
-[ipv4 : 10.245.245.8/30] - 0

[CIDR]
Host address            - 10.245.245.8
Host address (decimal)  - 183891208
Host address (hex)      - AF5F508
Network address         - 10.245.245.8
Network mask            - 255.255.255.252
Network mask (bits)     - 30
Network mask (hex)      - FFFFFFFC
Broadcast address       - 10.245.245.11
Cisco wildcard          - 0.0.0.3
Addresses in network    - 4
Network range           - 10.245.245.8 - 10.245.245.11
Usable range            - 10.245.245.9 - 10.245.245.10
```

* Большинство людей использует более крупные подсети как «сводные сети» (summary networks), например этот `/8`. Он включал бы `10.3.1.0/24` и `10.245.245.8/30` выше. То есть если вы хотите адресовать оба и не хотите иметь две записи маршрутизации, можно использовать один маршрут:

```text
❯ sipcalc 10.0.0.0/8
-[ipv4 : 10.0.0.0/8] - 0

[CIDR]
Host address            - 10.0.0.0
Host address (decimal)  - 167772160
Host address (hex)      - A000000
Network address         - 10.0.0.0
Network mask            - 255.0.0.0
Network mask (bits)     - 8
Network mask (hex)      - FF000000
Broadcast address       - 10.255.255.255
Cisco wildcard          - 0.255.255.255
Addresses in network    - 16777216
Network range           - 10.0.0.0 - 10.255.255.255
Usable range            - 10.0.0.1 - 10.255.255.254
```

* Наконец, пара «специальных» подсетей/CIDR. У нас есть `/31`, который используется для соединений «точка-точка» без траты двух адресов, и `0.0.0.0/0` — маршрут по умолчанию, представляющий весь интернет. Обратите внимание, что адрес `.0` в `/31` фактически пригоден к использованию! То есть два пригодных адреса — это `10.42.42.0 / 10.42.42.1`. Это странно, если вы к этому не привыкли:

```text
❯ sipcalc 10.42.42.0/31
-[ipv4 : 10.42.42.0/31] - 0

[CIDR]
Host address            - 10.42.42.0
Host address (decimal)  - 170535424
Host address (hex)      - A2A2A00
Network address         - 10.42.42.0
Network mask            - 255.255.255.254
Network mask (bits)     - 31
Network mask (hex)      - FFFFFFFE
Broadcast address       - 10.42.42.1
Cisco wildcard          - 0.0.0.1
Addresses in network    - 2
Network range           - 10.42.42.0 - 10.42.42.1

❯ sipcalc 0.0.0.0/0
-[ipv4 : 0.0.0.0/0] - 0

[CIDR]
Host address            - 0.0.0.0
Host address (decimal)  - 0
Host address (hex)      - 0
Network address         - 0.0.0.0
Network mask            - 0.0.0.0
Network mask (bits)     - 0
Network mask (hex)      - 0
Broadcast address       - 255.255.255.255
Cisco wildcard          - 255.255.255.255
Addresses in network    - 4294967295
Network range           - 0.0.0.0 - 255.255.255.255
Usable range            - 0.0.0.1 - 255.255.255.254
```

Так что `10.53.53.0/24` охватывает `10.53.53.53/32`. И в мире маршрутизации, если бы у вас в таблице были маршруты для обоих, был бы выбран более специфичный `/32`, чтобы добраться до хоста `10.53.53.53`.

Я знаю, что всё это был поток информации, но, надеюсь, это кое-что прояснило.

* * *

## Настройка Дом -> VPS

Я не хочу слишком увязать в деталях конфигурации домашних маршрутизаторов и VPS. Но я использую относительно свежий билд [vyos-rolling](https://downloads.vyos.io/?dir=rolling/current/amd64) и поднял дешёвый VPS в Vultr для этого блога.

Эта диаграмма показывает, чего я пытаюсь достичь:

![](/images/7470f68c5f3e712d7a437c135d965929.png)

### Настройка дома

Дома я зарыл новенькую VM VyOS глубоко внутри своей сети. Так что это будет представлять сетап кого-то за множеством слоёв NAT, включая carrier-grade, то есть они, возможно, не могут делать проброс портов.

Это наш маршрутизатор `edge` для этого сетапа.

Я предполагаю некоторое знакомство с VyOS в целом, но кратко пройдусь по прилагаемому конфигу:

* Выполните `generate wireguard named-keypairs Vultr` в op-режиме. Это создаёт приватный ключ для вставки в следующий конфиг.
* Выполните `show wireguard keypairs pubkey Vultr`, чтобы получить публичный ключ для конфига VPS.
* Настройте «WAN»-подключение. Это просто какой-то статический IP в существующей LAN.
* Настройте пару интерфейсов, которые будут общаться с несколькими другими маршрутизаторами. Эти адреса `10.42.0.0/16` или `10.42.0-255.0/24` — основные подсети, с которыми мы будем играть.
* Сделайте немного source NAT. Это позволит всему, что за этим маршрутизатором в любой подсети внутри `10.42.0.0/16`, попасть в интернет.
* Настройте соединение WireGuard к моему VPS (оно будет удалено до публикации блога, поэтому я оставляю IP).

```text
* Set the description and local IP for this tunnel. I'm using a `/31` as mentioned in the above CIDR section.
* Set the `allowed-ips`. This is the traffic we want to allow the traverse this tunnel. We are including both the tunnel `/31` subnet and the `/16` subnet.
* Make sure we have the `persistent-keepalive 15` set here. Since we aren't doing a site-to-site, we need to make sure to have this, so the tunnel doesn't timeout. The tunnel can ONLY be brought up when traffic attempts to go from Home->VPS and not vice-versa because we are emulating CGNAT here.
* The address and the port of the VPS that WireGuard is configured to listen on
* The public key of the VPS. From running `show wireguard keypairs pubkey Home` on the **VPS** after generating it with `generate wireguard named-keypairs Home`
```

* Выбор локального приватного ключа для этого соединения. Он должен соответствовать «generate …», который вы выполнили выше.
* Мой маршрут по умолчанию для этого маршрутизатора, чтобы у меня был доступ в интернет.
* Включение SSH и имя этого маршрутизатора.

```text
vyos@vyoslab-edge:~$ show configuration commands
set interfaces ethernet eth0 address '10.21.21.10/24'
set interfaces ethernet eth0 description 'WAN'
set interfaces ethernet eth1 address '10.42.0.1/24'
set interfaces ethernet eth1 description 'LAB1'
set interfaces ethernet eth2 address '10.42.1.1/24'
set interfaces ethernet eth2 description 'LAB2'
set interfaces loopback lo
set nat source rule 10 description 'Outgoing NAT'
set nat source rule 10 outbound-interface 'eth0'
set nat source rule 10 source address '10.42.0.0/16'
set nat source rule 10 translation address 'masquerade'
set interfaces wireguard wg0 address '172.24.32.1/31'
set interfaces wireguard wg0 description 'lab-ptp-vps'
set interfaces wireguard wg0 peer VPS-Lab address '144.202.75.103'
set interfaces wireguard wg0 peer VPS-Lab allowed-ips '172.24.32.0/31'
set interfaces wireguard wg0 peer VPS-Lab allowed-ips '10.42.0.0/16'
set interfaces wireguard wg0 peer VPS-Lab persistent-keepalive '15'
set interfaces wireguard wg0 peer VPS-Lab port '8765'
set interfaces wireguard wg0 peer VPS-Lab pubkey 'lQWPCw1f+B15Au441P2qwue8/YIZ3FLTTW+6N3EzhWM='
set interfaces wireguard wg0 private-key 'Vultr'
set protocols static route 0.0.0.0/0 next-hop 10.21.21.1
set service ssh port '22'
set system host-name 'vyoslab-edge'
```

Надеюсь, это покажет, откуда берутся pubkey:

```text
vyos@vyoslab-edge:~$ show wireguard keypairs pubkey Vultr
vzJetiL/M5Ujkb5DiwaG1CMAMr1Ib6a4OGdvlIMNWXs=
```

### Настройка VPS

В Vultr я сделал очень простой конфиг VyOS с минимумом для выхода в сеть и комплементарным конфигом WireGuard.

* Статический IP этого VPS и маршрут по умолчанию.
* Включите SSH.
* Задайте имя хоста.
* Настройте WireGuard.

```text
* Uses the opposite IP address, the .0, in the `/31` subnet
* Uses the pubkey from above.

vyos@vyoslab-vps# run show configuration commands
set interfaces ethernet eth0 address '144.202.75.103/23'
set interfaces loopback lo
set interfaces wireguard wg0 address '172.24.32.0/31'
set interfaces wireguard wg0 description 'lab-ptp-home'
set interfaces wireguard wg0 peer HomeLab allowed-ips '172.24.32.0/31'
set interfaces wireguard wg0 peer HomeLab allowed-ips '10.42.0.0/16'
set interfaces wireguard wg0 peer HomeLab pubkey 'vzJetiL/M5Ujkb5DiwaG1CMAMr1Ib6a4OGdvlIMNWXs='
set interfaces wireguard wg0 port '8765'
set interfaces wireguard wg0 private-key 'Home'
set protocols static route 0.0.0.0/0 next-hop 144.202.74.1
set service ssh port '22'
set system host-name 'vyoslab-vps'
```

И ключ, который совпадёт с конфигом pubkey Дома:

```text
vyos@vyoslab-vps:~$ show wireguard keypairs pubkey Home
lQWPCw1f+B15Au441P2qwue8/YIZ3FLTTW+6N3EzhWM=
```

Если вы внимательны, то заметите, что на стороне VPS в конфиге WireGuard нет директивы «endpoint».

Мы запускаем WireGuard здесь как сервер, а не site-to-site.

Хотя WireGuard'у в целом всё равно, на это стоит обратить внимание, потому что это имеет важные последствия, как намекалось выше.

В этом сетапе, если вы на VPS попробуете поднять туннель, ничего не произойдёт. Потому что VPS не знает, как добраться до другого конца. Так что трафик должен исходить с домашней стороны — и именно поэтому у нас `persistent-keepalive` на домашней стороне, чтобы туннель оставался поднятым.

* * *

> Кто-то мог заметить… я тут НИЧЕГО не делал в плане безопасности.
>
> Честно говоря, это, вероятно, вне рамок того, что я делаю. Локальный «edge»-маршрутизатор зарыто так глубоко в моей homelab, что это не важно. А что до маршрутизатора VPS — уверен, некоторые кричат ПОЧЕМУ ПОЧЕМУ ПОЧЕМУ?
>
> Это потому, что я использую файрвол Vultr, чтобы блокировать весь трафик отовсюду, кроме меня. Так что успокойтесь.

* * *

## Туннели подняты!

Если вы дочитали до сюда, ваш туннель должен быть поднят. Пинг должен работать до противоположного конца туннеля (дом — это .1, так что пингуйте .0):

```text
vyos@vyoslab-edge:~$ ping 172.24.32.0 count 4
PING 172.24.32.0 (172.24.32.0) 56(84) bytes of data.
64 bytes from 172.24.32.0: icmp_seq=1 ttl=64 time=19.9 ms
64 bytes from 172.24.32.0: icmp_seq=2 ttl=64 time=19.3 ms
64 bytes from 172.24.32.0: icmp_seq=3 ttl=64 time=19.3 ms
64 bytes from 172.24.32.0: icmp_seq=4 ttl=64 time=18.8 ms

--- 172.24.32.0 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 8ms
rtt min/avg/max/mdev = 18.768/19.333/19.887/0.419 ms
```

И простая op-команда show:

```text
vyos@vyoslab-edge:~$ show interfaces wireguard wg0
interface: wg0
  description: lab-ptp-vps
  address: 172.24.32.1/31
  public key: vzJetiL/M5Ujkb5DiwaG1CMAMr1Ib6a4OGdvlIMNWXs=
  private key: (hidden)
  listening port: 37175

  peer: VPS-Lab
    public key: lQWPCw1f+B15Au441P2qwue8/YIZ3FLTTW+6N3EzhWM=
    latest handshake: 0:01:16
    status: active
    endpoint: 144.202.75.103:8765
    allowed ips: 172.24.32.0/31, 10.42.0.0/16
    transfer: 54 KB received, 251 KB sent
    persistent keepalive: every 15 seconds

    RX:   bytes  packets  errors  dropped  overrun       mcast
          56008      599       0        0        0           0
    TX:   bytes  packets  errors  dropped  carrier  collisions
         257096     5728       0        1        0           0
```

* * *

### Маршрутизируй это!

Но цель здесь не просто поднять туннель. Мы действительно хотим добраться до `LAB1/2` на домашнем `edge`-маршрутизаторе с VPS.

```text
vyos@vyoslab-edge:~$ show interfaces
Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
Interface        IP Address                        S/L  Description
---------        ----------                        ---  -----------
eth0             10.21.21.10/24                    u/u  WAN
eth1             10.42.0.1/24                      u/u  LAB1
eth2             10.42.1.1/24                      u/u  LAB2
lo               127.0.0.1/8                       u/u
                 ::1/128
wg0              172.24.32.1/31                    u/u  lab-ptp-vps
```

Так что давайте сделаем это. С VPS:

```text
vyos@vyoslab-vps:~$ ping 10.42.0.1 count 4
PING 10.42.0.1 (10.42.0.1) 56(84) bytes of data.
^C
--- 10.42.0.1 ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 87ms
```

В чём проблема? Посмотрите на таблицу маршрутизации:

```text
vyos@vyoslab-vps:~$ show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 144.202.74.1, eth0, weight 1, 1d00h17m
C>* 144.202.74.0/23 is directly connected, eth0, 1d00h17m
C>* 172.24.32.0/31 is directly connected, wg0, 1d00h17m
```

Поскольку `10.42.0.1` не совпадает ни с одной подсетью в таблице маршрутизации, он попытается выйти через маршрут по умолчанию `0.0.0.0/0`. Это не сработает, потому что приватные IP не могут маршрутизироваться через публичный интернет.

#### Статическая маршрутизация, лёгкий выход

Есть несколько способов обойти это. Простая статическая запись для каждой из LAB-подсетей, указывающая на домашний IP туннеля (VPS — это .0, дом — это .1):

```text
vyos@vyoslab-vps# set protocols static route 10.42.0.0/24 next-hop 172.24.32.1
[edit]
vyos@vyoslab-vps# set protocols static route 10.42.1.0/24 next-hop 172.24.32.1
[edit]
vyos@vyoslab-vps# commit
Done
[edit]
vyos@vyoslab-vps# run show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 144.202.74.1, eth0, weight 1, 1d00h25m
S>* 10.42.0.0/24 [1/0] via 172.24.32.1, wg0, weight 1, 00:00:05
S>* 10.42.1.0/24 [1/0] via 172.24.32.1, wg0, weight 1, 00:00:05
C>* 144.202.74.0/23 is directly connected, eth0, 1d00h25m
C>* 172.24.32.0/31 is directly connected, wg0, 1d00h25m
[edit]
vyos@vyoslab-vps#
```

Конечно, это некрасиво, и поскольку я намеренно спроектировал используемые здесь подсети так, чтобы их было легко «суммировать», есть ОЧЕНЬ простое решение:

```text
vyos@vyoslab-vps# delete protocols static route 10.42.0.0/24
[edit]
vyos@vyoslab-vps# delete protocols static route 10.42.1.0/24
[edit]
vyos@vyoslab-vps# set protocols static route 10.42.0.0/16 next-hop 172.24.32.1
[edit]
vyos@vyoslab-vps# commit
[edit]
vyos@vyoslab-vps# save
Saving configuration to '/config/config.boot'...
Done
[edit]
vyos@vyoslab-vps# run show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 144.202.74.1, eth0, weight 1, 1d00h28m
S>* 10.42.0.0/16 [1/0] via 172.24.32.1, wg0, weight 1, 00:00:09
C>* 144.202.74.0/23 is directly connected, eth0, 1d00h28m
C>* 172.24.32.0/31 is directly connected, wg0, 1d00h28m
```

В обоих случаях простой пинг на адрес LAB1 или LAB2 у `edge` должен работать с VPS:

```text
vyos@vyoslab-vps# run ping 10.42.0.1 count 2
PING 10.42.0.1 (10.42.0.1) 56(84) bytes of data.
64 bytes from 10.42.0.1: icmp_seq=1 ttl=64 time=18.6 ms
64 bytes from 10.42.0.1: icmp_seq=2 ttl=64 time=19.2 ms

--- 10.42.0.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 3ms
rtt min/avg/max/mdev = 18.624/18.908/19.193/0.315 ms
[edit]
vyos@vyoslab-vps# run ping 10.42.1.1 count 2
PING 10.42.1.1 (10.42.1.1) 56(84) bytes of data.
64 bytes from 10.42.1.1: icmp_seq=1 ttl=64 time=19.5 ms
64 bytes from 10.42.1.1: icmp_seq=2 ttl=64 time=19.2 ms

--- 10.42.1.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 3ms
rtt min/avg/max/mdev = 19.164/19.338/19.512/0.174 ms
[edit]
```

Теперь, когда всё работает, удалите это и вернитесь к чистому состоянию, чтобы мы могли перейти к BGP:

```text
vyos@vyoslab-vps# delete protocols static route 10.42.0.0/16
[edit]
vyos@vyoslab-vps# commit
[edit]
vyos@vyoslab-vps# run show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 144.202.74.1, eth0, weight 1, 1d00h56m
C>* 144.202.74.0/23 is directly connected, eth0, 1d00h56m
C>* 172.24.32.0/31 is directly connected, wg0, 1d00h56m
```

* * *

#### BGP, чуть менее лёгкий выход

Так почему бы просто не использовать статическую маршрутизацию? Работает же? Да, работает… но имеет ряд заметных проблем:

* Требует планирования. Особенно если вы хотите разумно использовать сводные маршруты.
* Может потребовать много сопровождения по мере роста и изменения вашей сети.
* Это не BGP, а BGP — это просто круто.

Что касается первого пункта: кто вообще планирует? Знаю, что я нет. Я лучше подправлю конфиг на одном-двух маршрутизаторах, чем на всех.

В любом случае, мы здесь за BGP, так что займёмся им.

Если вы не знаете, что такое BGP, погуглите. Есть 1000 разных ресурсов, которые объяснят это лучше меня.

Есть два основных типа: внутренний и внешний (eBGP), и мы сосредоточимся на внешнем, потому что он более plug-and-play.

ASN, или Autonomous System Number, — важное понятие в eBGP. Когда вы анонсируете публичные подсети, вам нужен официально утверждённый ASN от организации вроде [ARIN](https://www.arin.net/resources/guide/asn/), но для наших целей есть несколько приватных диапазонов, которые мы можем использовать:

* 64512–65534 (16 бит)
* 4200000000–4294967294 (32 бита)

ASN используются и для идентификации, и для решений о маршрутизации. Если бы я хотел, чтобы маршрут иногда шёл по более короткому пути, а иногда по более длинному, я мог бы выставить ASN PATH в BGP «64512 64512 64512» на одном пире против просто «64512» на втором. Это дало бы предпочтение более короткому пути.

Действительно ли важно, использовать неприватный? Наверное, нет. И для наших случаев это повредит даже меньше, чем неправильное использование не-[RFC1918](https://datatracker.ietf.org/doc/html/rfc1918)-адресов, которое люди иногда делают в homelab. Но быть хорошим сетевым гражданином с порога — хорошая практика.

##### Настройка Дома

Я начну с домашней настройки, так как она будет своего рода центральным хабом. Сначала базовый пиринг:

```text
vyos@vyoslab-edge:~$ show configuration commands
set protocols bgp local-as '4200000000'
set protocols bgp neighbor 172.24.32.0 remote-as '4200000001'
```

Я выберу очень базовую настройку — просто подниму начальный туннель.

Пройдёмся по этому, чтобы понять, что происходит:

* Задаём наш локальный ASN. Для `edge` я использую нижний приватный 32-битный ASN.
* Настраиваем соседа — это IP `vps` через wireguard, следующий доступный 32-битный ASN.

##### Настройка VPS

На VPS аналогично простой конфиг со всем поменяным местами. Мы используем сторону `edge` туннеля WireGuard и меняем соответствующие локальный и удалённый ASN.

```text
vyos@vyoslab-vps# run show configuration commands
set protocols bgp local-as '4200000001'
set protocols bgp neighbor 172.24.32.1 remote-as '4200000000'
```

С этим туннель должен подняться. В op-режиме:

```text
vyos@vyoslab-edge:~$ show bgp summary

IPv4 Unicast Summary:
BGP router identifier 172.24.32.1, local AS number 4200000000 vrf-id 0
BGP table version 0
RIB entries 0, using 0 bytes of memory
Peers 1, using 21 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
172.24.32.0     4 4200000001        15        15        0    0    0 00:12:27            0        0

Total number of neighbors 1
vyos@vyoslab-edge:~$
```

и

```text
vyos@vyoslab-vps# run show bgp summary

IPv4 Unicast Summary:
BGP router identifier 172.24.32.0, local AS number 4200000001 vrf-id 0
BGP table version 0
RIB entries 0, using 0 bytes of memory
Peers 1, using 21 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
172.24.32.1     4 4200000000        16        16        0    0    0 00:14:00            0        0

Total number of neighbors 1
[edit]
```

Важно отметить, что ASN и IP соседа меняются местами на каждом хосте.

* * *

Конечно, нам нужны небольшие модификации, чтобы реально запустить анонсирование.

Сначала нужно сказать домашнему `edge` анонсировать свои подключённые маршруты. Это значит, что мы хотим перераспределить любые маршруты этого маршрутизатора, привязанные к интерфейсам:

```text
vyos@vyoslab-edge:~$ show configuration commands
set protocols bgp address-family ipv4-unicast redistribute connected
```

а затем на маршрутизаторе VPS мгновенно получать обновления:

```text
vyos@vyoslab-vps# set protocols bgp neighbor 172.24.32.1 address-family ipv4-unicast soft-reconfiguration inbound
[edit]
vyos@vyoslab-vps# commit
```

С этим, если вы посмотрите на маршрутизатор `vps`, увидите, что происходит:

```text
vyos@vyoslab-vps:~$ show bgp summary

IPv4 Unicast Summary:
BGP router identifier 172.24.32.0, local AS number 4200000001 vrf-id 0
BGP table version 8
RIB entries 9, using 1728 bytes of memory
Peers 1, using 21 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
172.24.32.1     4 4200000000        51        40        0    0    0 00:33:36            5        5

Total number of neighbors 1
```

Посмотрим на нашу таблицу маршрутизации на `vps`:

```text
vyos@vyoslab-vps:~$ show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 144.202.74.1, eth0, weight 1, 00:37:57
B>* 10.21.21.0/24 [20/0] via 172.24.32.1, wg0, weight 1, 00:13:12
B>* 10.42.0.0/24 [20/0] via 172.24.32.1, wg0, weight 1, 00:13:12
B>* 10.42.1.0/24 [20/0] via 172.24.32.1, wg0, weight 1, 00:13:12
C>* 144.202.74.0/23 is directly connected, eth0, 00:38:03
B   172.24.32.0/31 [20/0] via 172.24.32.1 inactive, weight 1, 00:13:12
C>* 172.24.32.0/31 is directly connected, wg0, 00:38:00
```

Если всё работает, любой маршрут, существующий в таблице нашего `edge` как «directly connected», должен присутствовать в таблице `vps`, идущим через туннель WireGuard.

Можно проверить это, добавив новый dummy-интерфейс на маршрутизаторе `edge`:

```text
vyos@vyoslab-edge# set interfaces dummy dum0 address 172.22.22.255/32
[edit]
vyos@vyoslab-edge# commit
```

Почти сразу вы должны увидеть его в таблице маршрутизации на `vps`, но он не будет пинговаться, потому что не входит в `allowed-ips` туннеля WireGuard:

```text
vyos@vyoslab-vps:~$ show ip route 172.22.22.255/32
Routing entry for 172.22.22.255/32
  Known via "bgp", distance 20, metric 0, best
  Last update 00:00:36 ago
  * 172.24.32.1, via wg0, weight 1

vyos@vyoslab-vps:~$ ping 172.22.22.255
PING 172.22.22.255 (172.22.22.255) 56(84) bytes of data.
From 172.24.32.0 icmp_seq=1 Destination Host Unreachable
ping: sendmsg: Required key not available
From 172.24.32.0 icmp_seq=2 Destination Host Unreachable
ping: sendmsg: Required key not available
^C
--- 172.22.22.255 ping statistics ---
2 packets transmitted, 0 received, +2 errors, 100% packet loss, time 54ms
```

Теперь может начаться настоящие веселье…

* * *

## BGeeeeeP для всего

Если вы следили за ходом, мы завершили верхнюю часть нашей диаграммы:

![](/images/0d23ed968564a65ba1508b3f9d05da24.png)

Пора поднять наши маршрутизаторы LAB1 и LAB2.

* * *

### Пара внутренних маршрутизаторов

Первое, что я сделаю, — подготовлю маршрутизатор `edge` к соединению с `lab1` и `lab2`:

* Настроить соседа, указывающего на `lab1`.
* `default-originate` говорит этому маршрутизатору автоматически задать маршрут по умолчанию для `lab1` на этот маршрутизатор.
* Как и раньше, быстро получать обновления от `lab1`.
* Задать следующий ASN в очереди.
* Повторить для `lab2`.

```text
set protocols bgp neighbor 10.42.0.2 address-family ipv4-unicast default-originate
set protocols bgp neighbor 10.42.0.2 address-family ipv4-unicast soft-reconfiguration inbound
set protocols bgp neighbor 10.42.0.2 remote-as '4200000002'
set protocols bgp neighbor 10.42.1.2 address-family ipv4-unicast default-originate
set protocols bgp neighbor 10.42.1.2 address-family ipv4-unicast soft-reconfiguration inbound
set protocols bgp neighbor 10.42.1.2 remote-as '4200000003'
```

* * *

Конфиги у этих двух почти идентичные. Обратите внимание на изменения IP-адресов и ASN.

* Я использую слегка другой метод анонсирования на `lab2`. Вместо перераспределения всех подключённых сетей я выбираю конкретную сеть для выдачи.
* Я настроил DHCP-серверы. Это чтобы просто подключить клиента и начать тестирование.
* Я также не стал настраивать source NAT. Это чтобы можно напрямую попадать в сети 100/101 с VPS.
* Заметьте, что у обоих отсутствует маршрут/шлюз по умолчанию `0.0.0.0/0`. Потому что они получают его по BGP.

#### LAB1

```text
vyos@vyoslab-lab1:~$ show configuration commands
set interfaces ethernet eth0 address '10.42.0.2/24'
set interfaces ethernet eth1 address '10.42.100.1/24'
set interfaces loopback lo
set protocols bgp address-family ipv4-unicast redistribute connected
set protocols bgp local-as '4200000002'
set protocols bgp neighbor 10.42.0.1 address-family ipv4-unicast soft-reconfiguration inbound
set protocols bgp neighbor 10.42.0.1 remote-as '4200000000'
set service dhcp-server shared-network-name LAB1 subnet 10.42.100.0/24 default-router '10.42.100.1'
set service dhcp-server shared-network-name LAB1 subnet 10.42.100.0/24 dns-server '1.1.1.1'
set service dhcp-server shared-network-name LAB1 subnet 10.42.100.0/24 dns-server '1.0.0.1'
set service dhcp-server shared-network-name LAB1 subnet 10.42.100.0/24 range 0 start '10.42.100.100'
set service dhcp-server shared-network-name LAB1 subnet 10.42.100.0/24 range 0 stop '10.42.100.200'
set service ssh port '22'
set system host-name 'vyoslab-lab1'
```

#### LAB2

```text
vyos@vyoslab-lab2:~$ show configuration commands
set interfaces ethernet eth0 address '10.42.1.2/24'
set interfaces ethernet eth1 address '10.42.101.1/24'
set interfaces loopback lo
set protocols bgp address-family ipv4-unicast network 10.42.101.0/24
set protocols bgp local-as '4200000003'
set protocols bgp neighbor 10.42.1.1 address-family ipv4-unicast soft-reconfiguration inbound
set protocols bgp neighbor 10.42.1.1 remote-as '4200000000'
set service dhcp-server shared-network-name LAB2 subnet 10.42.101.0/24 default-router '10.42.101.1'
set service dhcp-server shared-network-name LAB2 subnet 10.42.101.0/24 dns-server '1.1.1.1'
set service dhcp-server shared-network-name LAB2 subnet 10.42.101.0/24 dns-server '1.0.0.1'
set service dhcp-server shared-network-name LAB2 subnet 10.42.101.0/24 range 0 start '10.42.101.100'
set service dhcp-server shared-network-name LAB2 subnet 10.42.101.0/24 range 0 stop '10.42.101.200'
set service ssh port '22'
set system host-name 'vyoslab-lab2'
```

Если всё настроено правильно, BGP-соединения должны подняться и быть видны с `edge`. Обратите внимание на разное количество в `State/PfxRcd` у `lab1` и `lab2`. Это из-за выбранного мной способа анонсирования, упомянутого выше.

```text
vyos@vyoslab-edge:~$ show ip bgp summary

IPv4 Unicast Summary:
BGP router identifier 172.24.32.1, local AS number 4200000000 vrf-id 0
BGP table version 18
RIB entries 11, using 2112 bytes of memory
Peers 3, using 64 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
10.42.0.2       4 4200000002       131       139        0    0    0 01:22:18            2        6
10.42.1.2       4 4200000003       129       143        0    0    0 01:21:56            1        6
172.24.32.0     4 4200000001       123       122        0    0    0 01:33:50            0        6
```

И таблица маршрутизации вплоть до `vps` должна быть заполнена, и новые подсети должны пинговаться:

```text
vyos@vyoslab-edge:~$ show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

S>* 0.0.0.0/0 [1/0] via 10.21.21.1, eth0, weight 1, 01:37:31
C>* 10.21.21.0/24 is directly connected, eth0, 01:37:33
C>* 10.42.0.0/24 is directly connected, eth1, 01:37:34
C>* 10.42.1.0/24 is directly connected, eth2, 01:37:33
B>* 10.42.100.0/24 [20/0] via 10.42.0.2, eth1, weight 1, 00:04:04
B>* 10.42.101.0/24 [20/0] via 10.42.1.2, eth2, weight 1, 01:25:05
C>* 172.24.32.0/31 is directly connected, wg0, 01:37:32

------------

vyos@vyoslab-vps:~$ ping 10.42.100.1 count 1
PING 10.42.100.1 (10.42.100.1) 56(84) bytes of data.
64 bytes from 10.42.100.1: icmp_seq=1 ttl=64 time=0.264 ms

--- 10.42.100.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.264/0.264/0.264/0.000 ms

--------------

vyos@vyoslab-vps:~$ ping 10.42.101.1 count 1
PING 10.42.101.1 (10.42.101.1) 56(84) bytes of data.
64 bytes from 10.42.101.1: icmp_seq=1 ttl=64 time=10.7 ms

--- 10.42.101.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 10.711/10.711/10.711/0.000 ms
```

* * *

## Играем с клиентами

Ух… Мы добрались так далеко. Что же мы можем делать?

Для начала — пара базовых установок Ubuntu. Одна за `lab1` и одна за `lab2`:

![](/images/305953a5f93c4debedc1f27c15fcf10c.png)

Если мы сделаем traceroute с одной на другую:

```text
user@ubuntu1:~$ traceroute 10.42.101.100  <1st Ubuntu>
traceroute to 10.42.101.100 (10.42.101.100), 30 hops max, 60 byte packets
 1  _gateway (10.42.100.1)  0.192 ms  0.168 ms  0.162 ms
 2  10.42.0.1 (10.42.0.1)  0.719 ms  0.709 ms  0.704 ms
 3  10.42.1.2 (10.42.1.2)  0.769 ms  0.763 ms  0.759 ms
 4  10.42.101.100 (10.42.101.100)  1.188 ms  1.183 ms  1.177 ms  <2nd Ubuntu>
```

А что если пойти с `vps` на одну из установок Ubuntu:

```text
vyos@vyoslab-vps:~$ traceroute 10.42.101.100
traceroute to 10.42.101.100 (10.42.101.100), 30 hops max, 60 byte packets
 1  172.24.32.1 (172.24.32.1)  18.453 ms  18.367 ms  18.378 ms
 2  10.42.1.2 (10.42.1.2)  18.343 ms  18.308 ms  18.275 ms
 3  10.42.101.100 (10.42.101.100)  18.250 ms  18.211 ms  18.178 ms   <2nd Ubuntu>
```

До известного сайта:

```text
user@ubuntu1:~$ traceroute 1.1.1.1
traceroute to 1.1.1.1 (1.1.1.1), 30 hops max, 60 byte packets
 1  _gateway (10.42.100.1)  0.220 ms  0.183 ms  0.176 ms
 2  10.42.0.1 (10.42.0.1)  0.379 ms  0.372 ms  0.362 ms
 3  10.21.21.3 (10.21.21.3)  1.206 ms  1.200 ms  1.193 ms
 4  10.245.245.9 (10.245.245.9)  1.255 ms  1.249 ms  1.236 ms
 5  xxxxxxxxxxxxxxxxxxxxxxxxxxx 2.658 ms  2.651 ms  2.639 ms
 6  xxxxxxxxxxxxxxxxxxxxxxxxxxx 5.195 ms  3.781 ms  4.081 ms
 7  xxxxxxxxxxxxxxxxxxxxxxxxxxx  4.069 ms  4.646 ms  4.626 ms
 8  xxxxxxxxxxxxxxxxxxxxxxxxxxx.191 ms  4.610 ms  4.600 ms
 9  100ge15-2.core1.mci3.he.net (184.105.65.165)  8.474 ms  9.064 ms  8.443 ms
10  cloudflare.grand1.kcix.net (206.51.7.34)  9.040 ms  10.013 ms  9.385 ms
11  one.one.one.one (1.1.1.1)  9.415 ms  8.984 ms  8.106 ms
```

* * *

### Политический маршрут

Конечно, всё, что мы тут сделали, — это базовая связь между несколькими подсетями в нескольких местах. Так что добавим в смесь PBR (Policy Based Routing).

Первый шаг — убедиться, что `vps` настроен на NAT наружу. Это:

* Взять весь трафик из этой подсети
* Маскарадить его на публичный IP VPS
* `eth0` — это WAN-интерфейс VPS

```text
vyos@vyoslab-vps:~$ show configuration commands
set nat source rule 10 source address '10.42.100.0/24'
set nat source rule 10 translation address 'masquerade'
set nat source rule 10 outbound-interface 'eth0'
```

Затем на `edge` происходит вся магия. Цель — поместить весь трафик из/в подсеть `10.42.100.0/24` в отдельную таблицу маршрутизации. Так мы сможем сказать всему трафику `0.0.0.0/0` покидать этот маршрутизатор через соединение WireGuard/VPS.

* Настроить policy route. Это помещает весь трафик туда и обратно в отдельную таблицу маршрутизации `100`.
* Привязать специфичный маршрут для `0.0.0.0/0` к этой таблице и указать ему выходить через WireGuard IP `vps`.
* Разрешить весь трафик через WireGuard на этом конце. Иначе WireGuard будет блокировать трафик куда угодно.
* Прикрепить новую политику к интерфейсу, на который будет приходить трафик.

```text
vyos@vyoslab-edge:~$ show configuration commands
set policy route OUTGOING-VPS rule 100 set table '100'
set policy route OUTGOING-VPS rule 100 source address '10.42.100.0/24'
set policy route OUTGOING-VPS rule 101 destination address '10.42.100.0/24'
set policy route OUTGOING-VPS rule 101 set table '100'
set protocols static table 100 route 0.0.0.0/0 next-hop 172.24.32.0
set interfaces wireguard wg0 peer VPS-Lab allowed-ips '0.0.0.0/0'
set interfaces ethernet eth1 policy route 'OUTGOING-VPS'
```

Как только это будет сделано, вы должны выходить в веб через VPS. Обратите внимание на IP VPS в curl и кардинально другой путь по сравнению с тем, что был выше.

```text
user@ubuntu1:~$ curl ifconfig.co
144.202.75.103

user@ubuntu1:~$ traceroute 1.1.1.1
traceroute to 1.1.1.1 (1.1.1.1), 30 hops max, 60 byte packets
 1  _gateway (10.42.100.1)  0.221 ms  0.195 ms  0.189 ms
 2  10.42.0.1 (10.42.0.1)  0.421 ms  0.415 ms  0.406 ms
 3  172.24.32.0 (172.24.32.0)  19.710 ms  20.094 ms  20.088 ms
 4  * * *
 5  vl199-ds1-b5-02.05.dal4.constant.com (108.61.111.1)  23.403 ms  26.589 ms  29.625 ms
 6  * * *
 7  * * *
 8  ae-31.a01.dllstx09.us.bb.gin.ntt.net (128.241.219.53)  19.701 ms * 8-1-5.ear1.Dallas3.Level3.net (4.15.38.133)  19.719 ms
 9  ae-31.a01.dllstx09.us.bb.gin.ntt.net (128.241.219.53)  19.682 ms 8-1-5.ear1.Dallas3.Level3.net (4.15.38.133)  19.726 ms  19.721 ms
10  ae11.cr8-dal3.ip4.gtt.net (213.200.115.30)  19.877 ms ip4.gtt.net (208.116.142.210)  19.950 ms ae-6.r10.dllstx09.us.bb.gin.ntt.net (129.250.5.4)  19.623 ms
11  ip4.gtt.net (208.116.142.210)  20.130 ms  20.148 ms cloudflare-ic328260-dls-b23.ip.twelve99-cust.net (62.115.61.243)  20.989 ms
12  one.one.one.one (1.1.1.1)  19.788 ms  20.716 ms  20.428 ms
```

Когда это работает, вы можете поднять веб-сервер на этом IP и получить к нему доступ через VPS.

* * *

#### УУУУПС…

К сожалению, мы допустили ошибку. Помните это из выше?

![](/images/44002f1c89e2625fd66b41fe97c390ea.png)

Путь теперь выглядит совсем иначе:

```text
user@ubuntu1:~$ traceroute 10.42.101.100   <1st Ubuntu>
traceroute to 10.42.101.100 (10.42.101.100), 30 hops max, 60 byte packets
 1  _gateway (10.42.100.1)  0.215 ms  0.201 ms  0.196 ms
 2  10.42.0.1 (10.42.0.1)  0.357 ms  0.700 ms  0.694 ms
 3  172.24.32.0 (172.24.32.0)  19.082 ms  19.076 ms  19.142 ms
 4  172.24.32.1 (172.24.32.1)  19.135 ms  19.129 ms  19.264 ms
 5  10.42.1.2 (10.42.1.2)  19.504 ms  19.494 ms  19.488 ms
 6  10.42.101.100 (10.42.101.100)  19.717 ms  19.680 ms  19.654 ms <2nd Ubuntu>
```

Маршрутизация на основе политик создала странный путь. На деле нам повезло, что путь вообще находится.

К счастью, это легко исправить на `edge`:

* Когда трафик из нашего «перенаправленного» сети пытается попасть куда-либо в сеть `10.0.0.0/8` (ещё один сводный маршрут для сетей, которые я использую здесь и в остальной лаборатории), вернуть трафик в `main`-таблицу маршрутизации.

```text
vyos@vyoslab-edge:~$ show configuration commands
set policy route OUTGOING-VPS rule 90 destination address '10.0.0.0/8'
set policy route OUTGOING-VPS rule 90 set table 'main'
```

И снова traceroute выглядит нормально, И остальной трафик всё ещё маршрутизируется через VPS:

```text
user@ubuntu1:~$ traceroute 10.42.101.100
traceroute to 10.42.101.100 (10.42.101.100), 30 hops max, 60 byte packets
 1  _gateway (10.42.100.1)  0.286 ms  0.233 ms  0.227 ms
 2  10.42.0.1 (10.42.0.1)  0.429 ms  0.423 ms  0.413 ms
 3  10.42.1.2 (10.42.1.2)  0.732 ms  0.726 ms  0.720 ms
 4  10.42.101.100 (10.42.101.100)  0.964 ms  0.949 ms  0.937 ms

user@ubuntu1:~$ curl ifconfig.co
144.202.75.103
```

* * *

## Оговорки

Хотя в этом посте уже почти 5000 слов, я прекрасно осознаю, что он закончится с ОГРОМНЫМ количеством упущенных основ:

* В любой точке всего этого — «вставьте безопасность». Всё это широко открыто и было бы плохой идеей к внедрению без мер безопасности.
* Вам нужно было бы настроить access/as-path/communities/prefix-листы и route-maps для тонкой настройки того, что вы анонсируете и принимаете. Прямо сейчас всё построенное — в основном «анонсируй всё и принимай всё!». Это плохо во многих отношениях, и в публичном интернете это уже ломало большие части интернета, потому что какой-то сетевой инженер анонсировал или принял префикс, который не должен был.
* Всё это даже не царапает поверхность того, что может BGP. Можно строить failover и резервирование, принимать решения о маршрутизации на основе множества факторов и так далее.
* Я мог бы написать ещё 20 постов такой же или большей длины и всё равно едва продемонстрировал бы что-то сверх основ, особенно в части лучших практик (которых здесь было немного) или возможностей BGP.

* * *

## Заключение

Даже с учётом упомянутых оговорок, надеюсь, этот пост поставит некоторых на путь изучения и любви к маршрутизации. Он был долгим, но мне понравилось его вылабывать.

**********

[vyos](/tags/vyos.md)
[networking](/tags/networking.md)
[linux](/tags/linux.md)