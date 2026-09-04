# Настройка самовосстанавливающихся служб с systemd

Источник: [Set up self-healing services with systemd](https://www.redhat.com/en/blog/systemd-automate-recovery)

Anthony Critelli · 4 октября 2021 · 3 мин

Это факт жизни: системы, программы и службы отказывают. Держать пользователей довольными, а пейджер тихим — вечная забота каждого сисадмина. Поэтому умение быстро, эффективно и (в идеале) автоматически обрабатывать отказы службы — признак способного (и хорошо высыпающегося) сисадмина. Эта статья проведёт вас по нескольким способам, которыми [systemd](https://www.redhat.com/sysadmin/love-systemd) поможет вам смягчить отказы ваших служб.

## Перезапуск упавших юнитов

Systemd делает очень простым перезапуск юнита при сбое. Иногда это всё, что действительно нужно. Я работал с глючным ПО, которое изредка натыкается на неисправимую ошибку, падает и требует перезапуска. В идеале вы бы исправили лежащую в основе проблему ПО, но это не всегда в вашей власти.

Следующий unit-файл службы будет перезапускать службу при сбое. `Restart=on-failure` покрывает самый широкий спектр сценариев отказа, таких как «грязные» сигналы и нечистые коды выхода:

```ini
[Unit]
Description=My App
StartLimitIntervalSec=30
StartLimitBurst=2

[Service]
ExecStart=/usr/local/sbin/my-app.sh
Restart=on-failure
```

Другие варианты перезапуска смотрите в [документации systemd service](https://www.freedesktop.org/software/systemd/man/systemd.service.html).

Настройки `StartLimitBurst=2` и `StartLimitIntervalSec=30` говорят systemd, что если служба безуспешно пытается перезапуститься дважды в течение 30 секунд, ей следует перейти в состояние failed и больше не пытаться перезапуститься. Это гарантирует, что если служба действительно сломана, systemd не будет бесконечно пытаться её перезапускать. Эти настройки всегда стоит подстраивать под значения, подходящие вашей нагрузке.

Сбросить счётчик отказов можно командой `systemctl reset-failed`.

## Действия при отказе

Перезапустить службу — хорошо, но выполнить конкретные действия при отказе юнита — ещё лучше. Возможно, вы используете ПО с известным багом, требующим удаления файла кэша при падении, или, скажем, вы хотите запустить скрипт, собирающий журналы и информацию о системе, чтобы проблему можно было диагностировать. Systemd позволяет указывать юниты, запускающиеся при отказе службы.

Этот пример указывает `OnFailure=my-app-recovery.service`, сообщая systemd, что при отказе моей службы следует запустить юнит `my-app-recovery`:

```ini
[Unit]
Description=My App
StartLimitIntervalSec=30
StartLimitBurst=2
OnFailure=my-app-recovery.service

[Service]
ExecStart=/usr/local/sbin/my-app.sh
Restart=on-failure
```

Юнит `my-app-recovery` — это просто служба типа oneshot, запускающая этот скрипт:

```ini
[Unit]
Description=My App

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/my-app-recovery.sh
```

Этот скрипт может делать что угодно: выполнять некий ручной обходной манёвр, чтобы снова поднять службу, отправлять оповещение в систему мониторинга или упаковывать временные журналы и состояние приложения для расследования. В данном случае он просто пишет сообщение во временный файл и перезапускает службу:

```bash
#!/bin/bash

echo 'Attempting to recover!' > /tmp/recovery_info
systemctl reset-failed my-app
systemctl restart my-app
```

Когда этот юнит переходит в состояние отказа, журналы юнита чётко показывают, что зависимости `OnFailure` были запущены:

```text
Aug 30 03:04:30 server01 systemd[1]: my-app.service: Main process exited, code=exited, status=1/FAILURE
Aug 30 03:04:30 server01 systemd[1]: my-app.service: Failed with result 'exit-code'.
Aug 30 03:04:30 server01 systemd[1]: my-app.service: Service RestartSec=100ms expired, scheduling restart.
Aug 30 03:04:30 server01 systemd[1]: my-app.service: Scheduled restart job, restart counter is at 1.
Aug 30 03:04:30 server01 systemd[1]: Stopped My App.
Aug 30 03:04:30 server01 systemd[1]: Started My App.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Main process exited, code=exited, status=1/FAILURE
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Failed with result 'exit-code'.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Service RestartSec=100ms expired, scheduling restart.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Scheduled restart job, restart counter is at 2.
Aug 30 03:04:32 server01 systemd[1]: Stopped My App.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Start request repeated too quickly.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Failed with result 'exit-code'.
Aug 30 03:04:32 server01 systemd[1]: Failed to start My App.
Aug 30 03:04:32 server01 systemd[1]: my-app.service: Triggering OnFailure= dependencies.
```

Будьте осторожны с перезапуском служб внутри скрипта `OnFailure`. Вы же не хотите сценарий, в котором ваш скрипт так хорошо перезапускает службу, что вы никогда не узнаёте о проблеме. Разумно обеспечить какой-то ввод в вашу систему оповещений, чтобы она знала, когда сталкивается с условием отказа.

### А вы пробовали выключить и снова включить?

Каждый сисадмин знает ценность хорошего перезапуска для исправления странной проблемы, и вас может соблазнить просто вставить reboot в скрипт `OnFailure`. К счастью, systemd включает встроенную функциональность для запуска перезагрузок системы при отказах юнитов. В этом примере система корректно перезагрузится при отказе юнита:

```ini
[Unit]
Description=My App
StartLimitIntervalSec=30
StartLimitBurst=2
FailureAction=reboot

[Service]
ExecStart=/usr/local/sbin/my-app.sh
Restart=on-failure
```

У `FailureAction` есть несколько допустимых значений, так что обязательно [изучите документацию systemd unit](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) для полного понимания его возможностей.

## Автоматическое восстановление

Поддержание бесперебойной работы служб — цель любого преданного сисадмина, но именно автоматическая обработка сценариев отказа отличает новичков от закалённых ветеранов. Systemd включает мощные возможности автоматизации ваших реакций, чтобы службы продолжали работать. В этой статье вы узнали о нескольких простых возможностях systemd, которые помогут вам держать ваши системы в рабочем порядке.

**********

[systemd](/tags/systemd.md)
[linux](/tags/linux.md)
[сервис](/tags/service.md)