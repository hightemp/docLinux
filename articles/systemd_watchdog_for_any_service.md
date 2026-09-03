# systemd Watchdog для любого сервиса

Источник: [Systemd Watchdog for Any Service](https://medo64.com/posts/systemd-watchdog-for-any-service/)

24 января 2019

Создать базовый systemd-сервис просто. Возьмём простейшее приложение (не обязательно даже задуманное как сервис) и посмотрим, как заставить его работать под systemd.

Наше приложение-пример — скрипт в `/opt/test/application` со следующим содержимым:

```bash
#!/bin/bash

while(true); do
  date | tee /var/tmp/test.log
  sleep 1
done
```

По сути это просто бесконечный вывод текущей даты.

Чтобы превратить его в сервис, создадим `/etc/systemd/system/test.service` с описанием приложения:

```text
[Unit]
Description=Test service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/opt/test/application
Restart=always
RestartSec=1

[Install]
WantedBy=multi-user.target
```

Это всё, что нужно, прежде чем запустить сервис:

```bash
sudo systemctl start test

sudo systemctl status test
```

```text
 ● test.service - Test service
    Loaded: loaded (/etc/systemd/system/test.service; disabled; vendor preset: enabled)
    Active: active (running)
  Main PID: 5212 (service)
     Tasks: 2 (limit: 4657)
    CGroup: /system.slice/test.service
            ├─5212 /bin/bash /opt/test/application
            └─5321 sleep 1
```

Systemd запустит приложение и даже перезапустит его при сбое. Но что, если хочется чуть умнее? Что если нужен watchdog, который перезапускает приложение не только при падении процесса, но и когда другая проверка здоровья завершается неудачно?

Хотя systemd поддерживает такую схему, приложение, как правило, должно знать об этом и периодически вызывать функцию watchdog. К счастью, даже если наше приложение этого не делает, можно задействовать watchdog-механизм через утилиту `systemd-notify`.

Сначала нужно изменить три вещи в описании сервиса: сменить тип на `notify`, сменить исполняемый файл на скрипт-обёртку и задать время watchdog.

В этом примере приложение, не ответившее в течение 5 секунд, будет считаться упавшим. Новое описание в `/etc/systemd/system/test.service`:

```text
[Unit]
Description=Test service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=notify
ExecStart=/opt/test/test.sh
Restart=always
RestartSec=1
TimeoutSec=5
WatchdogSec=5

[Install]
WantedBy=multi-user.target
```

Внимательный читатель заметит, что мы пока ничего не решили — просто перенесли всю ответственность на скрипт-обёртку `/opt/test/test.sh`.

Именно в этом скрипте мы сначала сообщаем systemd, когда приложение готово, а затем в цикле проверяем не только PID приложения, но и любые другие условия (например, ответ curl), вызывая `systemd-notify`, если приложение здорово:

```bash
#!/bin/bash

trap 'kill $(jobs -p)' EXIT

/opt/test/service &
PID=$!

/bin/systemd-notify --ready

while(true); do
    FAIL=0

    kill -0 $PID
    if [[ $? -ne 0 ]]; then FAIL=1; fi

#    curl http://localhost/test/
#    if [[ $? -ne 0 ]]; then FAIL=1; fi

    if [[ $FAIL -eq 0 ]]; then /bin/systemd-notify WATCHDOG=1; fi

    sleep 1
done
```

Запуск сервиса теперь даёт немного другой вывод:

```bash
sudo systemctl stop test
sudo systemctl start test
sudo systemctl status test
```

```text
 ● test.service - Test service
    Loaded: loaded (/etc/systemd/system/test.service; disabled; vendor preset: enabled)
    Active: active (running)
  Main PID: 6406 (test.sh)
     Tasks: 4 (limit: 4657)
    CGroup: /system.slice/test.service
            ├─6406 /bin/bash /opt/test/test.sh
            ├─6407 /bin/bash /opt/test/application
            ├─6557 sleep 1
            └─6560 sleep 1
```

Если убить приложение вручную (например, `sudo kill 6407`), systemd сочтёт сервис умершим и запустит его заново. То же произойдёт при провале любой другой проверки.

Хотя такой подход не идеален, он позволяет легко добавлять watchdog для уже существующих приложений.

**********

[systemd](/tags/systemd.md)
[watchdog](/tags/watchdog.md)
[Linux](/tags/linux.md)