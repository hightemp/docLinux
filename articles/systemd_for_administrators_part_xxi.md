# systemd для администраторов, часть XXI: интеграция с контейнерами

Источник: [systemd For Administrators, Part XXI](https://0pointer.net/blog/systemd-for-administrators-part-xxi.html)

Опубликовано 12 ноября 2014

# Интеграция с контейнерами

Контейнеры уже какое-то время остаются одной из горячих тем в Linux. Менеджеры контейнеров вроде libvirt-lxc, LXC или Docker ныне широко известны и используются. В этом посте я хочу пролить свет на точки интеграции [systemd](http://www.freedesktop.org/wiki/Software/systemd/) с менеджерами контейнеров, позволяющие бесшовно управлять сервисами через границы контейнеров.

Здесь мы сосредоточимся на OS-контейнерах, то есть на случае, когда внутри контейнера работает система инициализации, и потому контейнер в большинстве аспектов выглядит как самостоятельная система. многое из описанного здесь доступно практически в любом менеджере контейнеров, реализующем логику, [описанную здесь](http://www.freedesktop.org/wiki/Software/systemd/ContainerInterface/), включая libvirt-lxc. Однако для простоты мы будем ориентироваться на [systemd-nspawn](http://www.freedesktop.org/software/systemd/man/systemd-nspawn.html) — мини-менеджер контейнеров, поставляемый вместе с самим systemd. systemd-nspawn использует те же интерфейсы ядра, что и другие менеджеры контейнеров, но менее гибок, так как задуман как менеджер контейнеров максимально простой в использовании и работающий «из коробки», а не как универсальный инструмент, настраиваемый в каждой мелочи. Мы активно используем systemd-nspawn при разработке systemd.

В общем, давайте начинать наш обзор. Начнём с создания дерева контейнера Fedora в подкаталоге:

```bash
# yum -y --releasever=20 --nogpg --installroot=/srv/mycontainer --disablerepo='*' --enablerepo=fedora install systemd passwd yum fedora-release vim-minimal
```

Это скачивает минимальную систему Fedora и устанавливает её в `/srv/mycontainer. Эта командная строка специфична для Fedora, но большинство дистрибутивов предоставляет похожую функциональность тем или иным способом. В разделе примеров [man-страницы systemd-nspawn(1)](http://www.freedesktop.org/software/systemd/man/systemd-nspawn.html) содержится список различных командных строк для других дистрибутивов.

Новый контейнер установлен; зададим начальный пароль root:

```text
# systemd-nspawn -D /srv/mycontainer
Spawning container mycontainer on /srv/mycontainer
Press ^] three times within 1s to kill container.
-bash-4.2# passwd
Changing password for user root.
New password:
Retype new password:
passwd: all authentication tokens updated successfully.
-bash-4.2# ^D
Container mycontainer exited successfully.
#
```

Здесь мы используем systemd-nspawn, чтобы получить оболочку внутри контейнера, а затем применяем passwd для установки пароля root. После этого первичная настройка завершена, так что загрузим контейнер и войдём как root с новым паролем:

```text
$ systemd-nspawn -D /srv/mycontainer -b
Spawning container mycontainer on /srv/mycontainer.
Press ^] three times within 1s to kill container.
systemd 208 running in system mode. (+PAM +LIBWRAP +AUDIT +SELINUX +IMA +SYSVINIT +LIBCRYPTSETUP +GCRYPT +ACL +XZ)
Detected virtualization 'systemd-nspawn'.

Welcome to Fedora 20 (Heisenbug)!

[  OK  ] Reached target Remote File Systems.
[  OK  ] Created slice Root Slice.
[  OK  ] Created slice User and Session Slice.
[  OK  ] Created slice System Slice.
[  OK  ] Created slice system-getty.slice.
[  OK  ] Reached target Slices.
[  OK  ] Listening on Delayed Shutdown Socket.
[  OK  ] Listening on /dev/initctl Compatibility Named Pipe.
[  OK  ] Listening on Journal Socket.
         Starting Journal Service...
[  OK  ] Started Journal Service.
[  OK  ] Reached target Paths.
         Mounting Debug File System...
         Mounting Configuration File System...
         Mounting FUSE Control File System...
         Starting Create static device nodes in /dev...
         Mounting POSIX Message Queue File System...
         Mounting Huge Pages File System...
[  OK  ] Reached target Encrypted Volumes.
[  OK  ] Reached target Swap.
         Mounting Temporary Directory...
         Starting Load/Save Random Seed...
[  OK  ] Mounted Configuration File System.
[  OK  ] Mounted FUSE Control File System.
[  OK  ] Mounted Temporary Directory.
[  OK  ] Mounted POSIX Message Queue File System.
[  OK  ] Mounted Debug File System.
[  OK  ] Mounted Huge Pages File System.
[  OK  ] Started Load/Save Random Seed.
[  OK  ] Started Create static device nodes in /dev.
[  OK  ] Reached target Local File Systems (Pre).
[  OK  ] Reached target Local File Systems.
         Starting Trigger Flushing of Journal to Persistent Storage...
         Starting Recreate Volatile Files and Directories...
[  OK  ] Started Recreate Volatile Files and Directories.
         Starting Update UTMP about System Reboot/Shutdown...
[  OK  ] Started Trigger Flushing of Journal to Persistent Storage.
[  OK  ] Started Update UTMP about System Reboot/Shutdown.
[  OK  ] Reached target System Initialization.
[  OK  ] Reached target Timers.
[  OK  ] Listening on D-Bus System Message Bus Socket.
[  OK  ] Reached target Sockets.
[  OK  ] Reached target Basic System.
         Starting Login Service...
         Starting Permit User Sessions...
         Starting D-Bus System Message Bus...
[  OK  ] Started D-Bus System Message Bus.
         Starting Cleanup of Temporary Directories...
[  OK  ] Started Cleanup of Temporary Directories.
[  OK  ] Started Permit User Sessions.
         Starting Console Getty...
[  OK  ] Started Console Getty.
[  OK  ] Reached target Login Prompts.
[  OK  ] Started Login Service.
[  OK  ] Reached target Multi-User System.
[  OK  ] Reached target Graphical Interface.

Fedora release 20 (Heisenbug)
Kernel 3.18.0-0.rc4.git0.1.fc22.x86_64 on an x86_64 (console)

mycontainer login: root
Password:
-bash-4.2#
```

Теперь у нас всё готово, чтобы поиграться с интеграцией контейнеров в systemd. Взглянем на первый инструмент — machinectl. Запущенный без параметров, он показывает список всех локально работающих контейнеров:

```text
$ machinectl
MACHINE                          CONTAINER SERVICE
mycontainer                      container nspawn

1 machines listed.
```

Подкоманда "status" показывает подробности о контейнере:

```text
$ machinectl status mycontainer
mycontainer:
       Since: Mi 2014-11-12 16:47:19 CET; 51s ago
      Leader: 5374 (systemd)
     Service: nspawn; class container
        Root: /srv/mycontainer
     Address: 192.168.178.38
              10.36.6.162
              fd00::523f:56ff:fe00:4994
              fe80::523f:56ff:fe00:4994
          OS: Fedora 20 (Heisenbug)
        Unit: machine-mycontainer.scope
              ├─5374 /usr/lib/systemd/systemd
              └─system.slice
                ├─dbus.service
                │ └─5414 /bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-act...
                ├─systemd-journald.service
                │ └─5383 /usr/lib/systemd/systemd-journald
                ├─systemd-logind.service
                │ └─5411 /usr/lib/systemd/systemd-logind
                └─console-getty.service
                  └─5416 /sbin/agetty --noclear -s console 115200 38400 9600
```

Отсюда мы видим интересную информацию о контейнере, включая его дерево контрольных групп (cgroup) с процессами, IP-адреса и корневой каталог.

Подкоманда "login" даёт нам новую login-оболочку в контейнере:

```text
# machinectl login mycontainer
Connected to container mycontainer. Press ^] three times within 1s to exit session.

