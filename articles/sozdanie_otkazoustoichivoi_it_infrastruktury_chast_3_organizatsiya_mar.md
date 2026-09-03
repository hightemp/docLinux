# Создание отказоустойчивой ИТ инфраструктуры. Часть 3. Организация маршрутизации на роутерах VyOS

Источник: [Создание отказоустойчивой ИТ инфраструктуры. Часть 3. Организация маршрутизации на роутерах VyOS](https://habr.com/ru/companies/lenvendo/articles/487408/)

Основная цель статьи – показать процесс установки и настройки виртуальных маршрутизаторов VyOS на кластере oVirt, для организации связи на уровне L3 между внутренними и внешними сетями.

Также в статье будут рассмотрены вопросы, связанные с особенностями настройки выхода в Интернет через двух провайдеров, и повышения отказоустойчивости межсетевой маршрутизации.

## Вводная часть

Основываясь на двух предыдущих статьях:

  * [Создание отказоустойчивой ИТ инфраструктуры. Часть 1 — подготовка к развёртыванию кластера oVirt 4.3](https://habr.com/ru/company/lenvendo/blog/483980/)
  * [Создание отказоустойчивой ИТ инфраструктуры. Часть 2. Установка и настройка кластера oVirt 4.3](https://habr.com/ru/company/lenvendo/blog/485208/)

Мы к этому времени создали отказоустойчивый кластер oVirt, с подключенным к нему СХД для хранения виртуальных дисков ВМ. При этом все сетевые устройства и хосты коммутируются в стек из двух коммутаторов второго уровня Cisco C2960RX, на котором настроены соответствующие порты в транковом или статическом режимах, и к которым привязаны идентификаторы VLAN.

С формальной и практической точек зрения, у нас имеется полная связность на уровне L2 между устройствами и ВМ в пределах одного и тоже VLAN'а.

**VLAN** – это «виртуальная» локальная сеть, в которой все хосты взаимодействуют друг с другом в пределах одной широковещательной области (или сети). Обычно широковещательные области изолируются друг от друга с помощью VLAN, настраиваемых на портах коммутатора, хотя давным-давно сети разделяли физически, а не логически, подключая хосты из определённой группы доступа, к своим сетевым концентраторам, или хабам.

Для взаимодействия хостов из разных широковещательных областей (VLAN'ов) между собой, нам необходимо устройство, которое может соединить их на третьем уровне OSI, или по-простому – **маршрутизатор**. Это устройство, в свою очередь, также может использоваться для подключения к внешним сетям, обеспечивая выход из внутренних сетей в Интернет.

Основная наша задача – это создание отказоустойчивой ИТ инфраструктуры, в том числе и сетевой, поэтому нам потребуется связка из двух маршрутизаторов, где один маршрутизатор является ведущим, а второй ведомым. В случае выхода из строя ведущего маршрутизатора, в дело вступает ведомый, и весь трафик начинает идти через него.

Главное требование к такой схеме – она должна быть устойчивой и абсолютно прозрачной для всех сетевых потребителей, т.е. они не должны страдать от каких-либо потерь во время таких переключений, и тем более на них ничего не нужно дополнительно настраивать, кроме IP адреса, маски и шлюза по умолчанию.

В качестве маршрутизатора был выбран [VyOS](https://www.vyos.io/) версии 1.2.2, по причине уже довольно длительной эксплуатации ([в нашей организации](https://habr.com/ru/company/lenvendo/)), в ходе которой он показал себя только с положительной стороны, работая как на физических серверах, так и в виде виртуальных машин под управлением гипервизора KVM.

VyOS содержит в себе много полезного для сетевого администрирования функционала – работу с динамическими протоколами маршрутизации, VPN и IPSec туннелями, WAN load balancing, VRRP, QoS, и т.д.

В основе VyOS лежит ядро Debian, а CLI (командный интерфейс), очень напоминает таковой у Juniper, так что особой сложности у тех, кто с ним уже знаком, он не вызовет.

О наличии GUI (графической оболочки) конкретно для VyOS на сегодняшний момент ничего не известно, но работа в его консоли для любого Linux/Cisco/Juniper администратора, не должна вызывать затруднений, тем более что «под капотом» у него Debian, в котором можно при необходимости запускать знакомые системные утилиты, хотя конечно же необходимо использовать в первую очередь CLI самого VyOS.
Как вариант, если без GUI никак не обойтись, можно использовать Web GUI от роутера Vyatta, и попробовать export, а потом import конфигурации в VyOS — но такое решение на полную совместимость команд не проверялось, и неизвестно, будет ли оно работать сразу, или придётся что-то руками менять в конфиге.

Как всегда, перед началом работы с новым ПО, желательно ознакомиться с документаций на него – [VyOS User Guide](https://vyos.readthedocs.io/en/latest/index.html), чтобы дальнейшее чтение статьи прошло без сложностей. К тому же на [Habr](https://habr.com/ru/) имеется свежая обзорная [статья про VyOS](https://habr.com/ru/post/435568/), надеюсь что автор будет не против ссылки на неё :)

Дистрибутив VyOS доступен в следующих вариантах:

  * [по подписке](https://www.vyos.io/subscriptions/) – это стабильные LTS (long-term support) версии;
  * в виде [rolling releases](https://www.vyos.io/rolling-release/), выпускающихся ежедневно (использовать в production можно, но только после тщательного и длительного тестирования и конечно на свой страх и риск);
  * в виде [самостоятельно собранного](https://docs.vyos.io/en/latest/contributing/build-vyos.html#build) LTS образа VyOS из исходников.

Для ускорения процесса развёртывания маршрутизаторов, в статье будет использоваться свежий [rolling release](https://downloads.vyos.io/?dir=rolling/current/amd64) VyOS 1.2.2, как вариант можно использовать бесплатную [предыдущую LTS версию](https://downloads.vyos.io/?dir=release/legacy/1.1.8) VyOS 1.1.8.

Протоколы и технологии (применительно к VyOS), которые будут задействованы в статье:

  * [WAN load balancing](https://docs.vyos.io/en/latest/load-balancing.html)
  * [NAT](https://docs.vyos.io/en/latest/nat.html)
  * [High availability (VRRP)](https://docs.vyos.io/en/latest/high-availability.html)

Подключение датацентра к Интернет с помощью протокола [BGP](https://docs.vyos.io/en/latest/routing/bgp.html) в этой статье не рассматривается, так как у большинства организаций обычно нет такой необходимости, но при наличии технических возможностей и поддержке со стороны провайдеров, его можно без проблем реализовать.

Итак, после небольшого вступления, перейдём к основной теме статьи. Чтобы было удобно ориентироваться, приведу основные главы статьи:

  * Описание тестового стенда.
  * Подготовительные работы.
  * Начальная настройка маршрутизаторов VyOS.
  * Настройка правил на файерволе.
  * Настройка vrrp для отказоустойчивой маршрутизации.
  * Настройка выхода в Интернет через двух провайдеров.

### Описание тестового стенда

Для тестового стенда в качестве внешних IP адресов и сетей, везде указаны приватные IP адреса, что конечно же никак не меняет сути нашей задачи и правил, по которым работают протоколы маршрутизации и функционирует Интернет. Ничто не помешает затем вместо приватных адресов использовать публичные адреса, и подключить нашу инфраструктуру к сети Интернет.

Для реализации отказоустойчивого подключения к сети Интернет и внутренним сетям, будут использоваться:

  * два виртуальных маршрутизатора – **VyOS1** и **VyOS2**.
  * три виртуальных маршрутизатора с ОС CentOS 7 и пакетом [Quagga](https://quagga.net/) – **Provider-1** , **Provider-2** и **Provider-3** , для эмуляции работы сети Интернет.
  * несколько клиентских машин с ОС CentOS 7, для тестирования связности между внутренними и внешними сетями.

Все виртуальные маршрутизаторы и клиентские ВМ, будут работать на кластере **oVirt**. Это не значит, что весь тестовый стенд «заточен» именно под oVirt, его можно реализовать на чём угодно – на ВМ под управлением обычного KVM, VMware, Hyper-V, и даже на физических хостах.

Общая схема сети на уровне L3 для тестового стенда:

[![](/images/821a75370c964674eb8f32730e6ee661.png)](https://habrastorage.org/webt/se/4s/y-/se4sy-sikppg2gvv9yyzkqmqwwo.jpeg)

На этой схеме имеется несколько допущений:

  * все «публичные» сети начинаются с **172.16**.x.x, и являются по отношению к сетям в датацентре внешними, это необходимо для эмуляции работы внутренних сетей с хостами в Интернет
  * все приватные сети в датацентре начинаются с **172.20**.x.x

В составе тестового стенда будут использованы следующие сети, с соответствующими идентификаторами VLAN:

  * **VLAN17** – сеть 172.20.1.0/24, приватные адреса для хостов в датацентре (IPMI, management)
  * **VLAN30** – сеть 172.16.1.0/24, «публичная» сеть, связь между **VyOS1** , **VyOS2** и **Provider-1**
  * **VLAN31** – сеть 172.16.2.0/24, «публичная» сеть, связь между **VyOS1** , **VyOS2** и **Provider-2**
  * **VLAN32** – сеть 172.20.32.0/23, приватные адреса для хостов в датацентре – PROD
  * **VLAN36** – сеть 172.16.10.8/30, «публичная» P2P сеть, связь между роутерами **Provider-1** и **Provider-3**
  * **VLAN37** – сеть 172.16.10.12/30, «публичная» P2P сеть, связь между роутерами **Provider-2** и **Provider-3**
  * **VLAN38** – сеть 172.16.3.0/24, «публичная» сеть для внешних хостов, эмуляция Интернет
  * **VLAN40** – сеть 172.20.40.0/23, приватные адреса для хостов в датацентре – TEST

В процессе развёртывания тестового стенда, нам придётся настраивать протокол BGP на роутерах **Provider-1** , **Provider-2** и **Provider-3** , чтобы обеспечить связность между «публичными» сетями 172.16.1.0/24, 172.16.2.0/24 и 172.16.3.0/24

Задачи, которые сетевому администратору предстоит реализовать:

  * обеспечить отказоустойчивое подключение к двум независимым провайдерам, для выхода в Интернет из внутренних сетей датацентра;
  * все хосты в датацентре с адресами из приватных сетей, должны выходить в Интернет через NAT;
  * выход из строя одного из маршрутизаторов VyOS, никак не должен сказываться на доступности хостов между внутренними сетями, и на доступность выхода в Интернет.

### Подготовительные работы.

Перед развёртыванием проекта, необходимо создать 9 виртуальных машин в **oVirt** :

  * VyOS – 2 шт., ОС – последний [rolling release](https://downloads.vyos.io/?dir=rolling/current/amd64)
  * маршрутизаторы с пакетом [Quagga](https://quagga.net/) – 3 шт., ОС – CentOS 7 x86/64 1810 Minimal (можно более свежую)
  * клиентские ВМ – 4 шт., ОС – CentOS 7 x86/64 1810 Minimal (можно более свежую)

**Имена и IP адреса виртуальных машин для тестового стенда, разворачиваемых на кластере oVirt.**

  1. **test-17** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN17, IP – 172.20.1.239/24, Gateway – 172.20.1.1
```

  2. **test-IM32** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN32, IP – 172.20.32.239/23, Gateway – 172.20.32.1
```

  3. **test-IM40** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN40, IP – 172.20.40.239/23, Gateway – 172.20.40.1
```

  4. **test-public** – 1 Gb RAM, 1 CPU, 10 Gb HDD,

```text
 * VLAN38, IP – 172.16.3.2/24, Gateway – 172.16.3.1
```

  5. **PROVIDER-1** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN30, IP – 172.16.1.1/24
 * VLAN36, IP – 172.16.10.9/30
```

  6. **PROVIDER-2** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN31, IP – 172.16.2.1/24
 * VLAN37, IP – 172.16.10.13/30
```

  7. **PROVIDER-3** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * VLAN36, IP – 172.16.10.10/30
 * VLAN37, IP – 172.16.10.14/30
 * VLAN38, IP – 172.16.3.1/24
```

  8. **VyOS1** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * eth0: VLAN17, IP – 172.20.1.253/24
 * eth1: VLAN30, IP – 172.16.1.2/24
 * eth2: VLAN31, IP – 172.16.2.3/24
 * eth3: VLAN32, IP – 172.20.33.253/23
 * eth4: VLAN40, IP – 172.20.40.253/23
```

  9. **VyOS2** – 1 Gb RAM, 1 CPU, 10 Gb HDD

```text
 * eth0: VLAN17, IP – 172.20.1.254/24
 * eth1: VLAN30, IP – 172.16.1.3/24
 * eth2: VLAN31, IP – 172.16.2.2/24
 * eth3: VLAN32, IP – 172.20.33.254/23
 * eth4: VLAN40, IP – 172.20.40.254/23
```

Все необходимые идентификаторы VLAN были созданы на коммутаторах и назначены на соответствующие сетевые порты ещё в самой [первой статье](https://habr.com/ru/company/lenvendo/blog/483980/) из цикла.

Из подготовительных работ, нужно ещё сделать следующее:
**1)** Создать все используемые выше логические сети в административном портале oVirt, а затем назначить их на хосты кластера.

Делаем всё по инструкциям из [предыдущей статьи](https://habr.com/ru/company/lenvendo/blog/485208/), а также по официальной документации. Результат этой работы можно посмотреть на скриншотах, настройки сети у обоих хостов кластера должны быть идентичны:

**Скриншот логических сетей oVirt**

[![](/images/979f876e685b15ddbc3343514e33fb37.png)](https://habrastorage.org/webt/tc/fo/v7/tcfov7i3hrim00muo3etmb04dno.png)

**Скриншот логических сетей, привязанных к хосту oVirt**

[![](/images/bf9c11179e76b577f0c041709635f1cd.png)](https://habrastorage.org/webt/fp/oh/vn/fpohvnbait7-fmswegfhj_aulce.png)

**2)** Установить ОС на виртуальные маршрутизаторы с пакетом [Quagga](https://quagga.net/), а также ОС на клиентские ВМ.

После подключения ВМ к соответствующим логическим сетям, устанавливаем на них ОС, и настраиваем IP адреса и шлюзы в соответствии со списком ВМ и со схемой сети.

Добавлять установочные образы с ОС и создавать виртуальные машины мы научились в [предыдущей статье](https://habr.com/ru/company/lenvendo/blog/485208/), поэтому особых затруднений этот процесс не должен вызвать.

Дальнейшая настройка этих виртуальных машин будет выполнена далее, по ходу статьи.

### Начальная настройка маршрутизаторов VyOS.

[Официальная документация](https://vyos.readthedocs.io/en/latest/install.html) по установке VyOS, [FAQ](https://support.vyos.io/en/kb/faq).

Для установки маршрутизатора VyOs в качестве виртуальной машины под управлением oVirt:

  * скачиваем ISO с самым последним rolling release по [ссылке](https://downloads.vyos.io/rolling/current/amd64/vyos-rolling-latest.iso)
  * добавляем этот образ в oVirt
  * создаём виртуальную машину и назначаем для неё логические сети
  * назначаем первым загрузочным устройством установочный ISO образ с VyOS
  * включаем ВМ и приступаем к установке.

**Скриншоты с настройками ВМ для VyOS:**

[![](/images/b070a2b93d130434e7e1a882328c407f.png)](https://habrastorage.org/webt/9t/_p/vn/9t_pvnz8srh5i6gbj84v-yyluyc.png)
[![](/images/394134812704bfef0195d69a4030c2d4.png)](https://habrastorage.org/webt/xb/uy/wl/xbuywlw3ih0qpx38-68bafezwfu.png)
[![](/images/36718c5673928fc0fff6a71634151a29.png)
](https://habrastorage.org/webt/yw/zg/s1/ywzgs1vslq783oqresvte5igenc.png)
[![](/images/bc524413fd4468fe742df7e65501f919.png)](https://habrastorage.org/webt/2s/ek/2k/2sek2k56mfeho-4jastnb6tzvpc.png)

После включения ВМ и загрузки с ISO, заходим в консоль ВМ и вводим команду для начала установки ОС:

```text
vyos@vyos:~$ install image
```

После завершения установки ОС, отсоединяем CD от ВМ, и перезагружаем её:

```text
vyos@vyos:~$ reboot
```

_Логин и пароль по умолчанию для входа в виртуальный маршрутизатор VyOS:**vyos / vyos**
_
После перезагрузки виртуального маршрутизатора, заходим в консоль роутера (из административного портала oVirt), и проверяем образ, с которого он загрузился, и с которым мы теперь будем работать.

**Команды для просмотра загрузочного образа и его версии**

```text
vyos@VyOS1:~$ sh system image
The system currently has the following image(s) installed:
   1: 1.2-rolling-201909060337 (default boot) (running image)

vyos@VyOS1:~$ show version
Version:          VyOS 1.2-rolling-201909060337
Built by:         autobuild@vyos.net
Built on:         Fri 06 Sep 2019 03:37 UTC
Build UUID:       8b5401ba-b2eb-45d9-b267-1e3c5cfba6d7
Build Commit ID:  ad4c3805b7b9af

Architecture:     x86_64
Boot via:         installed image
System type:      KVM guest

Hardware vendor:  oVirt
Hardware model:   oVirt Node
Hardware S/N:     4c4c4544-004a-5010-804e-cac04f4e5232
Hardware UUID:    0f6dcc5e-b60b-4a47-81cc-6885339aa695

Copyright:        VyOS maintainers and contributors
```

Для входа в режим конфигурирования роутера (по аналогии с «** _configure terminal_** » для устройств Cisco), вводим команду:

```text
vyos@VyOS1:~$ configure
[edit]
vyos@VyOS1#
```

Настройка сетевых интерфейсов и других параметров маршрутизатора, может производиться только в режим конфигурирования.

Команды для просмотра сетевых интерфейсов и их настроек:

```text
show interfaces ethernet
show interfaces ethernet detail
show interfaces ethernet eth0
```

**Настройка сетевых интерфейсов на VyOS1**

Настройка сетевого интерфейса **VLAN17** :

```text
set interfaces ethernet eth0 address '172.20.1.253/24'
set interfaces ethernet eth0 description 'VLAN17'
```

Чтобы удалить IP адрес с интерфейса:

```text
delete interfaces ethernet eth0 address 172.20.1.253/24
```

Настройка сетевого интерфейса **VLAN30** :

```text
set interfaces ethernet eth1 address '172.16.1.2/24'
set interfaces ethernet eth1 description 'VLAN30'
```

Настройка сетевого интерфейса **VLAN31** :

```text
set interfaces ethernet eth2 address '172.16.2.3/24'
set interfaces ethernet eth2 description 'VLAN31'
```

Настройка сетевого интерфейса **VLAN32** :

```text
set interfaces ethernet eth3 address '172.20.33.253/23'
set interfaces ethernet eth3 description 'VLAN32'
```

Настройка сетевого интерфейса **VLAN40** :

```text
set interfaces ethernet eth4 address '172.20.40.253/23'
set interfaces ethernet eth4 description 'VLAN40'
```

**Настройка сетевых интерфейсов на VyOS2**

Настройка сетевого интерфейса **VLAN17** :

```text
set interfaces ethernet eth0 address '172.20.1.254/24'
set interfaces ethernet eth0 description 'VLAN17'
```

Настройка сетевого интерфейса **VLAN30** :

```text
set interfaces ethernet eth1 address '172.16.1.3/24'
set interfaces ethernet eth1 description 'VLAN30'
```

Настройка сетевого интерфейса **VLAN31** :

```text
set interfaces ethernet eth2 address '172.16.2.2/24'
set interfaces ethernet eth2 description 'VLAN31'
```

Настройка сетевого интерфейса **VLAN32** :

```text
set interfaces ethernet eth3 address '172.20.33.254/23'
set interfaces ethernet eth3 description 'VLAN32'
```

Настройка сетевого интерфейса **VLAN40** :

```text
set interfaces ethernet eth4 address '172.20.40.254/23'
set interfaces ethernet eth4 description 'VLAN40'
```

**Дополнительные настройки на обоих маршрутизаторах**

Включение SSH для удалённого управления маршрутизатором

```text
set service ssh port 22
```

Настройка DNS forwarder для разрешения внешних имён с роутера

```text
set system name-server 1.1.1.1
set system name-server 8.8.8.8
```

Настройка имени роутера и уровня логирования

```text
set system host-name VyOS1
set system syslog global facility all level 'notice'
```

Добавление ключа SSH для аутентификации пользователя на роутере

```text
set system login user vyos authentication public-keys 'vyos' key "very_very_very_long_key"
set system login user vyos authentication public-keys 'vyos' type ssh-rsa
```

Настройка ntp сервера и временной зоны

```text
set system ntp server 0.pool.ntp.org
set system ntp server 1.pool.ntp.org
set system ntp server 2.pool.ntp.org
set system time-zone Europe/Moscow
date
```

Ускорение медленной работы по SSH (если нет доступа к DNS серверам)

```text
edit service ssh disable-host-validation
```

Для сохранения всех сделанных изменений, выполняем команды

```text
commit
save
```

Для отказа от всех сделанных изменений, выполняем команду

```text
discard
```

Приведённые выше настройки, являются минимально достаточными для начала работы с VyOS через SSH, с аутентификацией по паролю или SSH ключу.

Помимо этих базовых настроек, существует ещё множество других, которые могут пригодиться при дальнейшей работе с VyOS, например, для:

  * настройки SNMP для мониторинга параметров маршрутизатора, к примеру, в небезызвестном [Zabbix](https://www.zabbix.com/);
  * настройки роутера для автоматической выгрузки на tftp сервер всех изменений в конфигурации, после каждого commit'а и мониторинга факта таких изменений в [Zabbix](https://www.zabbix.com/);
  * настройки резервного копирования конфигурационного файла VyOS на tftp сервер по расписанию;
  * и т.п.

Все дополнительные настройки в рамках этой статьи описать нереально, так как потребуется ещё добавлять информацию о шаблонах и параметрах системы мониторинга [Zabbix](https://www.zabbix.com/), поэтому их внедрение и использование может быть темой одной из будущих статей.

### Настройка правил на файерволе.

Ссылка на документацию – [Firewall](https://docs.vyos.io/en/latest/firewall.html).
VyOS использует для фильтрации сетевых пакетов [netfilter](https://netfilter.org/).

Политика для файервола в VyOS может применяться двумя способами:

  * политика, применяемая к интерфейсу (**Per-Interface**)
  * политика зоны (**Zone Policy**).

В статье будет использоваться политика, применяемая к интерфейсу.

Политика для файервола управляется через наборы правил – это раздельные группы правил, пронумерованные от 1 до 9999. Правила выполняются последовательно, в соответствии с номером правила. Если трафик соответствует правилу, действие правила выполняется; если нет, то система переходит к следующему правилу.

Правила выполняют следующие действия:

  * Accept – означает, что трафик разрешается
  * Drop – означает, что трафик молча отбрасывается
  * Reject – означает, что трафик отбрасывается с сообщением «ICMP Port Unreachable».

Наборы правил обычно применяются к интерфейсу, или к нескольким интерфейсам, в следующих направлениях:

  * **входящий трафик** (или **in**)
Соответствует входящему интерфейсу цепочки FORWARD (netfilter), файервол фильтрует пакеты, которые входят в интерфейс и проходят через VyOS. Можно применить только один входной фильтр пакетов на интерфейс.
  * **исходящий трафик** (или **out**)
Соответствует исходящему интерфейсу цепочки FORWARD (netfilter), файервол фильтрует пакеты, которые покидают интерфейс. Это могут быть как пакеты, проходящие через VyOS, так и созданные на нём самом. Можно применить только один выходной фильтр пакетов на интерфейс.
  * **локальный трафик** (или **local**)
Соответствует цепочке INPUT (netfilter), т.е. трафик, который направляется на сам маршрутизатор VyOS, например, на 22 порт слушающий на его внешнем или внутреннем интерфейсе.

Пример настроек правил:

```text
set firewall name OUTSIDE-IN default-action 'drop'
set firewall name OUTSIDE-IN rule 10 action 'allow'
set firewall name OUTSIDE-IN rule 10 state established 'enable'
set firewall name OUTSIDE-IN rule 10 state related 'enable'
```

Строка 1 – создает политику файервола с именем «OUTSIDE-IN» для блокировки трафика по умолчанию.
Строка 2 – создает правило файервола (#10), которое разрешает трафик, соответствующий правилу.
Строка 3 – указывает, что правило применимо, когда существует установленный сеанс для трафика.
Строка 4 – указывает, что правило применимо, когда трафик относится к этому соединению.

Пример настройки файервола для блокировки трафика, направленного на сам маршрутизатор:

```text
set firewall name OUTSIDE-LOCAL default-action 'drop'
```

В этом примере весь трафик отбрасывается по умолчанию.

Пример применения правил для файервола к интерфейсам, в нужных направлениях:

```text
set interfaces ethernet eth0 firewall in name 'OUTSIDE-IN'
set interfaces ethernet eth1 firewall local name 'OUTSIDE-LOCAL'
```

Строка 1 – привязка политики файервола «OUTSIDE-IN» к интерфейсу eth0, для входящего трафика с внутренних адресов.
Строка 2 – привязка политики файервола «OUTSIDE-LOCAL» к интерфейсу eth1, для трафика, направляемого на сам маршрутизатор.

**Настройка локальных правил файервола**

Переходим к настройке локальных правил файервола (для трафика, направляемого на сам маршрутизатор).

Основные правила, которые будут использоваться:

  * принимаем трафик, относящийся к установленному соединению (established, related), отбрасываем неправильный трафик
  * Принимаем ICMP echo-request (ping)
  * Принимаем запросы DHCP
  * Принимаем запросы DNS
  * Ограничиваем соединения по SSH до 4 в минуту на IP адрес и принимаем их только из определённых внутренних сетей (management)
  * Принимаем подключения SNMP только из определённых внутренних сетей (management)

**Настройка локальных правил**

  * Создаём групповые объекты с внутренними сетями

```text
    set firewall group network-group NET-VLAN17 network '172.20.1.0/24'
    set firewall group network-group NET-VLAN30 network '172.16.1.0/24'
    set firewall group network-group NET-VLAN31 network '172.16.2.0/24'
    set firewall group network-group NET-VLAN32 network '172.20.32.0/23'
    set firewall group network-group NET-VLAN38 network '172.16.3.0/24'
    set firewall group network-group NET-VLAN40 network '172.20.40.0/23'
    set firewall group network-group NET-MANAGEMENT network '172.20.32.0/23'
    set firewall group network-group NET-MANAGEMENT network '172.20.1.0/24'
```

  * Создаём именную локальную политику для каждой сети, или интерфейса, подключенного к маршрутизатору.

```text
    set firewall name LOCAL-VLAN30 default-action 'drop'
    set firewall name LOCAL-VLAN30 rule 1010 action 'accept'
    set firewall name LOCAL-VLAN30 rule 1010 state established 'enable'
    set firewall name LOCAL-VLAN30 rule 1010 state related 'enable'
    set firewall name LOCAL-VLAN30 rule 1011 action 'drop'
    set firewall name LOCAL-VLAN30 rule 1011 state invalid 'enable'
    set firewall name LOCAL-VLAN30 rule 1020 action 'accept'
    set firewall name LOCAL-VLAN30 rule 1020 icmp type-name 'echo-request'
    set firewall name LOCAL-VLAN30 rule 1020 protocol 'icmp'
    set firewall name LOCAL-VLAN30 rule 1020 state new 'enable'
    set firewall name LOCAL-VLAN30 rule 1030 action 'drop'
    set firewall name LOCAL-VLAN30 rule 1030 destination port '22'
    set firewall name LOCAL-VLAN30 rule 1030 protocol 'tcp'
    set firewall name LOCAL-VLAN30 rule 1030 recent count '4'
    set firewall name LOCAL-VLAN30 rule 1030 recent time '60'
    set firewall name LOCAL-VLAN30 rule 1030 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN30 rule 1030 state new 'enable'
    set firewall name LOCAL-VLAN30 rule 1040 action 'accept'
    set firewall name LOCAL-VLAN30 rule 1040 destination port '22'
    set firewall name LOCAL-VLAN30 rule 1040 protocol 'tcp'
    set firewall name LOCAL-VLAN30 rule 1040 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN30 rule 1040 state new 'enable'

    set firewall name LOCAL-VLAN31 default-action 'drop'
    set firewall name LOCAL-VLAN31 rule 1010 action 'accept'
    set firewall name LOCAL-VLAN31 rule 1010 state established 'enable'
    set firewall name LOCAL-VLAN31 rule 1010 state related 'enable'
    set firewall name LOCAL-VLAN31 rule 1011 action 'drop'
    set firewall name LOCAL-VLAN31 rule 1011 state invalid 'enable'
    set firewall name LOCAL-VLAN31 rule 1020 action 'accept'
    set firewall name LOCAL-VLAN31 rule 1020 icmp type-name 'echo-request'
    set firewall name LOCAL-VLAN31 rule 1020 protocol 'icmp'
    set firewall name LOCAL-VLAN31 rule 1020 state new 'enable'
    set firewall name LOCAL-VLAN31 rule 1030 action 'drop'
    set firewall name LOCAL-VLAN31 rule 1030 destination port '22'
    set firewall name LOCAL-VLAN31 rule 1030 protocol 'tcp'
    set firewall name LOCAL-VLAN31 rule 1030 recent count '4'
    set firewall name LOCAL-VLAN31 rule 1030 recent time '60'
    set firewall name LOCAL-VLAN31 rule 1030 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN31 rule 1030 state new 'enable'
    set firewall name LOCAL-VLAN31 rule 1040 action 'accept'
    set firewall name LOCAL-VLAN31 rule 1040 destination port '22'
    set firewall name LOCAL-VLAN31 rule 1040 protocol 'tcp'
    set firewall name LOCAL-VLAN31 rule 1040 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN31 rule 1040 state new 'enable'

    set firewall name LOCAL-VLAN17 default-action 'drop'
    set firewall name LOCAL-VLAN17 rule 1001 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1001 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN17 rule 1010 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1010 state established 'enable'
    set firewall name LOCAL-VLAN17 rule 1010 state related 'enable'
    set firewall name LOCAL-VLAN17 rule 1011 action 'drop'
    set firewall name LOCAL-VLAN17 rule 1011 state invalid 'enable'
    set firewall name LOCAL-VLAN17 rule 1020 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1020 icmp type-name 'echo-request'
    set firewall name LOCAL-VLAN17 rule 1020 protocol 'icmp'
    set firewall name LOCAL-VLAN17 rule 1020 state new 'enable'
    set firewall name LOCAL-VLAN17 rule 1040 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1040 destination port '53'
    set firewall name LOCAL-VLAN17 rule 1040 protocol 'tcp_udp'
    set firewall name LOCAL-VLAN17 rule 1040 state new 'enable'
    set firewall name LOCAL-VLAN17 rule 1100 action 'drop'
    set firewall name LOCAL-VLAN17 rule 1100 destination port '22'
    set firewall name LOCAL-VLAN17 rule 1100 protocol 'tcp'
    set firewall name LOCAL-VLAN17 rule 1100 recent count '4'
    set firewall name LOCAL-VLAN17 rule 1100 recent time '60'
    set firewall name LOCAL-VLAN17 rule 1100 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN17 rule 1100 state new 'enable'
    set firewall name LOCAL-VLAN17 rule 1101 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1101 destination port '22'
    set firewall name LOCAL-VLAN17 rule 1101 protocol 'tcp'
    set firewall name LOCAL-VLAN17 rule 1101 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN17 rule 1101 state new 'enable'
    set firewall name LOCAL-VLAN17 rule 1110 action 'accept'
    set firewall name LOCAL-VLAN17 rule 1110 destination port '161'
    set firewall name LOCAL-VLAN17 rule 1110 protocol 'udp'
    set firewall name LOCAL-VLAN17 rule 1110 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN17 rule 1110 state new 'enable'

    set firewall name LOCAL-VLAN32 default-action 'drop'
    set firewall name LOCAL-VLAN32 rule 1010 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1010 state established 'enable'
    set firewall name LOCAL-VLAN32 rule 1010 state related 'enable'
    set firewall name LOCAL-VLAN32 rule 1011 action 'drop'
    set firewall name LOCAL-VLAN32 rule 1011 state invalid 'enable'
    set firewall name LOCAL-VLAN32 rule 1020 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1020 icmp type-name 'echo-request'
    set firewall name LOCAL-VLAN32 rule 1020 protocol 'icmp'
    set firewall name LOCAL-VLAN32 rule 1020 state new 'enable'
    set firewall name LOCAL-VLAN32 rule 1030 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1030 destination port '67'
    set firewall name LOCAL-VLAN32 rule 1030 protocol 'udp'
    set firewall name LOCAL-VLAN32 rule 1030 state new 'enable'
    set firewall name LOCAL-VLAN32 rule 1040 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1040 destination port '53'
    set firewall name LOCAL-VLAN32 rule 1040 protocol 'tcp_udp'
    set firewall name LOCAL-VLAN32 rule 1040 state new 'enable'
    set firewall name LOCAL-VLAN32 rule 1100 action 'drop'
    set firewall name LOCAL-VLAN32 rule 1100 destination port '22'
    set firewall name LOCAL-VLAN32 rule 1100 protocol 'tcp'
    set firewall name LOCAL-VLAN32 rule 1100 recent count '4'
    set firewall name LOCAL-VLAN32 rule 1100 recent time '60'
    set firewall name LOCAL-VLAN32 rule 1100 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN32 rule 1100 state new 'enable'
    set firewall name LOCAL-VLAN32 rule 1101 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1101 destination port '22'
    set firewall name LOCAL-VLAN32 rule 1101 protocol 'tcp'
    set firewall name LOCAL-VLAN32 rule 1101 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN32 rule 1101 state new 'enable'
    set firewall name LOCAL-VLAN32 rule 1110 action 'accept'
    set firewall name LOCAL-VLAN32 rule 1110 destination port '161'
    set firewall name LOCAL-VLAN32 rule 1110 protocol 'udp'
    set firewall name LOCAL-VLAN32 rule 1110 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN32 rule 1110 state new 'enable'

    set firewall name LOCAL-VLAN40 default-action 'drop'
    set firewall name LOCAL-VLAN40 rule 1001 action 'accept'
    set firewall name LOCAL-VLAN40 rule 1001 source group network-group 'NET-MANAGEMENT'
    set firewall name LOCAL-VLAN40 rule 1010 action 'accept'
    set firewall name LOCAL-VLAN40 rule 1010 state established 'enable'
    set firewall name LOCAL-VLAN40 rule 1010 state related 'enable'
    set firewall name LOCAL-VLAN40 rule 1011 action 'drop'
    set firewall name LOCAL-VLAN40 rule 1011 state invalid 'enable'
    set firewall name LOCAL-VLAN40 rule 1020 action 'accept'
    set firewall name LOCAL-VLAN40 rule 1020 icmp type-name 'echo-request'
    set firewall name LOCAL-VLAN40 rule 1020 protocol 'icmp'
    set firewall name LOCAL-VLAN40 rule 1020 state new 'enable'
```

  * Применяем локальную политику к интерфейсам на **VyOS1** и **VyOS2**

```text
    set interfaces ethernet eth0 firewall local name 'LOCAL-VLAN17'
    set interfaces ethernet eth1 firewall local name 'LOCAL-VLAN30'
    set interfaces ethernet eth2 firewall local name 'LOCAL-VLAN31'
    set interfaces ethernet eth3 firewall local name 'LOCAL-VLAN32'
    set interfaces ethernet eth4 firewall local name 'LOCAL-VLAN40'
```

**Настройка правил файервола между защищаемыми внутренними сетями**

Создаём политику для входящего трафика из сетей **VLAN32** и **VLAN17** – политика, которая устанавливается для трафика, который входит на интерфейс из локальной сети, защищаемой файерволом, с последующим его транзитом к другим сетям (снаружи, или защищаемым этим же файерволом).

С целью упрощения конфигурации тестового стенда и диагностики сети, политики для сетей **VLAN30** , **VLAN31** и **VLAN40** настраивать не будем, но можете создать правила для них самостоятельно.
Помните, что в производственной среде, отсутствие политики файервола на внешнем интерфейсе недопустимо!

_Важное примечание_
Все наборы политик для файервола, описанные в этой статье, даны для случаев обычной маршрутизации. Для случаев асимметричной маршрутизации (asymmetric routing), правила будут выглядеть немного по-другому, без поддержки SPI (stateful packet inspection).

**Настройка правил фильтрации межсетевого трафика**

  * Создаём политики для входящего трафика из сетей VLAN32 и VLAN17 к другим сетям

```text
    set firewall name VLAN32-IN default-action 'drop'
    set firewall name VLAN32-IN rule 1010 action 'accept'
    set firewall name VLAN32-IN rule 1010 state established 'enable'
    set firewall name VLAN32-IN rule 1010 state related 'enable'
    set firewall name VLAN32-IN rule 1011 action 'drop'
    set firewall name VLAN32-IN rule 1011 state invalid 'enable'
    set firewall name VLAN32-IN rule 9000 action 'accept'
    set firewall name VLAN32-IN rule 9000 source group network-group 'NET-VLAN32'
    set firewall name VLAN32-IN rule 9000 state new 'enable'

    set firewall name VLAN17-IN default-action 'drop'
    set firewall name VLAN17-IN rule 1010 action 'accept'
    set firewall name VLAN17-IN rule 1010 state established 'enable'
    set firewall name VLAN17-IN rule 1010 state related 'enable'
    set firewall name VLAN17-IN rule 1011 action 'drop'
    set firewall name VLAN17-IN rule 1011 state invalid 'enable'
    set firewall name VLAN17-IN rule 9000 action 'accept'
    set firewall name VLAN17-IN rule 9000 source group network-group 'NET-VLAN17'
    set firewall name VLAN17-IN rule 9000 state new 'enable'
```

  * Применяем политики для входящего трафика, к соответствующим интерфейсам

```text
    set interfaces ethernet eth0 firewall in name 'VLAN17-IN'
    set interfaces ethernet eth2 firewall in name 'VLAN32-IN'
```

  * Создаём политики для исходящего трафика из других сетей, к сетям VLAN32 и VLAN17, т.е. выходящего из интерфейса файервола в защищаемую локальную сеть.

```text
    set firewall name VLAN32-OUT default-action 'drop'
    set firewall name VLAN32-OUT rule 1010 action 'accept'
    set firewall name VLAN32-OUT rule 1010 state established 'enable'
    set firewall name VLAN32-OUT rule 1010 state related 'enable'
    set firewall name VLAN32-OUT rule 1011 action 'drop'
    set firewall name VLAN32-OUT rule 1011 state invalid 'enable'
    set firewall name VLAN32-OUT rule 1020 action 'accept'
    set firewall name VLAN32-OUT rule 1020 icmp type-name 'echo-request'
    set firewall name VLAN32-OUT rule 1020 protocol 'icmp'
    set firewall name VLAN32-OUT rule 1020 state new 'enable'
    set firewall name VLAN32-OUT rule 1100 action 'accept'
    set firewall name VLAN32-OUT rule 1100 source group network-group 'NET-VLAN40'
    set firewall name VLAN32-OUT rule 1100 state new 'enable'
    set firewall name VLAN32-OUT rule 1110 action 'accept'
    set firewall name VLAN32-OUT rule 1110 source group network-group 'NET-VLAN17'
    set firewall name VLAN32-OUT rule 1110 state new 'enable'
    set firewall name VLAN32-OUT rule 1120 action 'accept'
    set firewall name VLAN32-OUT rule 1120 source group network-group 'NET-VLAN30'
    set firewall name VLAN32-OUT rule 1120 state new 'enable'
    set firewall name VLAN32-OUT rule 1130 action 'accept'
    set firewall name VLAN32-OUT rule 1130 source group network-group 'NET-VLAN31'
    set firewall name VLAN32-OUT rule 1130 state new 'enable'
    set firewall name VLAN32-OUT rule 1140 action 'accept'
    set firewall name VLAN32-OUT rule 1140 source group network-group 'NET-VLAN38'
    set firewall name VLAN32-OUT rule 1140 state new 'enable'

    set firewall name VLAN17-OUT default-action 'drop'
    set firewall name VLAN17-OUT rule 1010 action 'accept'
    set firewall name VLAN17-OUT rule 1010 state established 'enable'
    set firewall name VLAN17-OUT rule 1010 state related 'enable'
    set firewall name VLAN17-OUT rule 1011 action 'drop'
    set firewall name VLAN17-OUT rule 1011 state invalid 'enable'
    set firewall name VLAN17-OUT rule 1020 action 'accept'
    set firewall name VLAN17-OUT rule 1020 icmp type-name 'echo-request'
    set firewall name VLAN17-OUT rule 1020 protocol 'icmp'
    set firewall name VLAN17-OUT rule 1020 state new 'enable'
    set firewall name VLAN17-OUT rule 1100 action 'accept'
    set firewall name VLAN17-OUT rule 1100 source group network-group 'NET-VLAN32'
    set firewall name VLAN17-OUT rule 1100 state new 'enable'
```

  * Применяем политики для исходящего трафика, к соответствующим интерфейсам

```text
    set interfaces ethernet eth0 firewall out name 'VLAN17-OUT'
    set interfaces ethernet eth3 firewall out name 'VLAN32-OUT'
```

Не забываем, что после создания политик, и их применения к интерфейсам, нужно сделать **_commit_** и **_save_**.

**Настройка дополнительных параметров файервола VyOS**

  * включаем логирование по snmp изменений в конфигурации файервола

```text
    set firewall config-trap 'enable'
```

  * логируем трафик, который доходит до правила по умолчанию для именованной политики (в нашем случае это _default drop_)

```text
    set firewall name VLAN17-IN 'enable-default-log'
    set firewall name VLAN17-OUT 'enable-default-log'
    set firewall name VLAN32-IN 'enable-default-log'
    set firewall name VLAN32-OUT 'enable-default-log'
```

  * пример, как это работает, когда нужно поймать отбрасываемый трафик:

```text
    set firewall name VLAN17-LOCAL 'enable-default-log'
    commit
    exit
    show log firewall name VLAN17-LOCAL
    configure
    delete firewall name VLAN17-LOCAL 'enable-default-log'
    commit
```

  * включаем глобальные настройки файервола, обычно настроенные по умолчанию

```text
    set firewall all-ping 'enable'
    set firewall broadcast-ping 'disable'
    set firewall config-trap 'disable'
    set firewall log-martians 'enable'
    set firewall receive-redirects 'disable'
    set firewall source-validation 'disable'
    set firewall syn-cookies 'enable'
    set firewall send-redirects 'enable'
    set firewall ipv6-receive-redirects 'disable'
    set firewall ipv6-src-route 'disable'
    set firewall ip-src-route 'disable'
```

### Настройка vrrp для отказоустойчивой маршрутизации

Ссылка на документацию – [High availability (VRRP)](https://docs.vyos.io/en/latest/high-availability.html).

После выполнения базовых настроек маршрутизаторов VyOS, перейдём к настройке отказоустойчивой связи между хостами во внутренних сетях и их шлюзами по умолчанию.
Достигается это с помощью протокола [vrrp](https://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol), настраиваемого на обоих маршрутизаторах, в результате чего появляется виртуальный высокодоступный IP адрес — HAIP (Highly Available IP), являющийся шлюзом по умолчанию для внутренней сети. Этот адрес активируется на ведущем роутере, и через него идёт обмен трафиком между подключенной к нему какой-либо внутренней сетью, с остальными внутренними или внешними сетями. В случае сбоя ведущего роутера, этот HAIP автоматически переключается на ведомый (резервный) роутер, и трафик начинает идти через него.

Если вы когда-либо использовали HAIP, настраиваемый в [keepalived](https://www.keepalived.org/index.html), то это практически тоже самое, но ещё интересным и полезным может отказаться тот факт, что такая связка вполне работает между VyOS и обычным хостом с Linux, на котором настроен HAIP и keepalived (конечно же с идентичными настройками). Такая возможность может пригодиться при каких-то миграциях, или при отладке конфигурации на роутере или другом устройстве.

Для более глубокого погружения в детали настроек vrrp, рекомендуется [статья от IBM](https://cloud.ibm.com/docs/infrastructure/virtual-router-appliance?topic=virtual-router-appliance-working-with-high-availability-and-vrrp), она относится к виртуальному маршрутизатору [Vyatta 5600](http://brocade.ocs.ru/products/vse/nfv/virtualizatsiya-seti/brocade-vyatta-5600-vrouter) от Brocade, но нам подойдёт, так как корни VyOS растут из проекта Vyatta (который в 2012 году был перекуплен Brocade).

**Список HAIP, использующихся в качестве шлюзов по умолчанию для внутренних сетей:**

**VLAN17** , HA VIP – 172.20.1.1/24

```text
Ведущий хост – 172.20.1.253/24
Резервный хост – 172.20.1.254/24
```

**VLAN32** , HA VIP – 172.20.32.1/23

```text
Ведущий хост – 172.20.33.253/23
Резервный хост – 172.20.33.254/23
```

**VLAN40** , HA VIP – 172.20.40.1/23

```text
Ведущий хост – 172.20.40.253/23
Резервный хост – 172.20.40.254/23
```

**Настройка локальных политик безопасности на роутерах VyOS1 и VyOS2**

```text
set firewall name LOCAL-VLAN32 rule 1120 action 'accept'
set firewall name LOCAL-VLAN32 rule 1120 protocol 'vrrp'

set firewall name LOCAL-VLAN17 rule 1120 action 'accept'
set firewall name LOCAL-VLAN17 rule 1120 protocol 'vrrp'

set firewall name LOCAL-VLAN40 rule 1030 action 'accept'
set firewall name LOCAL-VLAN40 rule 1030 protocol 'vrrp'
```

**Настройка vrrp для роутера VyOS1**

```text
set high-availability vrrp group haip-1 vrid 17
set high-availability vrrp group haip-1 interface eth0
set high-availability vrrp group haip-1 virtual-address 172.20.1.1/24
set high-availability vrrp group haip-1 priority '200'
set high-availability vrrp group haip-1 authentication type 'plaintext-password'
set high-availability vrrp group haip-1 authentication password 'b65495f9'
set high-availability vrrp group haip-1 preempt 2
set high-availability vrrp group haip-1 advertise-interval '1'

set high-availability vrrp group haip-2 vrid 32
set high-availability vrrp group haip-2 interface eth3
set high-availability vrrp group haip-2 virtual-address 172.20.32.1/23
set high-availability vrrp group haip-2 priority '200'
set high-availability vrrp group haip-2 authentication type 'plaintext-password'
set high-availability vrrp group haip-2 authentication password 'b65495f9'
set high-availability vrrp group haip-2 preempt 2
set high-availability vrrp group haip-2 advertise-interval '1'

set high-availability vrrp group haip-3 vrid 40
set high-availability vrrp group haip-3 interface eth4
set high-availability vrrp group haip-3 virtual-address 172.20.40.1/23
set high-availability vrrp group haip-3 priority '200'
set high-availability vrrp group haip-3 authentication type 'plaintext-password'
set high-availability vrrp group haip-3 authentication password 'b65495f9'
set high-availability vrrp group haip-3 preempt 2
set high-availability vrrp group haip-3 advertise-interval '1'
commit
```

**Настройка vrrp для роутера VyOS2**

```text
set high-availability vrrp group haip-1 vrid 17
set high-availability vrrp group haip-1 interface eth0
set high-availability vrrp group haip-1 virtual-address 172.20.1.1/24
set high-availability vrrp group haip-1 priority '199'
set high-availability vrrp group haip-1 authentication type 'plaintext-password'
set high-availability vrrp group haip-1 authentication password 'b65495f9'
set high-availability vrrp group haip-1 preempt 2
set high-availability vrrp group haip-1 advertise-interval '1'

set high-availability vrrp group haip-2 vrid 32
set high-availability vrrp group haip-2 interface eth3
set high-availability vrrp group haip-2 virtual-address 172.20.32.1/23
set high-availability vrrp group haip-2 priority '199'
set high-availability vrrp group haip-2 authentication type 'plaintext-password'
set high-availability vrrp group haip-2 authentication password 'b65495f9'
set high-availability vrrp group haip-2 preempt 2
set high-availability vrrp group haip-2 advertise-interval '1'

set high-availability vrrp group haip-3 vrid 40
set high-availability vrrp group haip-3 interface eth4
set high-availability vrrp group haip-3 virtual-address 172.20.40.1/23
set high-availability vrrp group haip-3 priority '199'
set high-availability vrrp group haip-3 authentication type 'plaintext-password'
set high-availability vrrp group haip-3 authentication password 'b65495f9'
set high-availability vrrp group haip-3 preempt 2
set high-availability vrrp group haip-3 advertise-interval '1'
commit
```

Команды для просмотра информации о работе vrrp:

```text
run show vrrp statistics
run show vrrp detail
run show log all
```

**Пример работы vrrp:**

```text
vyos@VyOS1# run show vrrp
Name    Interface      VRID  State    Last Transition
------  -----------  ------  -------  -----------------
haip-1  eth0            17   MASTER   13m48s
haip-2  eth3            32   MASTER   13m48s
haip-3  eth4            40   MASTER   13m48s

vyos@VyOS2# run show vrrp
Name    Interface      VRID  State    Last Transition
------  -----------  ------  -------  -----------------
haip-1  eth0            17    BACKUP   11m26s
haip-2  eth3            32    BACKUP   11m27s
haip-3  eth4            40    BACKUP   5m17s
```

**Проверка работы vrrp**

  * на роутере **VyOS1**

```text
    set high-availability vrrp group haip-1 disable
    set high-availability vrrp group haip-2 disable
    set high-availability vrrp group haip-3 disable
    commit
    run show vrrp
```

  * проверяем видимость тестовых хостов **test-17** , **test-IM3** и **test-IM40** друг с друга, на них шлюзом должен быть настроен соответствующий HAIP:

```text
    ping 172.20.32.239
    ping 172.20.1.239
    ping 172.20.40.239
```

  * после всех проверок, на роутере **VyOS1** включаем vrrp обратно:

```text
    delete high-availability vrrp group haip-1 disable
    delete high-availability vrrp group haip-2 disable
    delete high-availability vrrp group haip-3 disable
    commit
    run show vrrp
```

### Настройка выхода в Интернет через двух провайдеров.

Официальная документация – [WAN load balancing](https://docs.vyos.io/en/latest/load-balancing.html).

Балансировка исходящего трафика из датацентра к внешним сетям (в Интернет), может производиться между двумя и более внешними интерфейсами, понятно, что для этого датацентр должен быть подключен как минимум к двум независимым провайдерам.
В случае потери доступа к кому-либо из провайдеров, происходит балансировка трафика между оставшимися рабочими линиями связи, а после восстановления работоспособности канала, ранее сбоивший маршрут автоматически добавляется обратно в таблицу маршрутизации, для его дальнейшего использования балансировщиком. Балансировщик автоматически добавляет маршруты для каждого внешнего интерфейса в таблицу маршрутизации и балансирует трафик между ними, в зависимости от их состояния и веса.

Наша задача состоит в том, чтобы обеспечить выход в Интернет одновременно через двух провайдеров (балансировку нагрузки), для хостов из внутренних сетей: VLAN17, VLAN32 и VLAN40.

Установку и настройку IP адресов на «внешних» (провайдерских) роутерах, мы должны были выполнить ещё в самом начале, сейчас нам нужно будет настроить между ними маршрутизацию с помощью протокола BGPv4 и сервиса **bgpd** , являющегося составной частью пакета [Quagga](https://quagga.net/).

Установка пакета [Quagga](https://quagga.net/) делается относительно просто, а управление ею производится через CLI, вызываемый командой **_vtysh_**. Сам CLI довольно простой, и если сетевой администратор уже знаком с маршрутизаторами Cisco, то никаких проблем он не вызовет.

Безусловно, правильнее было бы на «внешних» (провайдерских) роутерах тоже установить VyOS и настраивать BGP на них, но целью статьи это не является, чтобы не перегружать читателей лишней информацией. Показать, как на VyOS настраивается BGP и политики маршрутизации, это возможная тема одной из следующих статей, поэтому в целях экономии времени и упрощения настройки тестового стенда, используется самый обычный CentOS и Quagga.

**Установка Quagga и настройка BGP на «внешних» (провайдерских) маршрутизаторах**

  * Установка пакета Quagga:

```text
    yum install -y quagga
    systemctl enable zebra && systemctl start zebra && systemctl status zebra
    cp /usr/share/doc/quagga-0.99.22.4/bgpd.conf.sample /etc/quagga/bgpd.conf
    systemctl start bgpd && systemctl enable bgpd && systemctl status bgpd
    chmod -R 777 /etc/quagga/
    vtysh
    show running-config
    config t
```

  * Настройка BGP на маршрутизаторе **Provider-1**

```text
    Provider-1# sh running-config
    Building configuration...
    Current configuration:
    !
    hostname Provider-1
    log file /var/log/quagga/quagga.log
    hostname bgpd
    log stdout
    !
    password zebra
    !
    interface eth0
    ipv6 nd suppress-ra
    !
    interface eth1
    ipv6 nd suppress-ra
    !
    interface lo
    !
    router bgp 65860
    bgp router-id 172.16.10.9
    network 172.16.1.0/24
    neighbor 172.16.10.10 remote-as 65880
    neighbor 172.16.10.10 description "Provider-3"
    neighbor 172.16.10.10 timers 30 90
    neighbor 172.16.10.10 soft-reconfiguration inbound
    !
    ip forwarding
    !
    line vty
    !
    end
```

  * Настройка BGP на маршрутизаторе **Provider-2**

```text
    Provider-2# sh running-config
    Building configuration...
    Current configuration:
    !
    hostname Provider-2
    log file /var/log/quagga/quagga.log
    hostname bgpd
    log stdout
    !
    password zebra
    !
    interface eth0
    ipv6 nd suppress-ra
    !
    interface eth1
    ipv6 nd suppress-ra
    !
    interface lo
    !
    router bgp 65870
    bgp router-id 172.16.10.13
    network 172.16.2.0/24
    neighbor 172.16.10.14 remote-as 65880
    neighbor 172.16.10.14 description "Provider-3"
    neighbor 172.16.10.14 timers 30 90
    neighbor 172.16.10.14 soft-reconfiguration inbound
    !
    ip forwarding
    !
    line vty
    !
    end
```

  * Настройка BGP на маршрутизаторе **Provider-3**

```text
    Provider-3# sh running-config
    Building configuration...
    Current configuration:
    !
    hostname Provider-3
    log file /var/log/quagga/quagga.log
    hostname bgpd
    log stdout
    !
    password zebra
    !
    interface eth0
    ipv6 nd suppress-ra
    !
    interface eth1
    ipv6 nd suppress-ra
    !
    interface eth2
    ipv6 nd suppress-ra
    !
    interface lo
    !
    router bgp 65880
    bgp router-id 172.16.3.1
    network 172.16.3.0/24
    neighbor 172.16.10.9 remote-as 65860
    neighbor 172.16.10.9 description "Provider-1"
    neighbor 172.16.10.9 timers 30 90
    neighbor 172.16.10.9 soft-reconfiguration inbound
    neighbor 172.16.10.13 remote-as 65870
    neighbor 172.16.10.13 description "Provider-2"
    neighbor 172.16.10.13 timers 30 90
    neighbor 172.16.10.13 soft-reconfiguration inbound
    !
    ip forwarding
    !
    line vty
    !
    end
```

После настройки BGP, не забываем также про настройку iptables на «внешних» маршрутизаторах, если это необходимо.
Если всё было сделано правильно, то таблица маршрутизации на **Provider-3** должна выглядеть так:

```text
[root@Provider-3 ~]# ip route
169.254.0.0/16 dev eth0 scope link metric 1002
169.254.0.0/16 dev eth1 scope link metric 1003
169.254.0.0/16 dev eth2 scope link metric 1004
172.16.1.0/24 via 172.16.10.9 dev eth0 proto zebra
172.16.2.0/24 via 172.16.10.13 dev eth1 proto zebra
172.16.3.0/24 dev eth2 proto kernel scope link src 172.16.3.1
172.16.10.8/30 dev eth0 proto kernel scope link src 172.16.10.10
172.16.10.12/30 dev eth1 proto kernel scope link src 172.16.10.14
```

То есть мы должны получать на этот роутер анонсы по BGP о сетях 172.16.1.0/24 и 172.16.2.0/24, и маршруты к ним должны присутствовать в таблице маршрутизации.

Соответственно, на маршрутизаторах **Provider-1** и **Provider-2** , маршрут к сети 172.16.3.0/24 также должен находиться в таблице маршрутизации.

**Настройка на VyOS1 и VyOS2 выхода в Интернет, для хостов из сетей датацентра VLAN17, 32, 40**

  * настраиваем правила балансировки исходящего трафика между роутерами **Provider-1** и **Provider-2** :

```text
    set protocols static route 0.0.0.0/0 next-hop 172.16.1.1
    set protocols static route 0.0.0.0/0 next-hop 172.16.2.1
    set load-balancing wan interface-health eth1 failure-count 3
    set load-balancing wan interface-health eth1 nexthop 172.16.1.1
    set load-balancing wan interface-health eth1 test 10 type ping
    set load-balancing wan interface-health eth1 test 10 target 172.16.3.1
    set load-balancing wan interface-health eth2 failure-count 3
    set load-balancing wan interface-health eth2 nexthop 172.16.2.1
    set load-balancing wan interface-health eth2 test 10 type ping
    set load-balancing wan interface-health eth2 test 10 target 172.16.3.1
```

  * исключаем трафик к внутренним сетям из балансировки трафика:

```text
    set load-balancing wan rule 10 inbound-interface eth+
    set load-balancing wan rule 10 destination address 172.20.40.0/23
    set load-balancing wan rule 10 exclude
    set load-balancing wan rule 20 inbound-interface eth+
    set load-balancing wan rule 20 destination address 172.20.32.0/23
    set load-balancing wan rule 20 exclude
    set load-balancing wan rule 30 inbound-interface eth+
    set load-balancing wan rule 30 destination address 172.20.1.0/24
    set load-balancing wan rule 30 exclude
```

  * применяем балансировку нагрузки для трафика из внутренних сетей в Интернет, на внешних сетевых интерфейсах:

```text
    set load-balancing wan rule 1000 inbound-interface eth0
    set load-balancing wan rule 1000 interface eth1
    set load-balancing wan rule 1000 interface eth2
    set load-balancing wan rule 1010 inbound-interface eth3
    set load-balancing wan rule 1010 interface eth1
    set load-balancing wan rule 1010 interface eth2
    set load-balancing wan rule 1020 inbound-interface eth3
    set load-balancing wan rule 1020 interface eth1
    set load-balancing wan rule 1020 interface eth2
    commit
```

_Примечание_ :
**eth+** используется как алиас (или псевдоним), который относится ко всем сетевым интерфейсам.

Проверка работы балансировки нагрузки:

```text
show wan-load-balance
show wan-load-balance connection
```

Перезагрузка балансировщика:

```text
restart wan-load-balance
```

**Тестирование работы внутренней маршрутизации и выхода в Интернет, при различных условиях**

  * Всё включено и настроено
  * Отключение интерфейса **VLAN30** на роутере **Provider-1**
  * Отключение сервиса **bgpd** на роутере **Provider-1**
  * Отключение интерфейса **VLAN31** на роутере **Provider-2**
  * Отключение сервиса **bgpd** на роутере **Provider-2**
  * Выключение роутера **VyOS1**
  * Включение роутера **VyOS1**
  * Выключение роутера **VyOS2**
  * Включение роутера **VyOS2**

Во время тестирования каждого пункта, указанного выше, обычно проверяется:

  * прохождение **ping** и **traceroute** к внешнему хосту в Интернете,
  * прохождение **ping** и **traceroute** между хостами во внутренних сетях,
  * дополнительно рекомендовал бы ещё проверять доступность хостов по **ssh** и, например, по **http**.

Для балансировки нагрузки можно задавать и другие параметры – вес и ограничение пропускной способности для канала, а также различные проверки для определения доступности внешнего канала. Можно самостоятельно разобраться с этими настройками, и даже протестировать как они работают – не зря же мы строили наш тестовый стенд.

Публикация в Интернет внутренних ресурсов через NAT, специально не рассматривалась, чтобы читатель имел возможность самостоятельно выполнить такую настройку, благо вся подготовительная работа для этого сделана (не забываем только про настройку политик файервола).

Также вполне может иметь место вариант, когда кто-либо из провайдеров, или даже оба провайдера, выдали не по два публичных адреса, а по одной подсети каждый, например, c префиксами /27.
В этом случае, чтобы иметь возможность выхода с хоста с двумя публичными адресами от двух разных провайдеров в Интернет, а также для подключения из Интернета к его публичным адресам, на нём необходимо будет настроить PBR ([policy-based routing](https://en.wikipedia.org/wiki/Policy-based_routing)) и [multipath routing](https://en.wikipedia.org/wiki/Multipath_routing). Впрочем, это уже тема для другой статьи (не разбирайте тестовый стенд, может ещё пригодится :)).

### Заключение

В этой статье мы вкратце рассмотрели настройку виртуальных маршрутизаторов VyOS, и довольно часто встречающийся вариант выхода в Интернет через двух независимых провайдеров – в принципе, без надёжной связи, датацентр со всей инфраструктурой в нём, не может считаться отказоустойчивым.

В частном случае, если необходима публикация большого числа каких-то внутренних ресурсов в Интернет, то можно рассмотреть аренду у какого-либо провайдера блока публичных IP адресов с префиксом не меньше /24, и анонсирование их по протоколу BGP через двух независимых провайдеров.

Такой вариант подключения нашего датацентра к Интернет может быть даже более интересным и предпочтительным, чем описанная в этой статье балансировка нагрузки на внешних каналах, так как позволяет организации в дальнейшем подключить второй датацентр с использованием публичных адресов из уже имеющегося блока адресов. Второй датацентр конечно же повысит не только отказоустойчивость, но и катастрофоустойчивость всего проекта в целом, понятно что нужно будет выполнять доработку проекта, но это уже другая история.

С формальной точки зрения, цикл статей о создании отказоустойчивой ИТ инфраструктуры можно было бы и закончить, так как все задачи, которые стояли перед нами в самом начале, были успешно выполнены:

  * всё железо настроено и подключено к сети и СХД;
  * настроен кластер oVirt;
  * настроена внутренняя маршрутизация и выход в Интернет.

Обычно ко времени начала развёртывания аппаратной инфраструктуры, разработчики уже должны иметь как минимум черновой вариант веб-проекта, который вероятно уже тестировался где-то в облаке. Так что пришло время начать развёртывать виртуальные машины, устанавливать на него ПО и настраивать публикацию ресурсов наружу.

Конечно, у нормального администратора неизменно возникнут вопросы про мониторинг и резервное копирование всего нашего хозяйства… В этом цикле статей такие вопросы не поднимались, но наверняка в будущих статьях мы к ним ещё вернёмся. Необходимо сразу отметить, что всем известный [Veeam](https://www.veeam.com/) – НЕ поддерживает резервное копирование oVirt/RHEV и вообще виртуальных машин KVM, от слова никак, поэтому придётся использовать или другие коммерческие решения (**Veritas NetBackup** , **Acronis Cyber Backup** , **TrilioVault** , **Bacula Enterprise Edition** , **SEP** , etc.), или «ваять» что-то своё, или «допиливать» какие-то уже имеющиеся OpenSource решения, найденные на просторах Интернета.

Ну а что касается мониторинга железа и виртуальных машин, то тут дело вкуса и личных предпочтений, обычно на проектах используется [Zabbix](https://www.zabbix.com/) – бесплатное и довольно надёжное решение, с массой доступных шаблонов на любой вкус и цвет.

Но, впрочем, вернёмся обратно к нашей инфраструктуре – напомню, что в первой статье в составе железа была указана пара замечательных коммутаторов [Cisco 3850](https://www.cisco.com/c/ru_ru/products/switches/catalyst-3850-series-switches/index.html), и было бы очень странно не использовать их по прямому предназначению – скоростной маршрутизации трафика между сетями. Поэтому в следующей статье мы и рассмотрим их интеграцию в нашу инфраструктуру, так как работа для них обязательно найдётся.

**********

[vyos](/tags/vyos.md)
