# VPN-туннель между маршрутизаторами Cisco и VyOS с использованием VTI

Источник: [VPN tunnel between Cisco and VyOS routers using VTIs](https://dosztal.com/blog/vpn-cisco-vyos/)

Андраш Достал, сетевой архитектор · 6 ноября 2016 · 4 мин чтения


Создание VPN-туннелей между оборудованием разных вендоров обычно стоит в самом низу списка желаний сетевика, однако иногда этого не избежать. Мы подключим маршрутизатор Cisco к маршрутизатору VyOS и настроим обмен маршрутной информацией между ними с помощью OSPF.

![превью к этому посту](/images/807b8199e20f4734c5e7b47d86b3a036.png)

## Топология

Топология простая: два маршрутизатора подключены к третьему, который играет роль интернета.

### Настройка первого уровня (Layer 1)

### Настройка третьего уровня (Layer 3)

Туннель (не показан выше) находится в подсети 192.168.13.0/24; адрес .1 назначен стороне Cisco, .3 — стороне VyOS. Маршрут по умолчанию на обеих сторонах указывает в сторону Интернета.

## Конфигурация Cisco

```text
conf t

crypto isakmp policy 1
 encr aes 256
 authentication pre-share
 group 14
 hash sha256
crypto isakmp key PSK_tahp_secret address 0.0.0.0 0.0.0.0

crypto ipsec transform-set VyOS_Tset esp-sha-hmac esp-aes 256
 mode tunnel

crypto ipsec profile VyOS
 set transform-set VyOS_Tset
exit

interface Tunnel0
 ip address 192.168.13.1 255.255.255.0
 ip ospf mtu-ignore
 tunnel source 192.168.12.1
 tunnel mode ipsec ipv4
 tunnel destination 192.168.23.3
 tunnel protection ipsec profile VyOS

router ospf 1
 router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0 area 0
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.13.0 0.0.0.255 area 0
end
```

## Конфигурация VyOS

```text
set vpn ipsec esp-group ESP_to_Cisco lifetime 3600
set vpn ipsec esp-group ESP_to_Cisco mode tunnel
set vpn ipsec esp-group ESP_to_Cisco pfs dh-group 14
set vpn ipsec esp-group ESP_to_Cisco proposal 1 encryption aes256
set vpn ipsec esp-group ESP_to_Cisco proposal 1 hash sha1
set vpn ipsec ike-group IKE_to_Cisco key-exchange ikev1
set vpn ipsec ike-group IKE_to_Cisco lifetime 86400
set vpn ipsec ike-group IKE_to_Cisco proposal 1 dh-group 14
set vpn ipsec ike-group IKE_to_Cisco proposal 1 encryption aes256
set vpn ipsec ike-group IKE_to_Cisco proposal 1 hash sha256
set vpn ipsec ipsec-interfaces interface eth0
set vpn ipsec logging log-modes all
set vpn ipsec site-to-site peer 192.168.12.1 authentication id 192.168.23.3
set vpn ipsec site-to-site peer 192.168.12.1 authentication mode pre-shared-secret
set vpn ipsec site-to-site peer 192.168.12.1 authentication pre-shared-secret PSK_tahp_secret
set vpn ipsec site-to-site peer 192.168.12.1 authentication remote-id 192.168.12.1
set vpn ipsec site-to-site peer 192.168.12.1 connection-type initiate
set vpn ipsec site-to-site peer 192.168.12.1 default-esp-group ESP_to_Cisco
set vpn ipsec site-to-site peer 192.168.12.1 ike-group IKE_to_Cisco
set vpn ipsec site-to-site peer 192.168.12.1 local-address 192.168.23.3
set vpn ipsec site-to-site peer 192.168.12.1 vti bind vti0
set vpn ipsec site-to-site peer 192.168.12.1 vti esp-group ESP_to_Cisco

set interfaces vti vti0 address 192.168.13.3/24
set interfaces vti vti0 ip ospf mtu-ignore

set protocols ospf area 0 network 3.3.3.3/32
set protocols ospf area 0 network 192.168.2.0/24
set protocols ospf area 0 network 192.168.13.0/24
```

## Проверка

### Таблица маршрутизации на Cisco

```text
Cisco#sh ip route
[...]

Gateway of last resort is 192.168.12.2 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 192.168.12.2
      1.0.0.0/32 is subnetted, 1 subnets
C        1.1.1.1 is directly connected, Loopback0
      3.0.0.0/32 is subnetted, 1 subnets
O        3.3.3.3 [110/1010] via 192.168.13.3, 01:53:27, Tunnel0
      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.1.0/24 is directly connected, Ethernet0/1
L        192.168.1.1/32 is directly connected, Ethernet0/1
O     192.168.2.0/24 [110/1010] via 192.168.13.3, 01:53:27, Tunnel0
      192.168.12.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.12.0/24 is directly connected, Ethernet0/0
L        192.168.12.1/32 is directly connected, Ethernet0/0
      192.168.13.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.13.0/24 is directly connected, Tunnel0
L        192.168.13.1/32 is directly connected, Tunnel0
```

### Таблица маршрутизации в VyOS

```text
vyos@vyos:~$ sh ip route
[...]

S>* 0.0.0.0/0 [1/0] via 192.168.23.2, eth0
O>* 1.1.1.1/32 [110/11] via 192.168.13.1, vti0, 01:53:49
O   3.3.3.3/32 [110/10] is directly connected, lo, 01:54:05
C>* 3.3.3.3/32 is directly connected, lo
C>* 127.0.0.0/8 is directly connected, lo
O>* 192.168.1.0/24 [110/20] via 192.168.13.1, vti0, 01:53:49
O   192.168.2.0/24 [110/10] is directly connected, eth1, 01:54:05
C>* 192.168.2.0/24 is directly connected, eth1
O   192.168.13.0/24 [110/10] is directly connected, vti0, 01:54:04
C>* 192.168.13.0/24 is directly connected, vti0
C>* 192.168.23.0/24 is directly connected, eth0
```

### Проверка связности между ПК

```text
PC1> ping 192.168.2.10
84 bytes from 192.168.2.10 icmp_seq=1 ttl=62 time=1.557 ms
84 bytes from 192.168.2.10 icmp_seq=2 ttl=62 time=2.394 ms
84 bytes from 192.168.2.10 icmp_seq=3 ttl=62 time=3.008 ms
84 bytes from 192.168.2.10 icmp_seq=4 ttl=62 time=5.351 ms
84 bytes from 192.168.2.10 icmp_seq=5 ttl=62 time=4.107 ms

PC1> trace 192.168.2.10
trace to 192.168.2.10, 8 hops max, press Ctrl+C to stop
 1   192.168.1.1   0.316 ms  0.172 ms  0.161 ms
 2   192.168.13.3   0.971 ms  0.810 ms  0.932 ms
 3   *192.168.2.10   1.125 ms (ICMP type:3, code:3, Destination port unreachable)
```

Примечание: первые 1–2 ping-запроса могут завершиться таймаутом, поскольку туннели поднимаются в момент, когда в них попадает первый пакет.

Файлы для скачивания:

* [Конфигурации](https://drive.google.com/open?id=0B0JYNJ26TeTaV2tRU3IwZVV1NWc)

**********

[vyos](/tags/vyos.md)
[networking](/tags/networking.md)
[linux](/tags/linux.md)