Fedora release 20 (Heisenbug)
Kernel 3.18.0-0.rc4.git0.1.fc22.x86_64 on an x86_64 (pts/0)

mycontainer login:
```

Подкоманда "reboot" перезагружает контейнер:

```text
# machinectl reboot mycontainer
```

Подкоманда "poweroff" выключает контейнер:

```text
# machinectl poweroff mycontainer
```

На этом с инструментом machinectl закончим. Инструмент знает ещё несколько команд — подробности смотрите в [man-странице](http://www.freedesktop.org/software/systemd/man/machinectl.html). Ещё раз отметим: хотя здесь мы используем systemd-nspawn как менеджер контейнеров, концепции применимы к любому менеджеру контейнеров, реализующему логику, [описанную здесь](http://www.freedesktop.org/wiki/Software/systemd/writing-vm-managers/), включая, например, libvirt-lxc.

machinectl — не единственный инструмент, полезный в связке с контейнерами. Многие собственные инструменты systemd тоже обновлены с явной поддержкой контейнеров! Попробуем (предварительно снова запустив контейнер, повторив команду systemd-nspawn из выше):

```text
# hostnamectl -M mycontainer set-hostname "wuff"
```

Это использует [hostnamectl(1)](http://www.freedesktop.org/software/systemd/man/hostnamectl.html) на локальном контейнере и устанавливает его имя хоста.

Аналогично обновлены и многие другие инструменты для подключения к локальным контейнерам. Вот в деле переключатель `-M` [systemctl(1)](http://www.freedesktop.org/software/systemd/man/systemctl.html):

```text
# systemctl -M mycontainer
UNIT                                 LOAD   ACTIVE SUB       DESCRIPTION
-.mount                              loaded active mounted   /
dev-hugepages.mount                  loaded active mounted   Huge Pages File System
dev-mqueue.mount                     loaded active mounted   POSIX Message Queue File System
proc-sys-kernel-random-boot_id.mount loaded active mounted   /proc/sys/kernel/random/boot_id
[...]
time-sync.target                     loaded active active    System Time Synchronized
timers.target                        loaded active active    Timers
systemd-tmpfiles-clean.timer         loaded active waiting   Daily Cleanup of Temporary Directories

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

