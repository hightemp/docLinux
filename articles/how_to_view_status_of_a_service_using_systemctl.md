# Как просмотреть статус службы с помощью systemctl

Источник: [Stop dance for nginx](https://www.cyberciti.biz/faq/systemd-systemctl-view-status-of-a-service-on-linux/)

Автор: Vivek Gite

Как использовать команду systemctl для просмотра статуса службы systemd в операционных системах Linux?

Мы используем команду **systemctl status** в **systemd** для просмотра статуса заданной службы в операционных системах Linux.

| Детали руководства |  |
| --- | --- |
| Уровень сложности | [Лёгкий (Easy)](https://www.cyberciti.biz/faq/tag/easy/ "Все лёгкие руководства для системных администраторов Linux/Unix") |
| Требуются права root | [Да](https://www.cyberciti.biz/faq/how-can-i-log-in-as-root/ "See how to login as root user") |
| Требования | Терминал Linux |
| Категория | [Управление системой](https://www.cyberciti.biz/faq/systemd-systemctl-view-status-of-a-service-on-linux/#System_Management "See ALL other tutorials in 'System Management' category") |
| Необходимые условия | systemd |
| Совместимость с ОС | AlmaLinux • [Arch](https://www.cyberciti.biz/faq/category/arch-linux/ "See all Arch Linux tutorials") • [Debian](https://www.cyberciti.biz/faq/category/debian-ubuntu/ "See all Debian Linux tutorials") • [Fedora](https://www.cyberciti.biz/faq/category/fedora-linux/ "See all Fedora Linux Enterprise tutorials") • [Linux](https://www.cyberciti.biz/faq/category/linux/ "See all Linux distributions tutorials") • Mint • [openSUSE](https://www.cyberciti.biz/faq/tag/opensuse/ "See all openSUSE Linux Enterprise tutorials") • Pop!_OS • [RHEL](https://www.cyberciti.biz/faq/category/redhat-and-friends/ "See all RHEL (Red Hat Enterprise Linux) tutorials") • Rocky • [Stream](https://www.cyberciti.biz/faq/tag/centos-stream/ "See all CentOS Stream Linux tutorials") • [SUSE](https://www.cyberciti.biz/faq/category/suse/ "See all SUSE Linux Enterprise tutorials") • [Ubuntu](https://www.cyberciti.biz/faq/category/ubuntu-linux/ "See all Ubuntu Linux tutorials") • WSL |
| Примерное время чтения | 9 минут |

## Просмотр статуса службы

Синтаксис команды systemctl следующий:

```bash
$ systemctl status {service-name}
$ systemctl status {unit-name}
```

Обратите внимание, что команда systemctl status {service-name} заменяет команду service {service-name} status, которая использовалась в более ранних версиях Linux без systemd.

### Как просмотреть статус службы с именем nginx

Введите следующую команду, чтобы увидеть статус Nginx, Sshd и Lighttpd:

```bash
$ systemctl status nginx.service
## статус ssh сервера ##
$ systemctl status sshd.service
## статус веб-сервера Lighttpd ##
$ systemctl status lighttpd.service
```

```text
● lighttpd.service - Lighttpd Daemon
     Loaded: loaded (/lib/systemd/system/lighttpd.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2020-08-04 04:29:19 UTC; 3 weeks 2 days ago
   Main PID: 105 (lighttpd)
      Tasks: 1 (limit: 115783)
     Memory: 56.5M
     CGroup: /system.slice/lighttpd.service
             └─105 /usr/sbin/lighttpd -D -f /etc/lighttpd/lighttpd.conf

Aug 04 04:29:19 utls-bash-wiki systemd[1]: Starting Lighttpd Daemon...
Aug 04 04:29:19 utls-bash-wiki systemd[1]: Started Lighttpd Daemon.
```

Точка («●») использует цвет на поддерживаемых терминалах, чтобы суммировать состояние юнита с одного взгляда. Белый цвет указывает на состояние «inactive» (неактивно) или «deactivating» (деактивация). Красный цвет указывает на состояние «failed» (сбой) или «error» (ошибка). Зелёный указывает на состояние «active» (активно), «reloading» (перезагрузка) или «activating» (активация).

### Понимание состояний служб/юнитов systemd

Статус службы Linux зависит от различных состояний, таких как следующие:

Табл. 1: Состояние службы (прокрутите таблицу)
| Статус службы | Описание |
| --- | --- |
| active (running) | Служба или демон работает в фоне. Например, sshd или веб-сервер nginx/apache, ожидающий входящий трафик. |
| active (exited) | Служба успешно запущена из конфигурационного файла. Обычно это разовые службы, конфигурация которых считывается до выхода из службы. Например, AppArmor или служба файрвола. |
| active (waiting) | Наша служба работает, но ожидает события, например события CPU/печати. |
| inactive | Служба не работает. |
| enabled | Служба включена при загрузке. |
| disabled | Служба выключена (disabled) и не будет запущена при загрузке Linux-сервера. |
| static | Службу нельзя включить в Linux, но по большей части она автоматически запускается другим юнитом systemd. Другими словами, файл юнита не включён и не имеет положений, разрешающих это, в секции [Install] файла юнита. |
| masked | Служба полностью отключена, и любая операция запуска на ней всегда завершается ошибкой. |
| alias | Имя службы — это псевдоним (alias). Это означает, что служба является симлинком на другой файл юнита. |
| linked | Сделана доступной через один или несколько симлинков на файл юнита (постоянно в /etc/systemd/system/ или временно в /run/systemd/system/), даже если сам файл юнита может находиться вне пути поиска файлов юнитов. |

### В настоящее время systemd поддерживает следующие юниты

* **service** : конфигурация юнита-службы для процесса, контролируемого и сопровождаемого systemd.
* **mount** : точка монтирования файловой системы, контролируемая и сопровождаемая systemd.
* **swap** : конфигурация swap-файла/диска, контролируемая systemd.
* **socket** : сокет IPC или сетевой сокет, либо FIFO файловой системы, контролируемые и сопровождаемые systemd, для активации по сокету.
* **target** : содержит информацию о целевом юните (target unit) systemd. Используется для группировки юнитов и как известные точки синхронизации при запуске. Например, graphical.target используется для входа в графический рабочий стол. Аналогично, multi-user.target используется серверами, куда пользователи входят по ssh/консоли.
* **device** : юнит устройства, представленный в дереве устройств sysfs/udev. Включает сетевые и другие устройства.
* **automount** : автоматическое монтирование файловых систем.
* **timer** : похожий на cron юнит systemd для запуска команд и служб в заданном формате даты/времени. Например, обновление прошивки или очистка сессий, созданных веб-приложениями Python или PHP.
* **path** : специальный целевой юнит systemd, который настраивает все path-юниты. Например, systemd может выполнять определённые действия в зависимости от пути в файловой системе. Если /etc/foo/ изменён, выполнить какое-то действие.
* **slice** : мы используем slice systemd для изоляции рабочих нагрузок. Они определяют иерархию, в которую помещаются scope и службы. Сами процессы содержатся в scope или в службах. Думайте об этом как о лёгком Docker. Для каждого slice могут быть установлены определённые ограничения ресурсов, такие как лимит CPU или дискового ввода-вывода, которые применяются ко всем процессам.
* **scope** : юниты scope не настраиваются через файлы конфигурации юнитов, а создаются только программно через шинные интерфейсы systemd. Они именуются подобно именам файлов. Юнит, чьё имя заканчивается на «.scope», относится к scope-юниту. Юниты scope управляют набором системных процессов. В отличие от юнитов служб, юниты scope управляют процессами, созданными извне, и сами не порождают процессы. Главная цель юнитов scope — группировка рабочих процессов системной службы для организации и управления ресурсами.

Мы можем перечислить все юниты-службы следующим образом:

```bash
$ sudo systemctl --type=service
```

Хотите увидеть юниты типа mount? Попробуйте:

```bash
$ sudo systemctl --type=mount
```

Показать все юниты-таймеры systemd на вашей Linux-машине:

```bash
$ sudo systemctl -t timer
```

```text
  UNIT                         LOAD   ACTIVE SUB     DESCRIPTION
____________________________________________________________________________________________________________
  anacron.timer                loaded active waiting Trigger anacron every hour
  apt-daily-upgrade.timer      loaded active waiting Daily apt upgrade and clean activities
  apt-daily.timer              loaded active waiting Daily apt download activities
  e2scrub_all.timer            loaded active waiting Periodic ext4 Online Metadata Check for All Filesystems
  fstrim.timer                 loaded active waiting Discard unused blocks once a week
  fwupd-refresh.timer          loaded active waiting Refresh fwupd metadata regularly
  logrotate.timer              loaded active waiting Daily rotation of log files
  man-db.timer                 loaded active waiting Daily man-db regeneration
  mdcheck_start.timer          loaded active waiting MD array scrubbing
  mdmonitor-oneshot.timer      loaded active waiting Reminder for degraded MD arrays
  motd-news.timer              loaded active waiting Message of the Day
  phpsessionclean.timer        loaded active waiting Clean PHP session files every 30 mins
  systemd-tmpfiles-clean.timer loaded active waiting Daily Cleanup of Temporary Directories

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

13 loaded units listed. Pass --all to see loaded but inactive units, too.
```

### Чтобы показать все установленные файлы юнитов, используйте:

```bash
$ sudo systemctl list-unit-files
```

![Linux: перечисление файлов юнитов с помощью команды systemctl](/images/ab996e41b00644b779cfdda0a3289356.png)

## Просмотр статуса службы в Linux

Введите следующую команду, чтобы просмотреть статусы всех служб и юнитов в вашей Linux-системе с момента загрузки:

```bash
$ sudo systemctl
```

[![Linux: просмотр состояния всех юнитов для проверки запуска системы](/images/3cab39effb96499edecc59ac961798e0.png)](https://www.cyberciti.biz/media/new/faq/2020/08/Linux-see-state-of-all-units-to-verify-a-system-startup.png)

Кликните для увеличения

Используйте [команду grep](https://www.cyberciti.biz/faq/howto-use-grep-command-in-linux-unix/ "How to use grep command In Linux / UNIX with examples")/[команду egrep](https://www.cyberciti.biz/faq/grep-regular-expressions/ "Regular expressions in grep ( regex ) with examples") для фильтрации нужных юнитов/служб:

```bash
$ sudo systemctl | grep ssh
$ sudo systemctl | egrep 'apache|nginx|lighttpd|php'
```

![Как просмотреть статус службы в Linux с помощью systemctl](/images/5f673adfb3d21c417b46442f0b229072.png)

### Как перечислить юниты, которые systemd сейчас держит в памяти

Выполните следующую команду:

```bash
$ sudo systemctl list-units
$ sudo systemctl list-units | more
$ sudo systemctl list-units | grep sshd
## фильтрация по типам юнитов ##
$ sudo systemctl list-units --type service
$ sudo systemctl list-units --type timer
```

### [Перечислить все упавшие юниты/службы systemd/systemctl в Linux](https://www.cyberciti.biz/faq/systemd-systemctl-list-all-failed-units-services-on-linux/)

```bash
$ sudo systemctl list-units --failed
$ sudo systemctl list-units --state failed
## фильтрация по типу юнита ##
$ sudo systemctl list-units --state failed --type service
$ sudo systemctl list-units --state failed --type timer
```

![Команда Linux systemctl для вывода списка всех упавших юнитов или служб](/images/ef6c22f47829ca076b896405d4bd2ba7.png)

Опции команды systemctl для вывода списка всех упавших юнитов/служб

## Что делать, если служба, например nginx, не работает?

Включите службу systemd:

```bash
$ sudo systemctl enable nginx.service
```

Запустите службу nginx:

```bash
$ sudo systemctl start nginx.service
```

Мы можем остановить или перезапустить службу так:

```bash
$ sudo systemctl stop nginx.service
$ sudo systemctl restart nginx.service
```

Проверить, включена ли служба, можно так:

```bash
$ sudo systemctl is-enabled nginx.service
```

Снова посмотреть статус:

```bash
$ sudo systemctl status nginx.service
```

Чтобы увидеть полные выводы для отладки проблемы со службой, передайте опцию --full или -l:

```bash
$ sudo systemctl status nginx.service -l
$ sudo systemctl status openvpn.service --full
```

Мы можем отладить и увидеть все сообщения журнала, связанные со службой, с помощью команды journalctl:

```bash
$ sudo journalctl UNIT=nginx.service
```

```text
Aug 02 03:51:05 utls-wp-mg-www-cbz systemd[1]: Stopped A high performance web server and a reverse proxy server.
Aug 02 03:51:15 utls-wp-mg-www-cbz systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 02 03:51:15 utls-wp-mg-www-cbz systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Aug 02 03:51:15 utls-wp-mg-www-cbz systemd[1]: nginx.service: Failed with result 'exit-code'.
Aug 02 03:51:15 utls-wp-mg-www-cbz systemd[1]: Failed to start A high performance web server and a reverse proxy server.
Aug 02 03:51:48 utls-wp-mg-www-cbz systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 02 03:51:48 utls-wp-mg-www-cbz systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Aug 02 03:51:48 utls-wp-mg-www-cbz systemd[1]: nginx.service: Failed with result 'exit-code'.
Aug 02 03:51:48 utls-wp-mg-www-cbz systemd[1]: Failed to start A high performance web server and a reverse proxy server.
Aug 02 03:52:07 utls-wp-mg-www-cbz systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 02 03:52:07 utls-wp-mg-www-cbz systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Aug 02 03:52:07 utls-wp-mg-www-cbz systemd[1]: nginx.service: Failed with result 'exit-code'.
Aug 02 03:52:07 utls-wp-mg-www-cbz systemd[1]: Failed to start A high performance web server and a reverse proxy server.
Aug 02 03:53:05 utls-wp-mg-www-cbz systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 02 03:53:05 utls-wp-mg-www-cbz systemd[1]: Started A high performance web server and a reverse proxy server.
Aug 04 04:11:47 utls-wp-mg-www-cbz systemd[1]: Stopping A high performance web server and a reverse proxy server...
Aug 04 04:11:48 utls-wp-mg-www-cbz systemd[1]: nginx.service: Succeeded.
Aug 04 04:11:48 utls-wp-mg-www-cbz systemd[1]: Stopped A high performance web server and a reverse proxy server.
-- Reboot --
Aug 04 04:27:35 utls-wp-mg-www-cbz systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 04 04:27:35 utls-wp-mg-www-cbz systemd[1]: Started A high performance web server and a reverse proxy server.
```

## Как просмотреть исходный файл юнита службы systemd

Передайте опцию cat следующим образом (это похоже на [команду cat](https://www.cyberciti.biz/faq/linux-unix-appleosx-bsd-cat-command-examples/ "cat Command in Linux / Unix with examples")):

```bash
$ sudo systemctl cat {service-name}
$ sudo systemctl cat nginx.service
```

```ini
 /lib/systemd/system/nginx.service
# Stop dance for nginx
# =======================
#
# ExecStop sends SIGSTOP (graceful stop) to the nginx process.
# If, after 5s (--retry QUIT/5) nginx is still running, systemd takes control
# and sends SIGTERM (fast shutdown) to the main process.
# After another 5s (TimeoutStopSec=5), and if nginx is alive, systemd sends
# SIGKILL to all the remaining processes in the process group (KillMode=mixed).
#
# nginx signals reference doc:
# http://nginx.org/en/docs/control.html
#
[Unit]
Description=A high performance web server and a reverse proxy server
Documentation=man:nginx(8)
After=network.target
 
[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t -q -g 'daemon on; master_process on;'
ExecStart=/usr/sbin/nginx -g 'daemon on; master_process on;'
ExecReload=/usr/sbin/nginx -g 'daemon on; master_process on;' -s reload
ExecStop=-/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid
TimeoutStopSec=5
KillMode=mixed
 
[Install]
WantedBy=multi-user.target
```

## Заключение

Вы узнали о перечислении юнитов systemd, включая службы Linux, с помощью команды systemctl. См. [документацию systemctl](https://www.freedesktop.org/software/systemd/man/systemctl.html) или введите следующую [команду man](https://bash.cyberciti.biz/guide/Man_command "Man command - Linux Bash Shell Scripting Tutorial Wiki") или передайте [--help в systemctl](https://bash.cyberciti.biz/guide/Help_command "help command - Linux Bash Shell Scripting Tutorial Wiki"):

```bash
$ man systemctl
$ systemctl --help
```

**********

[systemd](/tags/systemd.md)
[linux](/tags/linux.md)
[logs](/tags/logs.md)