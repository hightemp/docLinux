# Запуск контейнеров systemd-nspawn с VPN-интерфейсом

Источник: [Running systemd-nspawn containers with a VPN interface](https://blog.lieter.nl/posts/systemd-nspawn-multi-interfaces-container-wireguard/)

21 сентября 2020

Недавно был проект, в рамках которого кому-то нужно было провести измерения с использованием моей инфраструктуры (1). Им требовалась просто «машина», к которой можно подключиться через [wireguard](https://www.wireguard.com/) и у которой при этом был бы доступ в интернет. Естественно, я хотел запустить упомянутую «машину» в [`systemd-nspawn`](https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html). С помощью всего лишь нескольких строк конфигурации нескольких компонентов systemd мы можем создать контейнер, который забирает VPN-интерфейс с хоста и настраивает на нём адрес, чтобы к контейнеру можно было получить доступ через этот VPN.

Контейнер называется `ubuntu-focal-interfaces`, а интерфейс wireguard — `wg1`.

Вот шаги, необходимые для этого.

# Добавление интерфейса Wireguard на хосте с systemd-networkd

Если вы не используете [`systemd-networkd`](https://wiki.archlinux.org/index.php/Systemd-networkd) на хост-машине, просто создайте интерфейс wireguard, как описано в документации wireguard, но не назначайте IP-адрес на этот интерфейс.

`systemd-networkd` может сам создавать интерфейсы wireguard с помощью файла [`.netdev`](https://www.freedesktop.org/software/systemd/man/systemd.netdev.html#). Создайте такой файл в `/etc/systemd/network/wg1.netdev`:

```ini
[NetDev]
Name=wg1
Kind=wireguard
Description=Wireguard client interface, used in a container

[WireGuard]
# Bonus points if you actually use PrivateKeyFile
PrivateKey=XXXXXX
ListenPort=51820

[WireGuardPeer]
Endpoint=some-host.example.com:51820
PublicKey=YYYYYY
AllowedIPs=192.0.2.0/24

# Ensure the NAT knows about this connection
PersistentKeepalive=60
```

Поскольку файл содержит приватные ключи, `systemd-networkd` откажется его загружать, если права доступа слишком широкие, поэтому:

```bash
sudo chown root:systemd-network /etc/systemd/network/wg1.netdev
sudo chmod 640 /etc/systemd/network/wg1.netdev
```

Теперь создайте интерфейс:

```bash
sudo networkctl reload
```

# Создание образа

Теперь нам нужно собственно запустить контейнер, а для этого нужен образ, который nspawn сможет запустить. К счастью, [`mkosi`](https://github.com/systemd/mkosi) нам в этом поможет. Скачайте/установите его и создайте директорию, куда мы добавим конфигурацию сборки образа.

Теперь создайте файл `mkosi.default`:

```ini
[Distribution]
Distribution=ubuntu
Release=focal

[Packages]
Packages=iproute2
```

Мы запечём настройку IP-адреса на интерфейсе прямо в образ — `mkosi.postinst`:

```bash
#!/bin/bash
systemctl enable systemd-networkd
echo "[Match]
Name=wg1

[Network]
Address=192.0.2.2/24" > /etc/systemd/network/wg1.network
```

Теперь соберите образ и импортируйте его в [`machined`](https://www.freedesktop.org/software/systemd/man/systemd-machined.service.html):

```bash
chmod +x mkosi.postinst
sudo mkosi
# wait......
sudo machinectl import-raw image.raw ubuntu-focal-interfaces
```

# Добавление нужных интерфейсов в контейнер

Настройте nspawn так, чтобы он передавал интерфейс wg1 в контейнер, а также настроил veth-интерфейс. Создайте файл `/etc/systemd/nspawn/ubuntu-focal-interfaces.nspawn`:

```ini
[Network]
VirtualEthernet=true
Interface=wg1
```

# Запуск контейнера

Теперь запустите контейнер:

```bash
sudo machinectl start ubuntu-focal-interfaces
```

Если теперь выполнить `ip address show` на хосте, вы увидите, что интерфейс `wg1` исчез — он переместился в сетевое пространство имён (network namespace) контейнера.

Когда вы откроете shell в контейнере (`sudo machinectl shell ubuntu-focal-interfaces`) и выполните там `ip address show`, вы увидите два интерфейса: один veth-интерфейс с доступом в интернет и один интерфейс `wg1` с настроенным адресом.

Если остановить контейнер (`sudo machinectl stop ubuntu-focal-interfaces`), интерфейс `wg1` вернётся обратно в пространство имён хоста. Однако IP-адрес на интерфейсе после этого уже не будет настроен. Это означает, что теперь я могу спокойно сообщить людям, которым нужен доступ, публичный ключ интерфейса wireguard, запустить контейнер, установить SSH и дать им возможность делать всё, что им нужно.

# Соображения безопасности

Если у другой стороны будут права root внутри вашего контейнера, они всё равно смогут изменять параметры интерфейса wireguard. Эти изменения, конечно, будут потеряны после перезагрузки хоста, но помните об этом, перемещая интерфейсы между пространствами имён и контейнерами.

# Примечания

  1. «Инфраструктура» звучит внушительно — на самом деле всё это работало на Raspberry Pi 4, стоящем в распределительном щите моего дома и подключённом к коммутатору аплинка.

**********

[systemd](/tags/systemd.md)
[namespaces](/tags/namespaces.md)
[vpn](/tags/vpn.md)