49 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
```

Как и ожидалось, это показывает список активных юнитов указанного контейнера, а не хоста. (Вывод здесь сокращён — пост и так уже слишком длинный.)

Используем это, чтобы перезапустить сервис внутри нашего контейнера:

```text
# systemctl -M mycontainer restart systemd-resolved.service
```

Впрочем, поддержка контейнеров в systemctl не ограничивается переключателем `-M`. С переключателем `-r` он показывает юниты, работающие на хосте, плюс все юниты всех локально работающих контейнеров:

```text
# systemctl -r
UNIT                                        LOAD   ACTIVE SUB       DESCRIPTION
boot.automount                              loaded active waiting   EFI System Partition Automount
proc-sys-fs-binfmt_misc.automount           loaded active waiting   Arbitrary Executable File Formats File Syst
sys-devices-pci0000:00-0000:00:02.0-drm-card0-card0\x2dLVDS\x2d1-intel_backlight.device loaded active plugged   /sys/devices/pci0000:00/0000:00:02.0/drm/ca
[...]
timers.target                                                                                       loaded active active    Timers
mandb.timer                                                                                         loaded active waiting   Daily man-db cache update
systemd-tmpfiles-clean.timer                                                                        loaded active waiting   Daily Cleanup of Temporary Directories
mycontainer:-.mount                                                                                 loaded active mounted   /
mycontainer:dev-hugepages.mount                                                                     loaded active mounted   Huge Pages File System
mycontainer:dev-mqueue.mount                                                                        loaded active mounted   POSIX Message Queue File System
[...]
mycontainer:time-sync.target                                                                        loaded active active    System Time Synchronized
mycontainer:timers.target                                                                           loaded active active    Timers
mycontainer:systemd-tmpfiles-clean.timer                                                            loaded active waiting   Daily Cleanup of Temporary Directories

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

