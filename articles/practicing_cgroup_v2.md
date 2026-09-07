# Практика cgroup v2

Источник: [practicing_cgroup_v2](https://medium.com/@charles.vissol/practicing-cgroup-v2-cad6743bba0c)

Шарль Виссол (Charles Vissol) · 4 февраля 2024 · 14 мин чтения

![](/images/ee7b6542c851681b31794b8eb1b8cf02.png)

(Источник изображения: Charles Vissol)

Это моя последняя статья о `cgroup`, закрывающая данную тему.

Цель этого документа — описать набор практических команд для управления возможностями `cgroup`.

## Определение версии cgroup

Чтобы просто узнать вашу версию `cgroup`, выполните:

```bash
$ mount | grep cgroup
```

Вывод:

```text
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
```

Здесь это означает, что работает `cgroup` v2, потому что смонтирована файловая система `cgroup` v2. Вы не можете иметь одновременно работающие v1 и v2 в вашей системе.

Когда мы используем команду `mount` и передаём её вывод через `grep`, мы видим, что каждый из этих контроллеров ресурсов смонтирован в собственном виртуальном разделе.

Эта команда также напоминает вам, что `cgroup` — это иерархия файловой системы, выигрывающая от опций `mount` (обратите внимание на `nsdelegate` и `memory_recursiveprot`, поддерживаемые cgroup v2).

`/sys/fs/cgroup` называется **корневой контрольной группой** (root control group). Это директория, содержащая файлы интерфейса (начинающиеся с `cgroup`) и специфичные для контроллеров файлы, такие как `cpuset.cpus.effective`.

Некоторые директории специфичны для `systemd`: `init.scope`, `system.slice`, `user.slice` и в некоторых случаях `machine.slice`.

```text
ls -l /sys/fs/cgroup
total 0
-r--r--r-- 1 root root 0 Sep  9 08:00 cgroup.controllers
-rw-r--r-- 1 root root 0 Sep  9 08:00 cgroup.max.depth
-rw-r--r-- 1 root root 0 Sep  9 08:00 cgroup.max.descendants
-rw-r--r-- 1 root root 0 Sep  9 08:00 cgroup.procs
-r--r--r-- 1 root root 0 Sep  9 08:00 cgroup.stat
-rw-r--r-- 1 root root 0 Sep  9 07:43 cgroup.subtree_control
-rw-r--r-- 1 root root 0 Sep  9 08:00 cgroup.threads
-rw-r--r-- 1 root root 0 Sep  9 08:00 cpu.pressure
-r--r--r-- 1 root root 0 Sep  9 08:00 cpuset.cpus.effective
-r--r--r-- 1 root root 0 Sep  9 08:00 cpuset.mems.effective
-r--r--r-- 1 root root 0 Sep  9 08:00 cpu.stat
drwxr-xr-x 2 root root 0 Sep  9 07:43 dev-hugepages.mount
drwxr-xr-x 2 root root 0 Sep  9 07:43 dev-mqueue.mount
drwxr-xr-x 2 root root 0 Sep  9 08:00 init.scope
-rw-r--r-- 1 root root 0 Sep  9 08:00 io.cost.model
-rw-r--r-- 1 root root 0 Sep  9 08:00 io.cost.qos
-rw-r--r-- 1 root root 0 Sep  9 08:00 io.pressure
-r--r--r-- 1 root root 0 Sep  9 08:00 io.stat
-r--r--r-- 1 root root 0 Sep  9 08:00 memory.numa_stat
-rw-r--r-- 1 root root 0 Sep  9 08:00 memory.pressure
-rw-r--r-- 1 root root 0 Sep  9 08:00 memory.stat
drwxr-xr-x 2 root root 0 Sep  9 07:43 proc-sys-fs-binfmt_misc.mount
drwxr-xr-x 2 root root 0 Sep  9 07:43 sys-fs-fuse-connections.mount
drwxr-xr-x 2 root root 0 Sep  9 07:43 sys-kernel-config.mount
drwxr-xr-x 2 root root 0 Sep  9 07:43 sys-kernel-debug.mount
drwxr-xr-x 2 root root 0 Sep  9 07:43 sys-kernel-tracing.mount
drwxr-xr-x 47 root root 0 Sep  9 08:00 system.slice
drwxr-xr-x 3 root root 0 Sep  9 07:44 user.slice
```

Обратите внимание, если вы видите вывод вроде этого, ваша система поддерживает контроллеры `cgroup` v1:

```text
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,name=systemd)
cgroup on /sys/fs/cgroup/perf_event type cgroup (rw,nosuid,nodev,noexec,relatime,perf_event)
cgroup on /sys/fs/cgroup/net_cls,net_prio type cgroup (rw,nosuid,nodev,noexec,relatime,net_cls,net_prio)
cgroup on /sys/fs/cgroup/blkio type cgroup (rw,nosuid,nodev,noexec,relatime,blkio)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/devices type cgroup (rw,nosuid,nodev,noexec,relatime,devices)
cgroup on /sys/fs/cgroup/rdma type cgroup (rw,nosuid,nodev,noexec,relatime,rdma)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
cgroup on /sys/fs/cgroup/memory type cgroup (rw,nosuid,nodev,noexec,relatime,memory)
```

С cgroups версии 1 каждый из контроллеров ресурсов смонтирован в собственном виртуальном разделе:

```text
[vissol@debian ~]$ mount | grep 'cgroup'
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,seclabel,mode=755)
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,seclabel,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd)
. . .
. . .
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,seclabel,freezer)
```

## Как узнать, находится ли процесс в cgroup?

У любого процесса есть PID, и любой процесс, назначенный `cgroup`, имеет назначенную файловую систему `cgroup` в `/sys/fs/cgroup`.

Чтобы узнать информацию об управлении `cgroup` для конкретного PID, выполните следующие команды (пример):

```bash
$ top | grep firefox-esr
3509 vissol 20 0 4290852 636412 201840 S 6.7 3.9 26:51.34 firefox-esr
$ ps -o cgroup 3509
CGROUP
0::/user.slice/user-1000.slice/user@1000.service/app.slice/app-firefox\x2desr-07dd78c014ab4fe48f7395474e0b5c5e.scope
$ cd /sys/fs/cgroup/user.slice/user-1000.slice/user\@1000.service/app.slice/app-firefox\\x2desr-07dd78c014ab4fe48f7395474e0b5c5e.scope
$ ls -l
total 0
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.controllers
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.events
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.freeze
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.max.depth
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.max.descendants
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.procs
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.stat
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.subtree_control
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.threads
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cgroup.type
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cpu.pressure
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 cpu.stat
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 io.pressure
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.current
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.events
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.events.local
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.high
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.low
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.max
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.min
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.numa_stat
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.oom.group
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.pressure
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.stat
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.swap.current
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.swap.events
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.swap.high
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 memory.swap.max
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 pids.current
-r--r--r-- 1 vissol vissol 0 Jul 26 08:44 pids.events
-rw-r--r-- 1 vissol vissol 0 Jul 26 08:44 pids.max
```

Как вы видите, у процесса firefox-esr есть 4 назначенных контроллера cgroup v2: `cpu`, `io`, `memory`, `pids`.

## Как контролировать потребление CPU для приложения?

По умолчанию контроллеры вроде `cpu` хранятся в `/sys/fs/cgroup/cgroup.controllers`.

Пример в Debian:

```bash
cat /sys/fs/cgroup/cgroup.controllers
cpuset cpu io memory hugetlb pids rdma
```

`cgroup.controllers`: файл только для чтения, содержащий список контроллеров, доступных в этой `cgroup` и её дочерних узлах `cgroup`. Его содержимое соответствует файлу `cgroup.subtree_control`.

Этот список — полный список контроллеров, доступных на платформе для всех процессов `cgroup` (дочерних процессов корневой контрольной группы).

Но если вы создаёте дочернюю `cgroup`, в которой хотите включить определённые контроллеры, вам нужно:

1. Включить контроллеры, которые вы хотите применить к дочерней группе. Здесь, например, `cpu` и `cpuset` для контроля потребления CPU:

```bash
$ cat /sys/fs/cgroup/cgroup.controllers
cpuset cpu io memory hugetlb pids rdma
$ sudo echo "+cpu" >> /sys/fs/cgroup/cgroup.subtree_control
$ sudo echo "+cpuset" >> /sys/fs/cgroup/cgroup.subtree_control
$ sudo echo "-io" >> /sys/fs/cgroup/cgroup.subtree_control
```

> **Важно**
>
> Ресурсы распределяются сверху вниз, и `cgroup` может дальше распределять ресурс только если этот ресурс был распределён ей от родителя. Это значит, что все не-корневые файлы `cgroup.subtree_control` могут содержать только те контроллеры, которые включены в файле `cgroup.subtree_control` родителя. Контроллер может быть включён, только если родитель имеет этот контроллер включённым, и контроллер не может быть выключен, если один или более дочерних групп имеют его включённым.

2. Создать поддиректорию процесса (здесь — процесс `cgroup` с именем foo):

```bash
mkdir /sys/fs/cgroup/foo/
```

Debian автоматически заполняет папку полными контрольными файлами:

```text
$ ll /sys/fs/cgroup/foo/
-r——r——r--. 1 root root 0 Jun 1 10:33 cgroup.controllers
-r——r——r--. 1 root root 0 Jun 1 10:33 cgroup.events
-rw-r——r--. 1 root root 0 Jun 1 10:33 cgroup.freeze
-rw-r——r--. 1 root root 0 Jun 1 10:33 cgroup.max.depth
-rw-r——r--. 1 root root 0 Jun 1 10:33 cgroup.max.descendants
-rw-r——r--. 1 root root 0 Jun 1 10:33 cgroup.procs
-r——r——r--. 1 root root 0 Jun 1 10:33 cgroup.stat
-rw-r——r--. 1 root root 0 Jun 1 10:33 cgroup.subtree_control
……
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpuset.cpus
-r——r——r--. 1 root root 0 Jun 1 10:33 cpuset.cpus.effective
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpuset.cpus.partition
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpuset.mems
-r——r——r--. 1 root root 0 Jun 1 10:33 cpuset.mems.effective
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpu.stat
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpu.weight
-rw-r——r--. 1 root root 0 Jun 1 10:33 cpu.weight.nice
……
-r——r——r--. 1 root root 0 Jun 1 10:33 memory.events.local
-rw-r——r--. 1 root root 0 Jun 1 10:33 memory.high
-rw-r——r--. 1 root root 0 Jun 1 10:33 memory.low
……
-r——r——r--. 1 root root 0 Jun 1 10:33 pids.current
-r——r——r--. 1 root root 0 Jun 1 10:33 pids.events
-rw-r——r--. 1 root root 0 Jun 1 10:33 pids.max
```

Вывод показывает файлы вроде `cpuset.cpus` и `cpu.max`. Эти файлы специфичны для контроллеров `cpuset` и `cpu`. Контроллеры `cpuset` и `cpu` вручную включены для _прямых дочерних контрольных групп_ корня (`/sys/fs/cgroup/`) с помощью файла `/sys/fs/cgroup/cgroup.subtree_control`.

Директория также включает общие файлы контрольного интерфейса `cgroup.*`, такие как `cgroup.procs` или `cgroup.controllers`, которые общие для всех контрольных групп независимо от включённых контроллеров.

Файлы вроде `memory.high` и `pids.max` относятся к контроллерам `memory` и `pids`, которые находятся в корневой контрольной группе (`/sys/fs/cgroup/`) и всегда включены по умолчанию.

По умолчанию новосозданная дочерняя группа наследует доступ ко всем ресурсам CPU и памяти системы без каких-либо ограничений.

3. Включить контроллеры, связанные с CPU, в `/sys/fs/cgroup/foo/`, чтобы получить контроллеры, относящиеся только к CPU:

```bash
echo "+cpu" >> /sys/fs/cgroup/foo/cgroup.subtree_control
echo "+cpuset" >> /sys/fs/cgroup/foo/cgroup.subtree_control
```

Эти команды гарантируют, что непосредственная дочерняя контрольная группа будет иметь _только_ контроллеры, относящиеся к регулированию распределения времени CPU — не контроллеры `memory` или `pids`.

4. Создать директорию `/sys/fs/cgroup/foo/tasks/`:

```bash
mkdir /sys/fs/cgroup/foo/tasks/
```

Директория `/sys/fs/cgroup/foo/tasks/` определяет дочернюю группу с файлами, которые относятся только к контроллерам `cpu` и `cpuset`.

5. Осмотреть новосозданную папку:

```text
$ ll /sys/fs/cgroup/foo/tasks
-r——r——r--. 1 root root 0 Jun 1 11:45 cgroup.controllers
-r——r——r--. 1 root root 0 Jun 1 11:45 cgroup.events
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.freeze
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.max.depth
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.max.descendants
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.procs
-r——r——r--. 1 root root 0 Jun 1 11:45 cgroup.stat
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.subtree_control
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.threads
-rw-r——r--. 1 root root 0 Jun 1 11:45 cgroup.type
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpu.max
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpu.pressure
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpuset.cpus
-r——r——r--. 1 root root 0 Jun 1 11:45 cpuset.cpus.effective
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpuset.cpus.partition
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpuset.mems
-r——r——r--. 1 root root 0 Jun 1 11:45 cpuset.mems.effective
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpu.stat
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpu.weight
-rw-r——r--. 1 root root 0 Jun 1 11:45 cpu.weight.nice
-rw-r——r--. 1 root root 0 Jun 1 11:45 io.pressure
-rw-r——r--. 1 root root 0 Jun 1 11:45 memory.pressure
```

6. Гарантировать, что процессы, для которых вы хотите контролировать время CPU, конкурируют на одном и том же CPU:

```bash
echo "1" > /sys/fs/cgroup/foo/tasks/cpuset.cpus
```

Предыдущая команда гарантирует, что процессы, которые вы поместите в дочернюю контрольную группу `foo/tasks`, конкурируют на одном и том же CPU. Эта настройка важна для активации контроллера `cpu`.

> **Важно**
>
> Контроллер `cpu` активируется только если соответствующая дочерняя контрольная группа имеет по крайней мере 2 процесса, которые конкурируют за время на одном CPU.

## Создание собственного процесса cgroup

Чтобы создать процесс `cgroup`, вам нужно сначала создать директорию в структуре `/sys/fs/cgroup`.

> Информация
>
> Рекомендуется создавать по крайней мере два уровня дочерних контрольных групп внутри корневой контрольной группы `/sys/fs/cgroup/`, чтобы поддерживать лучшую организационную ясность файлов `cgroup`.

Но для упрощения здесь я создаю только одну поддиректорию:

```bash
$ sudo mkdir -p /sys/fs/cgroup/foo
```

Как только директория создана, она автоматически заполняется контроллерами `cgroup` v2 по умолчанию, такими как `freezer` (`cgroup.freeze`), `cpu` (`cpu.pressure`, `cpu.stat`), `io` (`io.pressure`), `memory` (`memory.events`, `memory.low`...), `pids` (`pids.events`, `pids.max`...)...

Вы можете изменять или добавлять любые контроллеры, которые хотите. См. далее в этой статье больше объяснений про контроллеры и их использование в `cgroup`.

Полное объяснение доступно в руководстве администратора ядра: **Documentation/admin-guide/cgroup-v2.rst** (скачайте исходный код ядра и документацию с [kernel.org](https://kernel.org/)).

После правильной настройки вы можете породить собственный процесс — например, создать скрипт с бесконечным циклом `foo.sh`:

```bash
#!/bin/bash
while :
do
  echo "Press [CTRL+C] to stop.."
  sleep 1000
done
```

Запустите скрипт и получите его PID. Здесь это `46983`.

Теперь вставьте PID в файл `cgroup.procs` в директории `foo`, чтобы назначить ваш процесс в созданную вами `cgroup`:

```bash
sudo ./foo.sh
# Вставить PID, чтобы назначить его в cgroup foo
sudo echo 46983 > /sys/fs/cgroup/foo/cgroup.procs
```

После этого вы можете проверить, что ваш процесс назначен в cgroup **foo**:

```text
$ sudo ps -o cgroup 46983
CGROUP
0::/foo
```

## Получение списка доступных контроллеров

Вы можете увидеть доступные контроллеры в вашей системе, отобразив:

```bash
$ cat /sys/fs/cgroup/cgroup.controllers
cpuset cpu io memory hugetlb pids rdma
```

На этом шаге мы знаем, доступны ли контроллеры в системе. Но чтобы быть уверенными, что они доступны, вы должны отобразить:

```bash
cat /sys/fs/cgroup/cgroup.subtree_control
```

Вывод (значение по умолчанию):

```text
memory pids
```

`memory` и `pids` включены по умолчанию в Debian.

## Просмотр иерархии контрольных групп

Чтобы отобразить всю иерархию cgroup вашей системы, выполните:

```bash
systemd-cgls
```

Вывод в Debian 11.4 должен выглядеть примерно так:

```text
Control group /:
-.slice
├─user.slice
│ └─user-1000.slice
│   ├─user@1000.service
│   │ ├─background.slice
│   │ │ └─plasma-kglobalaccel.service
│   │ │   └─1977 /usr/bin/kglobalaccel5
│   │ ├─app.slice
│   │ │ ├─app-org.kde.kate-b498c13a5e274a0c882c324e5d1f72f7.scope
│   │ │ │ └─38353 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/vm/numa.rst
│   │ │ ├─app-org.kde.kate-bd04ec663c48458388b9fa5763b21475.scope
│   │ │ │ └─36045 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/tainted-kernels.rst
│   │ │ ├─app-org.kde.kate-701de1e0f47c4040b04c2b14b0736814.scope
│   │ │ │ └─36107 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/perf-security.rst
│   │ │ ├─xdg-permission-store.service
│   │ │ │ └─1877 /usr/libexec/xdg-permission-store
│   │ │ ├─app-\x2fusr\x2fbin\x2fkorgac-fba6fc922f304fd892acdbd09d5c57e6.scope
│   │ │ │ └─2059 /usr/bin/korgac -session 10dfd7e29f000165373856000000016460011_1659082942_32052
│   │ │ ├─xdg-document-portal.service
│   │ │ │ ├─1873 /usr/libexec/xdg-document-portal
│   │ │ │ └─1883 fusermount -o rw,nosuid,nodev,fsname=portal,auto_unmount,subtype=portal -- /run/user/1000/doc
│   │ │ ├─app-org.kde.kate-3c8915e087fd4680ba5fed65f42a4f88.scope
│   │ │ │ └─36427 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/sysctl/vm.rst
│   │ │ ├─app-org.kde.kate-1a49d3c474e34ad283440d3d1298394a.scope
│   │ │ │ └─36893 /usr/bin/kate -b /home/vissol/Downloads/linux-5.19-rc8/Documentation/admin-guide/laptops/laptop-mode.rst
│   │ │ ├─xdg-desktop-portal.service
│   │ │ │ └─1864 /usr/libexec/xdg-desktop-portal
│   │ │ ├─app-org.kde.kate-2b0ef5011a5344989296587e17dde86a.scope
[lines 1-29]
```

Срез (slice) — это группа иерархически организованных юнитов. Срез управляет процессами, которые работают либо в **областях видимости** (scopes), либо в **сервисах** (services). Четыре среза по умолчанию таковы:

* `-.slice`: корневой срез, который является корнем всей иерархии срезов. Обычно он не будет напрямую содержать какие-либо другие юниты. Однако вы можете использовать его для создания настроек по умолчанию для всего дерева срезов.
* `system.slice`: системные сервисы, которые были запущены systemd.
* `user.slice`: сервисы пользовательского режима. Неявный срез назначается каждому вошедшему пользователю.
* `machine-slice`: сервисы, предназначенные для запуска контейнеров или виртуальных машин.

Если вы хотите увидеть пользовательские срезы, вам нужно запустить команду `systemd-cgls` _снаружи_ файловой системы `cgroup`. Если вы сделаете `cd` в директорию `/sys/fs/cgroup/`, вы не увидите пользовательские срезы. Чем дальше вы углубляетесь в файловую систему `cgroup`, тем меньше вы увидите с помощью `systemd-cgls`.

Обозначение `user-1000.slice` соответствует номеру идентификатора пользователя, здесь `1000`.

Когда `systemd-cgls` выполняется без параметров, он возвращает всю иерархию `cgroup`. Высший уровень дерева `cgroup` формируется срезами и может выглядеть следующим образом:

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
> Обратите внимание, что machine slice присутствует только если вы запускаете виртуальную машину или контейнер.

Чтобы сократить вывод `systemd-cgls` и просмотреть определённую часть иерархии, выполните:

```bash
$ systemd-cgls $NAME
```

`$NAME` — это контроллер ресурсов, который вы хотите осмотреть.

Пример: контроллер `memory`:

```text
$ systemd-cgls memory
memory:
├─ 1 /usr/lib/systemd/systemd --switched-root --system --deserialize 23
├─ 475 /usr/lib/systemd/systemd-journald
[...]
```

> Информация
>
> systemd также предоставляет команду `machinectl`, предназначенную для мониторинга Linux-контейнеров.

## Просмотр контроллеров ресурсов процессов

Чтобы узнать, какие контроллеры ресурсов используются какими процессами, вам нужно отобразить выделенный файл процесса:

```bash
$ cat /proc/$PID/cgroup
```

Где PID — это ID процесса, который вы хотите исследовать. По умолчанию список одинаков для всех юнитов, запущенных systemd, поскольку он автоматически монтирует все контроллеры по умолчанию.

Пример:

```text
$ cat proc/27/cgroup
10:hugetlb:/
9:perf_event:/
8:blkio:/
7:net_cls:/
6:freezer:/
5:devices:/
4:memory:/
3:cpuacct,cpu:/
2:cpuset:/
1:name=systemd:/
```

## Мониторинг потребления ресурсов

`systemd-cgtop` предоставляет динамический учёт текущих работающих cgroup, упорядоченных по их использованию ресурсов (CPU, память, ввод-вывод):

```text
$ systemd-cgtop
Control Group                                           Tasks   %CPU   Memory    Input/s Output/s
/                                                       1060   401.1   15.3G     1.0M    0B
user.slice                                               863   376.1   12.4G    -       -
user.slice/user-1000.slice                               863   376.0   12.4G    -       -
user.slice/user-1000.slice/user@1000.service            669   375.1   11.2G    -       -
system.slice                                              84    14.1    2.5G    -       -
system.slice/anacron.service                              5     9.8    1.2G    -       -
system.slice/NetworkManager.service                      7     1.6    13.1M   -       -
system.slice/sddm.service                                12     1.5    136.6M  -       -
system.slice/dbus.service                                1      1.1    5.0M     -       -
user.slice/user-1000.slice/session-3.scope              194    1.0    1.1G     -       -
system.slice/wpa_supplicant.service                      1     0.0    4.0M     -       -
system.slice/pcscd.service                               7     0.0    1.0M     -       -
system.slice/rtkit-daemon.service                        3     0.0    608.0K  -       -
dev-hugepages.mount                                      -      -      8.0K     -       -
init.scope                                               1      -      7.1M     -       -
proc-sys-fs-binfmt_misc.mount                            -      -      4.0K     -       -
sys-fs-fuse-connections.mount                           -      -      4.0K     -       -
sys-kernel-config.mount                                  -      -      4.0K     -       -
system.slice/ModemManager.service                        3      -      3.6M     -       -
system.slice/accounts-daemon.service                     3      -      4.2M     -       -
system.slice/auditd.service                              2      -      3.1M     -       -
system.slice/avahi-daemon.service                        2      -      1.4M     -       -
system.slice/bluetooth.service                           1      -      2.8M     -       -
system.slice/boot-efi.mount                              -      -      20.0K    -       -
system.slice/boot.mount                                  -      -      52.0K    -       -
```

## Дополнительные ресурсы

## Старомодный способ контроля использования ресурсов

До `cgroup` и `systemd` контроль ресурсов был возможен с использованием команды `ulimit` и модуля `pam_limits`. Эти возможности всегда доступны в системах Linux.

## Команда ulimit

`ulimit` — это команда для динамического выделения, внутри shell-сессии, использования ресурсов.

Чтобы увидеть настройки `ulimit` по умолчанию, выполните `ulimit -a`:

```text
vissol@debian:~$ ulimit -a
real-time non-blocking time (microseconds, -R) unlimited
core file size (blocks, -c) 0
data seg size (kbytes, -d) unlimited
scheduling priority (-e) 0
file size (blocks, -f) unlimited
pending signals (-i) 63283
max locked memory (kbytes, -l) 2035929
max memory size (kbytes, -m) unlimited
open files (-n) 1024
pipe size (512 bytes, -p) 8
POSIX message queues (bytes, -q) 819200
real-time priority (-r) 0
stack size (kbytes, -s) 8192
cpu time (seconds, -t) unlimited
max user processes (-u) 63283
virtual memory (kbytes, -v) unlimited
file locks (-x) unlimited
```

> Информация
>
> Изменения `ulimit` сохраняются только на время shell-сессии.
>
> Для снижения ресурсов вам не нужны привилегии, но для повышения ресурсов вам нужен профиль sudoer.

```text
vissol@debian:~$ ulimit -f 20000
-bash: ulimit: file size: cannot modify limit: Operation not permitted
```

`ulimit -a` показывает текущие лимиты, но также и опции для ограничения ресурсов.

Давайте теперь попрактикуемся!

Представьте, что вы хотите ограничить размер любых новых файлов только 10 МБ — вы можете использовать опцию `-f` и количество блоков в байтах:

```bash
ulimit -f 10240
```

После этого, если вы выполните `ulimit -a`, система покажет вам:

```text
vissol@debian:~$ ulimit -a
. . .
. . .
file size (blocks, -f) 10240
. . .
. .
```

В этом случае, если вы захотите создать файл размером 11 МБ, появится ошибка:

```text
vissol@debian:~$ dd if=/dev/zero of=afile bs=1M count=11
File size limit exceeded (core dumped)
```

**********

[cgroup](/tags/cgroup.md)
[linux](/tags/linux.md)