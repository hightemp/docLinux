# Из дневника разработчика: автологин в machinectl

Источник: [Developer Diary Excerpts: machinectl auto-login](https://philip-trauner.me/blog/post/machinectl-autologin)

16 марта 2019 · 492 слова · 2 минуты

Поднятие корневой файловой системы через `systemd-nspawn -b -D` и последующий вход в контейнер требует, чтобы либо у нужного пользователя был установлен пароль, либо существовал [`autologin`-override для службы `console-getty`](https://wiki.archlinux.org/index.php/Getty#Nspawn_console).

Если же контейнер поднимается через `machinectl start`, override для `console-getty` не влияет на последующие вызовы `machinectl login`, поскольку за псевдотерминалы, к которым подключается `login`, вместо этого отвечает `container-getty@.service`:

```text
    State: running
     Jobs: 0 queued
   Failed: 0 units
    Since: Sat 2019-03-16 17:11:26 CET; 16min ago
   CGroup: /
           ├─init.scope
           │ └─1 /lib/systemd/systemd
           └─system.slice
             ├─console-getty.service
             │ └─48 /sbin/agetty --noclear --keep-baud console 115200,38400,9600 vt220
             └─system-container\x2dgetty.slice
               └─container-getty@0.service
                 ├─53 /bin/login -f
                 └─58 -bash
```

Сокращённый вывод `systemctl status` контейнера.

Войти в контейнер без пароля всё ещё можно с помощью [подкоманды `shell`](https://www.freedesktop.org/software/systemd/man/machinectl.html#shell%20%5B%5BNAME@%5DNAME%20%5BPATH%20%5BARGUMENTS%E2%80%A6%5D%5D%5D%20) утилиты [`machinectl`](https://github.com/systemd/systemd/pull/1022), однако для дистрибутивов Linux со старыми версиями `systemd` (без `shell`, то есть до [v224](https://github.com/systemd/systemd/releases/tag/v224)) подкоманда `login` остаётся единственным вариантом.

Поведение `shell` можно воспроизвести для `login` с помощью `ExecStart`-override для `container-getty@.service`:

```bash
systemctl edit container-getty@.service
```

Выполнять внутри контейнера, а не на хосте (текстовый редактор должен быть установлен).

```text
[Service]
ExecStart=
ExecStart=-/sbin/agetty --noclear --autologin root --keep-baud pts/%I 115200,38400,9600 $TERM
```

  * Пустое место после первого `ExecStart` оставлено намеренно: оно говорит `systemd` очистить существующее содержимое `ExecStart`.
  * Подстановка другого имени пользователя вместо `root` включит автоматический вход для указанного пользователя.

## Примечания

  * В корневой файловой системе контейнера должны быть установлены `systemd` и `dbus`, иначе и `login`, и `shell` завершатся с ошибкой (`Failed to get shell PTY: Protocol error`).
  * Override не обязательно создавать подкомандой `edit` у `systemd`. Создание и последующее заполнение `/etc/systemd/system/container-getty@.service.d/override.conf` работает точно так же.

**********

[machinectl](/tags/machinectl.md)
[systemd](/tags/systemd.md)
[systemd-nspawn](/tags/systemd-nspawn.md)