191 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
```

Сначала мы видим юниты хоста, за которыми следуют юниты единственного работающего сейчас контейнера. Юниты контейнеров имеют префикс из имени контейнера и двоеточия (":"). (Вывод снова сокращён ради краткости.)

Подкоманда `list-machines` у systemctl показывает список всех работающих контейнеров, запрашивая у системных менеджеров внутри контейнеров состояние и здоровье системы. Точнее, она показывает, нормально ли контейнеры загрузились и есть ли в них упавшие сервисы:

```text
# systemctl list-machines
NAME         STATE   FAILED JOBS
delta (host) running      0    0
mycontainer  running      0    0
miau         degraded     1    0
waldi        running      0    0

4 machines listed.
```

Для интереса мы параллельно запустили ещё два контейнера. В одном из них есть упавший сервис, из-за чего состояние машины — `degraded`.

Взглянем на поддержку контейнеров в [journalctl(1)](http://www.freedesktop.org/software/systemd/man/journalctl.html). Он тоже поддерживает `-M` для показа логов конкретного контейнера:

```text
# journalctl -M mycontainer -n 8
Nov 12 16:51:13 wuff systemd[1]: Starting Graphical Interface.
Nov 12 16:51:13 wuff systemd[1]: Reached target Graphical Interface.
Nov 12 16:51:13 wuff systemd[1]: Starting Update UTMP about System Runlevel Changes...
Nov 12 16:51:13 wuff systemd[1]: Started Stop Read-Ahead Data Collection 10s After Completed Startup.
Nov 12 16:51:13 wuff systemd[1]: Started Update UTMP about System Runlevel Changes.
Nov 12 16:51:13 wuff systemd[1]: Startup finished in 399ms.
Nov 12 16:51:13 wuff sshd[35]: Server listening on 0.0.0.0 port 24.
Nov 12 16:51:13 wuff sshd[35]: Server listening on :: port 24.
```

Однако он поддерживает и `-m` — для показа объединённого потока логов хоста и всех локальных контейнеров:

```text
# journalctl -m -e
```

(Вывод здесь полностью пропустим — полагаю, вы можете сами представить, как он выглядит.)

Но контейнерную поддержку ныне понимают не только собственные инструменты systemd — procps тоже добавил её:

```text
# ps -eo pid,machine,args
 PID MACHINE                         COMMAND
    1 -                               /usr/lib/systemd/systemd --switched-root --system --deserialize 20
[...]
 2915 -                               emacs contents/projects/containers.md
 3403 -                               [kworker/u16:7]
 3415 -                               [kworker/u16:9]
 4501 -                               /usr/libexec/nm-vpnc-service
 4519 -                               /usr/sbin/vpnc --non-inter --no-detach --pid-file /var/run/NetworkManager/nm-vpnc-bfda8671-f025-4812-a66b-362eb12e7f13.pid -
 4749 -                               /usr/libexec/dconf-service
 4980 -                               /usr/lib/systemd/systemd-resolved
 5006 -                               /usr/lib64/firefox/firefox
 5168 -                               [kworker/u16:0]
 5192 -                               [kworker/u16:4]
 5193 -                               [kworker/u16:5]
 5497 -                               [kworker/u16:1]
 5591 -                               [kworker/u16:8]
 5711 -                               sudo -s
 5715 -                               /bin/bash
 5749 -                               /home/lennart/projects/systemd/systemd-nspawn -D /srv/mycontainer -b
 5750 mycontainer                     /usr/lib/systemd/systemd
 5799 mycontainer                     /usr/lib/systemd/systemd-journald
 5862 mycontainer                     /usr/lib/systemd/systemd-logind
 5863 mycontainer                     /bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
 5868 mycontainer                     /sbin/agetty --noclear --keep-baud console 115200 38400 9600 vt102
 5871 mycontainer                     /usr/sbin/sshd -D
 6527 mycontainer                     /usr/lib/systemd/systemd-resolved
