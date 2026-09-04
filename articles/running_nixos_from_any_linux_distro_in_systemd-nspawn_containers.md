# Запуск NixOS из любого дистрибутива Linux в контейнерах systemd-nspawn

Источник: [Running NixOS from any Linux Distro in systemd-nspawn Containers](https://nixcademy.com/posts/nixos-nspawn/)

Jacek Galowicz · 29 августа 2023 · 10 мин

![Запуск NixOS из любого дистрибутива Linux в контейнерах systemd-nspawn](/images/6a8cd9d814ad76573cbcdbc5c9c623ba.png)

*Изображение сгенерировано ИИ. Контент написан человеком.*

Когда показываешь Nix или NixOS новичкам, первым порывом часто бывает запустить [образ NixOS для Docker](https://hub.docker.com/r/nixos/nix) на [Docker](https://www.docker.com/) или [Podman](https://podman.io/). На этой неделе мы рассмотрим, как сделать то же самое с помощью средства [systemd](https://systemd.io/) `systemd-nspawn` через команду `machinectl`. Как мы увидим, это даёт огромные преимущества как для пробного знакомства с NixOS, так и для профессионального использования её наподобие сайдкар-VM. Если вы используете Ubuntu, Debian, Fedora, Rocky Linux или что-то подобное — присоединяйтесь!

## Что не так с Docker?

Кто-то может сначала спросить: «А что не так с Docker или Podman?» — при пробе или использовании Nix(OS) через Docker есть несколько минусов:

Поскольку изменения в образах Docker не являются постоянными, нам приходится создавать собственный [`Dockerfile`](https://docs.docker.com/engine/reference/builder/), чтобы сделать изменения в контейнере постоянными, — или вручную клонировать запущенный образ. С установкой нескольких пакетов это начало выглядит нормально. Но при разработке в этом контейнере nix store заполняется скачанными и собранными пакетами — только чтобы быть выброшенным при следующем перезапуске контейнера. Это приводит к повторяющимся долгим временам сборки, хотя Nix известен своей прекрасной кэширующей функцией ускорения сборки! Обе системы, похоже, не были созданы друг для друга.

В дополнение к этому, NixOS поставляется с прекрасными средствами, которые позволяют легко настраивать несколько systemd-юнитов для каждого сервиса, индивидуально ограничивать их безопасной конфигурацией и заставлять их работать вместе. У Docker/Podman совершенно другая философия: каждый контейнер запускает ровно один процесс, а затем они объединяются через [docker-compose](https://docs.docker.com/compose/).

Хотя это в целом нормально и хорошо интегрировано в Nix-инструмент [`arion`](https://docs.hercules-ci.com/arion/), компромисс в том, что NixOS используется лишь за ради своей огромной коллекции пакетов, а её сила — композируемая конфигурация системы — остаётся неиспользованной.

## Альтернатива: systemd-nspawn

Если вы читаете это на машине GNU/Linux, крайне высока вероятность, что это средство у вас было установлено ещё до Docker или Podman: уже довольно давно `systemd` поставляется с командой `systemd-nspawn`, которая имеет некоторое сходство с куда более старой командой [`chroot`](https://en.wikipedia.org/wiki/Chroot). `systemd-nspawn` принимает путь к корню файловой системы другого дистрибутива Linux и, как и Docker/Podman, запускает внутри него новый процесс. Иллюзия того, что новый процесс живёт внутри файловой системы совершенно другого дистрибутива Linux, и отсутствие всех остальных процессов хоста, включая новое имя хоста, создаются с помощью [пространств имён Linux (Linux namespaces)](https://en.wikipedia.org/wiki/Linux_namespaces).

![Официальный логотип systemd](/images/4d68141837f447c21b6afa80eef4c0b9.png)

Хотя большинство Linux-технологий контейнеризации используют пространства имён, `systemd-nspawn` идёт на шаг дальше и запускает обычный процесс `systemd`, который затем создаёт собственное _дерево_ процессов внутри контейнера. Благодаря этому внутри контейнера не ощущается как одиночный процесс, работающий в файловой системе другого дистрибутива, — это по сути собственный полноценный GNU/Linux с сервисами, но без своего ядра.

## Запуск nspawn-образа NixOS

Давайте посмотрим на подготовленный [репозиторий на GitHub с nspawn-образом NixOS](https://github.com/tfc/nspawn-nixos), который попробовать почти так же просто, как образ NixOS для Docker. Если у вас установлена команда `machinectl`, вы можете приступить к следующим шагам без какой-либо дополнительной подготовки!

Вместе с `systemd-nspawn` поставляется команда `machinectl`, которая является удобной обёрткой, позволяющей легко скачивать nspawn-образы из интернета и запускать их наподобие сервисов. Запустить этот образ с помощью `machinectl` почти так же легко, как образы Docker:

Сначала мы выполняем `pull-tar` для скачивания образа из интернета. Затем мы его `start` — это запускает его в фоне. Обратите внимание, что команды `machinectl` нужно выполнять от root:

```bash
machinectl pull-tar https://github.com/tfc/nspawn-nixos/releases/latest/download/nixos-system-x86_64-linux.tar.xz nixos --verify=no
machinectl start nixos
```

> Аргумент `--verify=no` необходим, потому что по этому URL нет ни подписи, ни выложенного файла `SHA256SUMS`. Это задача на другой день.

В этом конкретном образе не задан пароль root, что мы можем сделать с помощью `passwd`. Наконец, мы можем открыть root-shell с помощью подкоманды `login` команды `machinectl`:

```bash
machinectl shell nixos /usr/bin/env passwd
machinectl login nixos
```

Разница между `machinectl shell` и `machinectl login` в том, что подкоманда `shell` просто запускает процесс внутри пространства имён нашего контейнера, тогда как `login` действительно выполняет вход в систему контейнера.

После использования `machine login ...` для входа в контейнер «соединение» с контейнером можно закрыть, нажав `<ctrl> + ]` три раза.

Если вы не хотите пробовать это прямо сейчас, посмотрите на этот скриншот, чтобы понять, как это выглядит:

![Скачивание и запуск NixOS в виде systemd-nspawn-образа — быстро и просто!](/images/51017abf3baf5ee0dd8cedb0cffe2e24.png)

Выполнение этих команд не выглядит чем-то впечатляющим, хотя система в контейнере _загружается_ крайне быстро. `machinectl status nixos` показывает нам статус загруженного образа. Здесь мы можем наблюдать, что в контейнере работает целое **дерево** процессов — что сильно отличается от стандартного использования образов Docker:

```text
# machinectl status nixos
nixos(e2bb44c36c4246049d7eff6cb6e10d7d)
           Since: Mon 2023-08-28 21:38:23 CEST; 36s ago
          Leader: 741701 (systemd)
         Service: systemd-nspawn; class container
            Root: /var/lib/machines/nixos
           Iface: ve-nixos
              OS: NixOS 23.11 (Tapir)
        UID Shift: 819658752
            Unit: systemd-nspawn@nixos.service
                  ├─payload
                  │ ├─init.scope
                  │ │ └─741701 /run/current-system/systemd/lib/systemd/systemd
                  │ └─system.slice
                  │   ├─console-getty.service
                  │   │ └─742127 agetty --login-program /nix/store/hlzi9rwycvpf907r5jhhl6v7090108sc-shadow-4.13/bin/login --noclear --keep-baud console 115200,38400,9600 vt220
                  │   ├─dbus.service
                  │   │ └─742084 /nix/store/ai87d2awsm4xasaly144cjwk2k2b815l-dbus-1.14.8/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
                  │   ├─dhcpcd.service
                  │   │ ├─742016 "dhcpcd: [manager] [ip4] [ip6]"
                  │   │ ├─742017 "dhcpcd: [privileged proxy]"
                  │   │ ├─742018 "dhcpcd: [network proxy]"
                  │   │ └─742019 "dhcpcd: [control proxy]"
                  │   ├─nscd.service
                  │   │ └─742012 /nix/store/nd4yn9v9561ss4xcpr9166n02pddb0cg-nsncd-unstable-2022-11-14/bin/nsncd
                  │   ├─systemd-journald.service
                  │   │ └─741925 /nix/store/sabybrrms75zv55a3nx2qsfyp9h5jbr3-systemd-253.6/lib/systemd/systemd-journald
                  │   └─systemd-logind.service
                  │     └─742040 /nix/store/sabybrrms75zv55a3nx2qsfyp9h5jbr3-systemd-253.6/lib/systemd/systemd-logind
                  └─supervisor
                    └─741695 systemd-nspawn --quiet --keep-unit --boot --link-journal=try-guest --network-veth -U --settings=override --machine=nixos

Aug 28 21:38:23 jongepad systemd-nspawn[741695]: [  OK  ] Reached target Network.
Aug 28 21:38:23 jongepad systemd-nspawn[741695]:          Starting Permit User Sessions...
Aug 28 21:38:23 jongepad systemd-nspawn[741695]: [  OK  ] Finished Permit User Sessions.
Aug 28 21:38:23 jongepad systemd-nspawn[741695]: [  OK  ] Started Console Getty.
Aug 28 21:38:23 jongepad systemd-nspawn[741695]: [  OK  ] Reached target Login Prompts.
Aug 28 21:38:29 jongepad systemd-nspawn[741695]:
Aug 28 21:38:29 jongepad systemd-nspawn[741695]:
Aug 28 21:38:29 jongepad systemd-nspawn[741695]: <<< Welcome to NixOS 23.11.20230826.5237477 (x86_64) - console >>>
Aug 28 21:38:29 jongepad systemd-nspawn[741695]:
Aug 28 21:38:29 jongepad systemd-nspawn[741695]:
```

Потребление ресурсов и так невелико, но если мы захотим его приостановить, можно выполнить `machinectl stop nixos`. Если он нам больше не нравится, можно даже выполнить `machinectl remove nixos`. Машину также можно настроить на автоматический запуск при каждой загрузке с помощью `machinectl enable nixos`.

## Дополнительная настройка

Что ещё можно сделать дальше? Мы можем использовать её как любую другую машину NixOS: устанавливать пакеты, настраивать сервисы и т.д., но перед этим нам, возможно, нужно разрешить контейнеру доступ в интернет. Мы также можем настроить обмен файлами между хостом и контейнером.

### Доступ в интернет

Нам может понадобиться доступ в интернет, для чего systemd предоставляет разные способы. Простейший способ включить доступ в интернет — поделиться сетью хоста с контейнером. Для этого просто создайте конфигурационный файл `/etc/systemd/nspawn/nixos.nspawn` со следующим содержимым:

```ini
[Network]
VirtualEthernet=no
```

Или используйте эту однострочную команду shell:

```bash
printf "[Network]\nVirtualEthernet=no" > /etc/systemd/nspawn/nixos.nspawn
```

После изменения этого конфигурационного файла нам нужно один раз выполнить `machinectl reboot nixos`.

Что касается проброса портов, нам ничего делать не нужно: все порты, которые мы открываем в контейнере, открыты и на хосте, поскольку это одни и те же порты. Единственное ограничение — мы не можем открыть в контейнере порты меньше 1024. Мы можем подключаться по `localhost` как из контейнера к хосту, так и наоборот.

Более сложные сетевые конфигурации допускают более тонкие настройки. См. также [раздел _Network_ документации по формату конфигурационного файла `systemd.nspawn`](https://man7.org/linux/man-pages/man5/systemd.nspawn.5.html#%5BNETWORK%5D_SECTION_OPTIONS).

### Конфигурация NixOS

Теперь мы можем редактировать конфигурационный файл NixOS `/etc/nixos/configuration.nix` в файловой системе контейнера. Мы можем делать это как изнутри контейнера, так и с хоста, поскольку все пути контейнера находятся ниже `/var/lib/machines/<имя машины>`. Для конфигурационного файла полный путь с хоста — `/var/lib/machines/nixos/etc/nixos/configuration.nix`.

После каждого изменения конфигурации мы обычно выполняем `nixos-rebuild switch`, чтобы пересобрать систему на манер nix и активировать новую конфигурацию. Это ощущается почти как настоящая система.

Давайте быстро настроим веб-сервер, добавив две строки в `/etc/nixos/configuration.nix`:

```nix
{ pkgs, modulesPath, ... }:

{
  # ...rest of the config is truncated for clarity...

  services.nginx = {
    enable = true;
    virtualHosts.default.listen = [ { port = 9000; addr="0.0.0.0"; } ];
  };
}
```

Затем пересоберём систему:

```text
[root@nixos:~]# nixos-rebuild switch
warning: creating lock file '/etc/nixos/flake.lock'
building the system configuration...
stopping the following units: nscd.service, resolvconf.service
NOT restarting the following changed units: console-getty.service, container-getty@1.service, systemd-journal-flush.service, systemd-logind.service, systemd-update-utmp.service, systemd-user-sessions.service, user-runtime-dir@0.service, user@0.service
activating the configuration...
mount: /dev: permission denied.
       dmesg(1) may have more information after failed mount system call.
mount: /dev/pts: permission denied.
       dmesg(1) may have more information after failed mount system call.
mount: /dev/shm: permission denied.
       dmesg(1) may have more information after failed mount system call.
mount: /run: permission denied.
       dmesg(1) may have more information after failed mount system call.
Activation script snippet 'specialfs' failed (32)
setting up /etc...
restarting systemd...
reloading user units for root...
setting up tmpfiles
reloading the following units: dbus.service
restarting the following units: nix-daemon.service, systemd-journald.service
starting the following units: nscd.service, resolvconf.service
the following new units were started: nginx.service
warning: error(s) occurred while switching to the new configuration

[root@nixos:~]# systemctl status nginx.service
● nginx.service - Nginx Web Server
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled; preset: enabled)
     Active: active (running) since Tue 2023-08-29 10:23:45 CEST; 21s ago
    Process: 11753 ExecStartPre=/nix/store/lv0psgdbcv360qmgcz3dbmzz7810bf3x-unit-script-nginx-pre-start/bin/nginx-pre-start (cod>
   Main PID: 11803 (nginx)
     CGroup: /system.slice/nginx.service
             ├─11803 "nginx: master process /nix/store/i710dxxlgczlk56wx3d1hg69ci85cf6k-nginx-1.24.0/bin/nginx -c /nix/store/7iw>
             └─11807 "nginx: worker process"

Aug 29 10:23:45 nixos systemd[1]: Starting Nginx Web Server...
Aug 29 10:23:45 nixos nginx-pre-start[11799]: nginx: the configuration file /nix/store/7iwjk2b4qya42ijmd3ijv6qbv0w5rx6k-nginx.co>
Aug 29 10:23:45 nixos nginx-pre-start[11799]: nginx: configuration file /nix/store/7iwjk2b4qya42ijmd3ijv6qbv0w5rx6k-nginx.conf t>
Aug 29 10:23:45 nixos systemd[1]: Started Nginx Web Server.
```

(Не обращайте внимания на сообщения об ошибках с монтированием. Ничего они не ломают.)

Отлично, это работает как ожидалось, что и демонстрирует открытие страницы в браузере на хосте:

![Приветственная страница nginx в браузере хоста, отданная контейнером NixOS](/images/ca35db44a403e33af24b593c1b85d6b8.png)

Если вы уже используете NixOS на своих продакшн-серверах, это позволяет очень легко переиспользовать части их конфигураций NixOS локально в разработке. Или наоборот: мы можем разрабатывать и тестировать модули конфигурации NixOS локально, прежде чем переиспользовать их на продакшн-серверах.

### Обмен файлами между хостом и контейнером

Если мы хотим сделать папки общими между хостом и гостем, можно просто создать отображения между путями хоста и путями контейнера вот так в конфигурационном файле `/etc/systemd/nspawn/nixos.nspawn`:

```ini
[Files]
Bind=/some/path/in/host:/some/path/in/container
```

Опция `BindReadOnly` работает так же, но делает bind-монтирование доступным контейнеру только для чтения.

В [разделе _Files_ документации по формату конфигурационного файла `systemd.nspawn`](https://man7.org/linux/man-pages/man5/systemd.nspawn.5.html#%5BFILES%5D_SECTION_OPTIONS) есть ещё много опций.

## Итоги и перспективы

В этой учебной статье мы узнали, как быстро запустить почти полноценный экземпляр NixOS на любом дистрибутиве GNU/Linux, использующем systemd (например, Ubuntu, Debian, Fedora, Rocky Linux и т.д.).

Этот экземпляр NixOS можно настроить под наши нужды, а также запускать как сайдкар к нашей обычной хост-системе. systemd может обращаться с ним как с системным сервисом, который по умолчанию поднимается вместе с хост-системой, через `machinectl enable nixos`.

Все изменения в этой системе сохраняются между перезапусками. systemd/`machinectl` предоставляет средства и настройки, чтобы это изменить: мы можем настроить машину под свои нужды, а затем сделать её _эфемерной_ (сбрасывающейся при каждом запуске), каковыми образы Docker являются по умолчанию. Мы также можем экспортировать её подкомандой `machinectl export-tar`, чтобы поделиться с коллегами и заказчиками.

Следующий шаг — автоматизация развёртывания всей системы путём помещения конфигурации контейнера в конфигурацию хоста. Тогда при настройке системы не потребуется никаких ручных шагов. Как это сделать, мы увидим в следующей статье блога.

Конечно, углублённое путешествие в мир NixOS и контейнеров может быть частью [каждого занятия Nixcademy](https://nixcademy.com), специально адаптированного под требования вашей компании!

![Jacek Galowicz](/images/b73a86e857d7b2d8d58174f32606fc9c.png)

### Об авторе

Jacek — основатель Nixcademy, интересуется функциональным программированием, управлением сложностью и распространением Nix и NixOS по всему миру. Он также написал книгу о C++ и читал университетские лекции о качестве ПО.

**********

[nixos](/tags/nixos.md)
[nix](/tags/nix.md)
[systemd-nspawn](/tags/systemd-nspawn.md)