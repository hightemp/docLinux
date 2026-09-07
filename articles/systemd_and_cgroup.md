# systemd и cgroup

Источник: [systemd and cgroup](https://medium.com/@charles.vissol/systemd-and-cgroup-7eb80a08234d)

Автор: Charles Vissol · 16 декабря 2023 · 8 мин чтения

![Заголовное изображение](/images/102441cc7ce59cb3c6d5a990fc6f7ee1.png)

(Изображение: Charles Vissol)

Эта статья требует хорошего знания Linux, а также минимального знания о `cgroup` (прочитайте мою предыдущую статью: [Cgroup introduction](https://medium.com/@charles.vissol/cgroup-introduction-45017140493d)). Она описывает совместную работу `systemd` и `cgroup` в системах Linux.

В последних дистрибутивах Debian `systemd` автоматически монтирует `cgroupfs` (файловая система `cgroup`) версии 2 в `/sys/fs/cgroup` во время процесса загрузки. Таким образом, `systemd` и менеджер служб используют `cgroup` для организации всех юнитов и служб, а это значит, что `systemd` и `cgroup` работают вместе.

## Что такое systemd?

`systemd` — это системный менеджер и менеджер служб для операционных систем Linux. `systemd` запускается на раннем этапе загрузки системы и работает как первый процесс (PID 1).

`systemd` выступает в роли системы инициализации («init»), которая запускает и поддерживает **службы пользовательского пространства**.

Обычно пользователь не запускает `systemd` напрямую — экземпляры пользовательского менеджера запускаются автоматически через службу [user@.service](https://www.man7.org/linux/man-pages/man5/user@.service.5.html).

Кроме того, `systemd` предоставляет ряд интерфейсов, используемых для создания и управления наборами процессов с целью мониторинга и контроля их использования ресурсов.

Как следствие, основное дерево `cgroup` становится частной собственностью этого компонента пользовательского пространства и больше не является общим ресурсом.

В дистрибутивах с `systemd` эту роль берёт на себя процесс с PID 1, и поэтому он должен предоставлять API, чтобы клиенты могли воспользоваться возможностями `cgroup`.

> Примечание
>
> Службы, работающие в дистрибутивах с `systemd`, могут управлять собственными поддеревьями дерева `cgroup`, при условии что они явно включают для них режим делегирования (delegation mode).

`systemd` имеет 2 категории экземпляров:

**1-я категория: системный экземпляр**

Работая как **системный экземпляр**, `systemd` интерпретирует конфигурационный файл `/etc/systemd/system.conf` и файлы в каталоге `/etc/systemd/system.conf.d`.

Подробнее см. [systemd-system.conf](https://www.man7.org/linux/man-pages/man5/systemd-system.conf.5.html).

**2-я категория: пользовательский экземпляр**

Работая как **пользовательский экземпляр**, `systemd` обычно интерпретирует конфигурационный файл `~/.config/systemd/user.conf` и файлы в каталоге `/etc/systemd/user.conf.d`.

> Примечание
>
> В некоторых случаях вы можете найти файлы (службы) в `~/.config/systemd/user/`.

`systemd` предоставляет систему зависимостей между различными сущностями, называемыми «юнитами» (units), 11 различных типов. Юниты инкапсулируют различные объекты, которые имеют отношение к загрузке и сопровождению системы. Большинство этих юнитов настраивается в файлах конфигурации юнитов (подробности синтаксиса см. в [systemd.unit](https://www.man7.org/linux/man-pages/man5/systemd.unit.5.html)).

Опишем их кратко:

1. Юниты `.service` запускают и управляют демонами и процессами, из которых они состоят. Подробности см. в [systemd.service(5)](https://www.man7.org/linux/man-pages/man5/systemd.service.5.html).
2. Юниты `.socket` инкапсулируют локальные сокеты IPC (Inter-Process Call, межпроцессное взаимодействие) или сетевые сокеты в системе и полезны для активации по сокету. Подробности о юнитах сокетов см. в [systemd.socket(5)](https://www.man7.org/linux/man-pages/man5/systemd.socket.5.html), а о деталях активации по сокету и других формах активации — в [daemon(7)](https://www.man7.org/linux/man-pages/man7/daemon.7.html).
3. Юниты `.target` полезны для группировки юнитов или предоставления известных точек синхронизации во время загрузки, см. [systemd.target(5)](https://www.man7.org/linux/man-pages/man5/systemd.target.5.html).
4. Юниты `.device` предоставляют устройства ядра в `systemd` и могут использоваться для реализации активации по устройству. Подробности см. в [systemd.device(5)](https://www.man7.org/linux/man-pages/man5/systemd.device.5.html).
5. Юниты `.mount` управляют точками монтирования в файловой системе, подробности см. в [systemd.mount(5)](https://www.man7.org/linux/man-pages/man5/systemd.mount.5.html).
6. Юниты `.automount` предоставляют возможности автоматического монтирования для монтирования файловых систем по требованию, а также для параллелизации загрузки. См. [systemd.automount(5)](https://www.man7.org/linux/man-pages/man5/systemd.automount.5.html).
7. Юниты `.timer` полезны для запуска активации других юнитов по таймерам. Подробности можно найти в [systemd.timer(5)](https://www.man7.org/linux/man-pages/man5/systemd.timer.5.html).
8. Юниты `.swap` очень похожи на юниты монтирования и инкапсулируют разделы или файлы подкачки (swap) операционной системы. Они описаны в [systemd.swap(5)](https://www.man7.org/linux/man-pages/man5/systemd.swap.5.html).
9. Юниты `.path` могут использоваться для активации других служб при изменении или модификации объектов файловой системы. См. [systemd.path(5)](https://www.man7.org/linux/man-pages/man5/systemd.path.5.html).
10. Юниты `.slice` могут использоваться для группировки юнитов, которые управляют системными процессами (такими как юниты служб и scope), в иерархическое дерево в целях управления ресурсами. См. [systemd.slice(5)](https://www.man7.org/linux/man-pages/man5/systemd.slice.5.html).
11. Юниты `.scope` похожи на юниты служб, но управляют чужими процессами, а не запускают их сами. См. [systemd.scope(5)](https://www.man7.org/linux/man-pages/man5/systemd.scope.5.html). Юниты называются так же, как их файлы конфигурации. Некоторые юниты имеют особую семантику. Подробный список доступен в [systemd.special(7)](https://www.man7.org/linux/man-pages/man7/systemd.special.7.html).

## cgroup и systemd

`cgroup` (изобретён Google) не зависит от `systemd` (изобретён Red Hat) и старше него.

Сегодня в корпоративных системах Linux `cgroup` версии 2 включается по умолчанию вместе с `systemd`.

> Информация
>
> Fedora, Arch, Ubuntu 21.10+ и Debian 11 — единственные дистрибутивы Linux, которые на этот момент по умолчанию работают с `cgroup` версии 2. Однако многие контейнерные технологии всё ещё на версии 1.

Если точнее, `systemd` построен поверх API `cgroup` ядра, который требует, чтобы каждым отдельным `cgroup` управлял только один писатель.

По умолчанию `systemd` создаёт новый `cgroup` под `system.slice` для каждой отслеживаемой им службы, и вы можете изменить это поведение, отредактировав файлы служб `systemd`.

Есть три варианта управления `cgroup` в `systemd`:

* Редактирование самого файла службы.
* Использование drop-in файлов.
* Использование команд `systemctl set-property` — это то же самое, что редактировать файлы вручную, но `systemctl` создаёт необходимые записи за вас.

Подробнее: [https://www.redhat.com/sysadmin/cgroups-part-four](https://www.redhat.com/sysadmin/cgroups-part-four)

## Структура cgroup

Я сосредоточусь на юните slice — это юнит `systemd` для взаимодействия с `cgroup`.

Slice не содержит процессов. Это группа иерархически организованных юнитов. Slice управляет процессами, которые запущены либо в **scope**, либо в **службах**. Четыре slice по умолчанию таковы:

* `-.slice`: корневой slice, который является корнем всей иерархии slice. Обычно он не содержит напрямую других юнитов. Однако вы можете использовать его для создания настроек по умолчанию для всего дерева slice.
* `system.slice`: системные службы, запущенные systemd.
* `user.slice`: службы пользовательского режима. Каждому вошедшему в систему пользователю назначается неявный slice.
* `machine.slice`: службы, предназначенные для запуска контейнеров или виртуальных машин.

> Примечание
>
> Службы запускаются `systemd`, а scope запускаются внешними средствами (виртуальные машины, контейнеры, пользовательские сессии...).
>
> Сисадмин может определять собственные slice и назначать им scope и службы.

Чтобы увидеть графическое представление этих процессов, выполните команду `systemd-cgls`:

```bash
systemd-cgls
```

Вывод в Debian 11.4 должен выглядеть так (одинаково для версии 1 и версии 2):

```text
Control group /:
-.slice
├─user.slice
│ └─user-1000.slice
│ ├─user@1000.service
│ │ ├─background.slice
│ │ │ └─plasma-kglobalaccel.service
│ │ │ └─1977 /usr/bin/kglobalaccel5
│ │ ├─app.slice
│ │ │ ├─app-org.kde.kate-b498c13a5e274a0c882c324e5d1f72f7.scope
│ │ │ │ └─38353 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/vm/numa.rst
│ │ │ ├─app-org.kde.kate-bd04ec663c48458388b9fa5763b21475.scope
│ │ │ │ └─36045 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/tainted-kernels.rst
│ │ │ ├─app-org.kde.kate-701de1e0f47c4040b04c2b14b0736814.scope
│ │ │ │ └─36107 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/perf-security.rst
│ │ │ ├─xdg-permission-store.service
│ │ │ │ └─1877 /usr/libexec/xdg-permission-store
│ │ │ ├─app-\x2fusr\x2fbin\x2fkorgac-fba6fc922f304fd892acdbd09d5c57e6.scope
│ │ │ │ └─2059 /usr/bin/korgac -session 10dfd7e29f000165373856000000016460011_1659082942_32052
│ │ │ ├─xdg-document-portal.service
│ │ │ │ ├─1873 /usr/libexec/xdg-document-portal
│ │ │ │ └─1883 fusermount -o rw,nosuid,nodev,fsname=portal,auto_unmount,subtype=portal -- /run/user/1000/doc
│ │ │ ├─app-org.kde.kate-3c8915e087fd4680ba5fed65f42a4f88.scope
│ │ │ │ └─36427 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/sysctl/vm.rst
│ │ │ ├─app-org.kde.kate-1a49d3c474e34ad283440d3d1298394a.scope
│ │ │ │ └─36893 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/laptops/laptop-mode.rst
│ │ │ ├─xdg-desktop-portal.service
│ │ │ │ └─1864 /usr/libexec/xdg-desktop-portal
│ │ │ ├─app-org.kde.kate-2b0ef5011a5344989296587e17dde86e.scope
[lines 1-29]
```

> Информация
>
> На любой настольной машине у вас всегда будет намного больше работающих служб, чем на строго текстовой машине.

Первый cgroup — это cgroup `/`, корневой cgroup. Вторая строка начинает листинг для корневого slice (`-.slice`) с прямым потомком `user.slice`, а далее `user-1000.slice`. Здесь `1000` соответствует моему идентификатору пользователя (User ID).

> Важно
>
> Чтобы увидеть пользовательские slice, нужно запустить `systemd-cgls` вне файловой системы `cgroup`. Чем глубже вы погружаетесь в файловую систему `/sys/fs/cgroup`, тем меньше видите с помощью `systemd-cgls`.

## user.slice

`user.slice` определяется файлом юнита `/lib/systemd/system/user.slice`, который выглядит так:

```ini
[Unit]
Description=User and Session Slice
Documentation=man:systemd.special(7)
Before=slices.target
```

Этот slice должен завершить запуск до `slices.target` (в том же каталоге, что и `user.slice`), который содержит:

```ini
[Unit]
Description=Slices
Documentation=man:systemd.special(7)
Wants=-.slice system.slice
After=-.slice system.slice
```

`slices.target` отвечает за настройку slice, которые работают при загрузке вашей машины: по умолчанию он запускает `system.slice` и корневой slice (`-.slice`), как мы видим в параметрах `Wants` и `After`.

> Примечание
>
> Мы можем добавить больше slice в текущий список в `user.slice` и `slices.target`.

На том же уровне, что и `user.slice`, у нас есть `init.scope` и `system.slice`:

```text
-.slice
├─user.slice
. . .
├─init.scope
. . .
├─system.slice
│. . .
```

## user-1000.slice

Первым потомком `user-1000.slice` является `user@1000.slice`. `user@1000.slice` отвечает за все службы, работающие в slice пользователя `1000`, и настраивается шаблоном `user@.service` (в `/lib/systemd/system/user@.service`).

Шаблон `user@.service` имеет 2 секции:

* `[Unit]`

```ini
[Unit]
Description=User Manager for UID %i
Documentation=man:user@.service(5)
After=systemd-user-sessions.service user-runtime-dir@%i.service dbus.service
Requires=user-runtime-dir@%i.service
IgnoreOnIsolate=yes
```

* `[Service]`

```ini
[Service]
User=%i
PAMName=systemd-user
Type=notify
ExecStart=/lib/systemd/systemd --user
Slice=user-%i.slice
KillMode=mixed
Delegate=pids memory
TasksMax=infinity
TimeoutStopSec=120 s
KeyringMode=inherit
```

> Важно
>
> Во время выполнения `%i` заменяется на числовой идентификатор пользователя.

Рассмотрим некоторые интересные директивы секции `[Service]`:

* `ExecStart`: `systemd` запускает новую сессию `systemd` для каждого пользователя, который входит в систему
* `Slice`: создаёт отдельный slice для каждого пользователя
* `TaskMax`: ограничивает или не ограничивает количество процессов. Здесь `infinity` означает, что ограничений нет
* `Delegate`: разрешает делегирование для перечисленных здесь контроллеров, то есть `pids` и `memory` (делегирование работает только для `cgroup` версии 2)

Все службы, работающие в slice пользователя `1000`, являются потомками `user@1000.service`. В этом дереве мы также можем видеть scope, соответствующие запуску локальных программ пользователя.

```bash
systemd-cgls | grep scope
```

```text
│ │ │ ├─app-gnome\x2dtodo-c8bbb1ea42124e4eabe95eca8c02e5f7.scope
│ │ │ ├─app-google\x2dchrome-fa92ae1ce8f54f4298975211065460e7.scope
│ │ │ ├─app-protonvpn-8065209d48094182b0b0c0352d51cd10.scope
│ │ │ ├─app-org.kde.konsole-de12e69356754c5dae23bdfdc108d53a.scope
│ │ │ │ └─44710 grep scope
│ │ │ ├─app-firefox\x2desr-73828cd3b1754ee0b4ffafdd6750507d.scope
│ │ │ ├─app-\x2fusr\x2flib\x2fx86_64\x2dlinux\x2dgnu\x2flibexec\x2fDiscoverNotifier-72a3c7b93c0947d5bbcf6c3beee4e003.scope
│ │ │ ├─app-marktext-d9ed06b1e1724ec482580148c7aa057c.scope
│ │ │ ├─app-\x2fusr\x2fbin\x2fkorgac-9e6550aaf81c4723a7afd6ba45888d14.scope
│ │ └─init.scope
│ └─session-3.scope
├─init.scope
```

> Информация
>
> Локальная терминальная сессия обозначается `session-2.scope`
>
> Удалённая терминальная сессия обозначается `session-3.scope`
>
> Здесь терминальная сессия обслуживается `konsole`, терминальной программой KDE

> Важно
>
> `.scope` создаются только программно во время выполнения (не создаются с помощью файлов юнитов). Так что не стоит ожидать наличия каких-либо файлов `.scope` в каталоге `/lib/systemd/system/`.

## machine.slice

В моей конфигурации работает Podman (`libpod` — это контейнер `podman-docker`), и мы можем увидеть представление `machine.slice` следующим образом:

```text
. . .
└─machine.slice
 └─libpod-cc06c35f21cedd4d2384cf2c048f013748e84cabdc594b110a8c8529173f4c81.sco>
 ├─1438 apache2 -DFOREGROUND
 ├─1560 apache2 -DFOREGROUND
 ├─1561 apache2 -DFOREGROUND
 ├─1562 apache2 -DFOREGROUND
 ├─1563 apache2 -DFOREGROUND
 └─1564 apache2 -DFOREGROUND
```

## Управление древовидным представлением процессов systemd

Когда `systemd-cgls` запускается без параметров, он возвращает всю иерархию `cgroup`. Самый высокий уровень дерева `cgroup` формируется slice и может выглядеть следующим образом:

```text
├─system
│ ├─1 /usr/lib/systemd/systemd --switched-root --system --deserialize 20
│ ...
│
├─user
│ ├─user-1000
│ │ └─ ...
│ ├─user-2000
│ │ └─ ...
│ ...
│
└─machine
 ├─machine-1000
 │ └─ ...
 ...
```

> Информация
>
> Slice machine присутствует только если вы запускаете виртуальную машину или контейнер.

Чтобы сократить вывод `systemd-cgls` и просмотреть указанную часть иерархии, выполните:

```bash
$ systemd-cgls $NAME
```

`$NAME` — это контроллер ресурсов, который вы хотите просмотреть.

Пример: контроллер `memory`:

```bash
$ systemd-cgls memory
```

```text
memory:
├─ 1 /usr/lib/systemd/systemd --switched-root --system --deserialize 23
├─ 475 /usr/lib/systemd/systemd-journald
[...]
```

`systemd` также предоставляет команду `machinectl`, предназначенную для мониторинга контейнеров Linux.

Linux также предоставляет `systemctl` для получения древовидного представления процессов с использованием юнитов `systemd` в качестве параметра для фильтрации запросов по синтаксису: `systemctl status $systemd_unit`.

Например: `systemctl status user.slice`

## Почему cgroup важен?

Сегодня серверы поставляются с одним или несколькими многоядерными CPU и большим объёмом памяти. Управление ресурсами на этих «монстрахах» важнее, чем это было в старых системах. Фактически сервер может одновременно запускать несколько служб, несколько виртуальных машин, несколько контейнеров и несколько учётных записей пользователей, поэтому управление ресурсами становится приоритетом.

Эта ситуация требует более мощных инструментов, чтобы гарантировать, что все эти процессы и пользователи «играют по правилам». В этом и заключается назначение `cgroup`.

## Что может сделать сисадмин с помощью cgroup?

* Управлять использованием ресурсов процессами или пользователями.
* Отслеживать использование ресурсов пользователями в многопользовательских (multi-tenant) системах для точного выставления счетов.
* Легче изолировать работающие процессы друг от друга. Это не только повышает безопасность, но и позволяет нам иметь лучшие технологии контейнеризации, чем раньше.
* Запускать серверы, плотно упакованные виртуальными машинами и контейнерами, благодаря лучшему управлению ресурсами и изоляции процессов.
* Повышать производительность, гарантируя, что процессы всегда работают на одном и том же ядре CPU или наборе ядер, вместо того чтобы позволять ядру Linux перемещать их между разными ядрами.
* Вносить устройства в белый или чёрный список.
* Настраивать формирование сетевого трафика (traffic shaping).

---

[systemd](/tags/systemd.md)
[cgroups](/tags/cgroups.md)
[linux](/tags/linux.md)