[...]
```

Это (сокращённый) список процессов. Вторая колонка показывает, к какому контейнеру принадлежит процесс. Все процессы, показанные с "-", принадлежат самому хосту.

На этом дело не заканчивается. Новая клиентская D-Bus-библиотека "sd-bus", которую мы готовим в контексте systemd/kdbus, тоже знает о контейнерах. Если `sd_bus_open_system()` используется для подключения к системной шине локального хоста, то [`sd_bus_open_system_container()`](http://www.freedesktop.org/software/systemd/man/sd_bus_open_system_container.html) можно использовать для подключения к системной шине любого локального контейнера, чтобы вызывать методы шины на нём.

[`sd-login.h`](http://www.freedesktop.org/software/systemd/man/sd_pid_get_machine_name.html) и [D-Bus-интерфейс machined](http://www.freedesktop.org/wiki/Software/systemd/machined/) предоставляют ряд API для добавления поддержки контейнеров и в другие программы. Они поддерживают перечисление контейнеров, а также получение имени машины по PID и подобное.

systemd-networkd тоже имеет поддержку контейнеров. Запущенный внутри контейнера, он по умолчанию запускает DHCP-клиент и IPv4LL на любом сетевом интерфейсе veth с именем `host0` (этот интерфейс особый в рамках логики, описанной [здесь](http://www.freedesktop.org/wiki/Software/systemd/ContainerInterface/)). Запущенный на хосте, networkd по умолчанию предоставляет DHCP-сервер и IPv4LL на сетевом интерфейсе veth с именем `ve-`, за которым следует имя контейнера.

Взглянем на последний аспект интеграции контейнеров в systemd: стыковку с механизмом переключения имён (name service switch, NSS). Свежие версии systemd содержат новый NSS-модуль nss-mymachines, который делает имена всех локальных контейнеров разрешаемыми через `gethostbyname()` и [`getaddrinfo()`](http://man7.org/linux/man-pages/man3/getaddrinfo.3.html). Это применимо только к контейнерам, работающим в собственном сетевом namespace. С показанной выше командой systemd-nspawn контейнер, однако, делит сетевую конфигурацию с хостом; поэтому перезапустим контейнер, на этот раз с виртуальным сетевым каналом `veth` между хостом и контейнером:

```text
# machinectl poweroff mycontainer
# systemd-nspawn -D /srv/mycontainer --network-veth -b
```

Теперь (при условии, что networkd используется и в контейнере, и снаружи) мы уже можем пинговать контейнер по его имени — благодаря простой магии nss-mymachines:

```text
# ping mycontainer
PING mycontainer (10.0.0.2) 56(84) bytes of data.
64 bytes from mycontainer (10.0.0.2): icmp_seq=1 ttl=64 time=0.124 ms
64 bytes from mycontainer (10.0.0.2): icmp_seq=2 ttl=64 time=0.078 ms
```

Разумеется, разрешение имён работает не только с `ping` — оно работает и со всеми остальными инструментами, использующими libc `gethostbyname()` или `getaddrinfo()`, включая почтенный `ssh`.

И это практически всё, что я хотел сейчас охватить. Мы кратко коснулись множества точек интеграции, а если присмотреться, есть ещё многое. Мы постоянно работаем над ещё большей интеграцией контейнеров, так что ожидайте новых возможностей в этой области с каждым релизом systemd.

Отмечу, что вся концепция _машин_ (machine) на самом деле не ограничена контейнерами, а в определённой степени охватывает и виртуальные машины. Однако интеграция с ними не столь тесная, поскольку доступ к внутренностям ВМ не так прост, как к контейнерам: обычно он требует сетевой передачи вместо прямого доступа через системные вызовы.

Надеюсь, это было полезно. Подробнее смотрите по ссылкам на man-страницы и прочую документацию.

**********

[systemd](/tags/systemd.md)
[linux](/tags/linux.md)