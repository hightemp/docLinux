# systemd/Timers

Источник: [systemd/Timers — русскоязычная страница ArchWiki по systemd-таймерам: `.timer`-юниты, monotonic и realtime timers, `OnCalendar`, `OnBootSec`, `OnUnitActiveSec`, `AccuracySec`, `Persistent`, пользовательские таймеры и примеры расписаний.](https://wiki.archlinux.org/title/Systemd_(Русский)

< [Systemd (Русский)](/title/Systemd_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Systemd \(Русский\)")

Ссылки по теме

  * [systemd (Русский)](/title/Systemd_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Systemd \(Русский\)")
  * [systemd/Пользователь](/title/Systemd/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C "Systemd/Пользователь")
  * [systemd FAQ](/title/Systemd_FAQ "Systemd FAQ")
  * [cron (Русский)](/title/Cron_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Cron \(Русский\)")

**Состояние перевода:** На этой странице представлен перевод статьи [systemd/Timers](/title/Systemd/Timers "Systemd/Timers"). Дата последней синхронизации: 12 июля 2021. Вы можете [помочь](/title/ArchWiki:Translation_Team_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "ArchWiki:Translation Team \(Русский\)") синхронизировать перевод, если в английской версии произошли [изменения](https://wiki.archlinux.org/index.php?title=Systemd/Timers&diff=0&oldid=684326).

Таймеры — файлы юнитов [systemd](/title/Systemd_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Systemd \(Русский\)"), имя которых имеет суффикс _.timer_ ; они позволяют контролировать файлы _.service_ или события. Таймеры могут использоваться в качестве замены [cron](/title/Cron "Cron") (смотрите #В качестве замены cron). Таймеры имеют встроенную поддержку календарных и регулярных событий и могут запускаться в асинхронном режиме.

## Юниты таймера

Таймеры _systemd_ — файлы юнитов с суффиксом _.timer_. Они хранятся в тех же каталогах, что и другие [файлы настроек юнитов](/title/Systemd_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\)#Написание_файлов_юнитов "Systemd \(Русский\)"), но включают в себя раздел `[Timer]`, который определяет, как и когда таймер запускается. Существует два типа таймеров:

  * **Таймеры реального времени** (также известные как настенные часы) запускаются в зависимости от событий календаря (как cronjobs). Для определения таких таймеров используется опция `OnCalendar=`.
  * **Монотонные таймеры** активируются после определенного промежутка времени по отношению к той или иной отправной точке. Они не сработают, если компьютер находится в режиме ожидания или выключен. Есть несколько различных монотонных таймеров, но все они имеют вид: `On _Type_ Sec=`. Обычно монотонные таймеры включают в себя `OnBootSec` и `OnUnitActiveSec`.

Подробнее см. [systemd.timer(5)](https://man.archlinux.org/man/systemd.timer.5). Синтаксис аргументов для календарных событий и временных промежутков можно найти в [systemd.time(7)](https://man.archlinux.org/man/systemd.time.7).

**Примечание** В _systemd_ предусмотрена цель `timers.target`, к которой можно привязать таймеры, запускаемые сразу после загрузки системы (подробнее см. [systemd.special(7)](https://man.archlinux.org/man/systemd.special.7)). Чтобы ею воспользоваться, укажите параметр `WantedBy=timers.target` в разделе `[Install]` файла таймера, после чего [включите](/title/%D0%92%D0%BA%D0%BB%D1%8E%D1%87%D0%B8%D1%82%D0%B5 "Включите") юнит.

## Юнит службы

Каждому файлу _.timer_ соответствует файл _.service_ (например, `foo.timer` и `foo.service`). _.timer_ запускается и контролирует _.service_. _.service_ не требует раздела `[Install]`, так как последний присутствует в юните _timer_ , который уже включен. Если необходимо, то можно контролировать юниты с разным названием, используя опцию `Unit=` в таймере в разделе `[Timer]`.

## Управление

Для того, чтобы использовать юнит-_timer_ , [включите](/title/%D0%92%D0%BA%D0%BB%D1%8E%D1%87%D0%B8%D1%82%D0%B5 "Включите") и [запустите](/title/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%B8%D1%82%D0%B5 "Запустите") его, как любой другой юнит (не забудьте добавить суффикс _.timer_). Для того, чтобы увидеть все запущенные таймеры, выполните:

```bash
$ systemctl list-timers

NEXT                          LEFT        LAST                          PASSED     UNIT                         ACTIVATES
Thu 2014-07-10 19:37:03 CEST  11h left    Wed 2014-07-09 19:37:03 CEST  12h ago    systemd-tmpfiles-clean.timer systemd-tmpfiles-clean.service
Fri 2014-07-11 00:00:00 CEST  15h left    Thu 2014-07-10 00:00:13 CEST  8h ago     logrotate.timer              logrotate.service
```

**Примечание**

  * Чтобы увидеть все таймеры (в том числе и неактивные), используйте `systemctl list-timers --all`.
  * Статус службы, запускаемой посредством таймера, вероятно, будет неактивным, если, конечно, она не была запущена непосредственно перед проверкой статуса.
  * Если таймер рассинхронизировался, то может помочь удаление соответствующих файлов `stamp-*` в `/var/lib/systemd/timers` (или `~/.local/share/systemd/`). Это файлы нулевого размера, которые отмечают последнее время запуска таймера. Если данные файлы отсутствуют, то они будут перестроены при следующем запуске соответствующего таймера.

## Примеры

Запуск службы может быть запланирован по таймеру. В последующих примерах назначается запуск `foo.service` в соответствии с таймером `foo.timer`.

### Монотонный таймер

Таймер, который запустится через 15 минут после загрузки, а затем снова будет запускаться каждую неделю во время работы системы.

```text
/etc/systemd/system/foo.timer

[Unit]
Description=Run foo weekly and on boot

[Timer]
OnBootSec=15min
OnUnitActiveSec=1w

[Install]
WantedBy=timers.target
```

### Таймер реального времени

Таймер, который будет запускаться один раз в неделю (в 12:00 в понедельник). При активации он сразу же запустит службу, если отсутствует последнее время запуска (опция `Persistent=true`), например, в связи с отключением системы:

```text
/etc/systemd/system/foo.timer

[Unit]
Description=Run foo weekly

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```

Если требуется указать более точную дату и время, используйте следующий формат:

```text
ДеньНедели Год-Месяц-День Часы:Минуты:Секунды
```

Звездочка может быть использована, чтобы указать все значения, а запятые, в свою очередь, для перечисления возможных значений. Используйте `..`, чтобы выделить какой-то конкретный промежуток. В следующем примере служба запускается в первые четыре дня каждого месяца в полдень, но _только_ если день является понедельником или вторником.

```text
OnCalendar=Mon,Tue *-*-01..04 12:00:00
```

Запуск службы в первую субботу каждого месяца:

```text
OnCalendar=Sat *-*-1..7 18:00:00
```

По крайней мере один день должен быть указан при использовании `ДеньНедели`. Таймер, который будет запускаться каждый день в 4 утра:

```text
OnCalendar=*-*-* 4:00:00
```

Если необходимо запускать службу в разное время, то можно указать параметр `OnCalendar` несколько раз. В примере ниже служба запускается в 22:30 по рабочим дням и в 20:00 по выходным:

```text
OnCalendar=Mon..Fri 22:30
OnCalendar=Sat,Sun 20:00
```

Подробнее см. [systemd.time(7)](https://man.archlinux.org/man/systemd.time.7).

**Совет**

  * Указатели времени `OnCalendar` могут быть протестированы для того, чтобы проверить их правильность и вычислить следующее время срабатывания условия. Например, `systemd-analyze calendar weekly` или `systemd-analyze calendar "Mon,Tue *-*-01..04 12:00:00"`.
  * Команда `faketime` полезна для тестирования с командой выше. [Установите](/title/%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%B8%D1%82%D0%B5 "Установите") пакет [libfaketime](https://archlinux.org/packages/?name=libfaketime).
  * Специальные выражения событий, такие как `daily` и `weekly`, относятся к _конкретному времени начала_ и, таким образом, все таймеры, использующие эти выражения, запустятся одновременно. Таймеры, использующие специальные выражения, могут негативно сказаться на производительности системы, если сервисы, запускаемые таймерами, являются ресурсозатратными. Опция `RandomizedDelaySec` в разделе `[Timer]` помогает избежать подобных проблем посредством случайного выбора времени запуска каждого из таймеров. Смотрите [systemd.timer(5)](https://man.archlinux.org/man/systemd.timer.5).
  * Добавьте опцию `AccuracySec=1us` в раздел `[Timer]`, чтобы не использовать значение погрешности _1m_ , установленное по умолчанию. См. также [systemd.timer(5)](https://man.archlinux.org/man/systemd.timer.5).

## Временные юниты .timer

Можно использовать `systemd-run` для создания временных юнитов _.timer_. То есть можно назначить запуск определённой команды в нужное время, не имея соответствующего файла службы. Например, следующая команда создаст файл через 30 секунд:

```text
# systemd-run --on-active=30 /bin/touch /tmp/foo
```

Кроме того, можно указать предварительно существующий файл сервиса, при этом не имея файла таймера. Например, запустим юнит, который называется `_некоторыйюнит_.service`, через 12.5 часов:

```text
# systemd-run --on-active="12h 30m" --unit _некоторыйюнит_.service
```

Смотрите [systemd-run(1)](https://man.archlinux.org/man/systemd-run.1) для получения дополнительной информации и примеров.

## В качестве замены cron

Несмотря на то, что [cron](/title/Cron "Cron"), возможно, самый известный планировщик задач, таймеры _systemd_ могут выступать в качестве альтернативы.

### Преимущества

Основные преимущества использования таймеров приходят от каждой задачи, которая имеет собственную службу _systemd_. Вот некоторые из этих преимуществ:

  * Задачи могут быть легко запущены независимо от их таймеров. Это упрощает отладку.
  * Каждая задача может быть настроена для работы в определенной среде (смотрите [systemd.exec(5)](https://man.archlinux.org/man/systemd.exec.5)).
  * Задачи могут быть присоединены к [cgroups](/title/Cgroups "Cgroups").
  * Задачи могут быть настроены в зависимости от других юнитов _systemd_.
  * Задачи регистрируются в журнале _systemd_ для легкости отладки.

### Предостережения

Некоторые вещи, которые легко сделать посредством cron, трудно сделать только юнитами таймера.

  * Создание: чтобы настроить задачу, запускаемую в определенное время, при помощи _systemd_ , вам нужно создать два файла и использовать команды `systemctl`. Сравните это с добавлением одной строчки в crontab.
  * Электронная почта: отсутствие встроенного эквивалента cron `MAILTO` для отправки писем при сбое. В следующем разделе приведен пример создания эквивалента с использованием `OnFailure=`.

Также обратите внимание, что [пользовательские](/title/Systemd/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C "Systemd/Пользователь") юниты-таймеры будут запускаться только тогда, когда активен сеанс соответствующего пользователя. Тем не менее, [долговременные](/title/Systemd/%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C#Автоматический_запуск_systemd_от_имени_пользователя "Systemd/Пользователь") службы могут запускаться при загрузке системы даже если пользователь не выполнил вход.

### MAILTO

Вы можете настроить systemd для отправки электронной почты при сбое юнита - так же, как Cron делает с `MAILTO`. Прежде всего, нужно два файла: исполняемый для посылки почты и _.service_ для запуска первого. В следующем примере, исполняемый файл - скрипт, использующий `sendmail`, который можно найти в пакетах, предоставляющих `smtp-forwarder`.:

```bash
/usr/local/bin/systemd-email

#!/bin/sh

/usr/bin/sendmail -t <<ERRMAIL
To: $1
From: systemd <root@$HOSTNAME>
Subject: $2
Content-Transfer-Encoding: 8bit
Content-Type: text/plain; charset=UTF-8

$(systemctl status --full "$2")
ERRMAIL
```

Исполняемый файл, видимо, должен получать минимум два аргумента, полученных сценарием: адрес для отправки и файл юнита для получения статуса. Файл _.service_ , который мы создадим, будет передавать эти аргументы:

```text
/etc/systemd/system/status_email__user_ @.service

[Unit]
Description=status email for %i to _user_

[Service]
Type=oneshot
ExecStart=/usr/local/bin/systemd-email _address_ %i
User=nobody
Group=systemd-journal
```

Здесь `_user_` — получатель почты, а `_address_` — адрес электронной почты пользователя. Хотя получать "захардкожен", файл юнита для отчёта передается как параметр экзепляра, поэтому данная служба может посылать электронные письма множеству юнитов. [Запустите](/title/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%B8%D1%82%D0%B5 "Запустите") `status_email__user_ @dbus.service`, чтобы убедиться, что вы можете получать почту.

Затем просто [отредактируйте](/title/%D0%9E%D1%82%D1%80%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%B8%D1%80%D1%83%D0%B9%D1%82%D0%B5 "Отредактируйте") службу, от которой вы хотите получать почту и добавьте `OnFailure=status_email__user_ @%n.service` в раздел `[Unit]`. `%n` передает имя юнита в шаблон.

**Примечание**

  * Если вы настроили sSMTP в соответствии с [sSMTP#Security](/title/SSMTP#Security "SSMTP"), то пользователь `nobody` не будет иметь доступа к `/etc/ssmtp/ssmtp.conf` и команда `systemctl start status_email__user_ @dbus.service` не сработает. Одним из решений является использование `root`-пользователя в юните `status_email__user_ @.service`.
  * Если вы попробуете использовать `mail -s somelogs _address_` в почтовом скрипте, `mail` создаст свой форк и systemd убьет процесс посылки почты, когда увидит, что скрипт завершился. Можно сделать так, чтобы почтовый процесс не создавал своих форков путем выполнения `mail -Ssendwait -s somelogs _address_`.

### Использование crontab

Некоторые из предостережений можно обойти путем установки пакета, который анализирует crontab, а затем настраивает таймеры на его основе. [systemd-cron-next](https://aur.archlinux.org/packages/systemd-cron-next/)AUR[[ссылка недействительна](/title/ArchWiki:Requests#Broken_package_links "ArchWiki:Requests"): package not found] и [systemd-cron](https://aur.archlinux.org/packages/systemd-cron/)AUR — два таких пакета. Они могут предоставлять недостающую функцию `MAILTO`.

Если вам нравится crontabs только потому, что он предоставляет единый вид для всех запланированных задач, `systemctl` делает тоже самое. Смотрите #Управление

## Смотрите также

  * [systemd.timer(5)](https://man.archlinux.org/man/systemd.timer.5)
  * [Fedora:Features/SystemdCalendarTimers](https://fedoraproject.org/wiki/Features/SystemdCalendarTimers "fedora:Features/SystemdCalendarTimers")
  * [Gentoo:Systemd#Timer services](https://wiki.gentoo.org/wiki/Systemd#Timer_services "gentoo:Systemd")
  * **systemd-cron-next** -- утилита для создания таймеров/служб из файлов crontab и anacrontab

```c
<https://github.com/systemd-cron/systemd-cron-next> || [systemd-cron-next](https://aur.archlinux.org/packages/systemd-cron-next/)AUR[[ссылка недействительна](/title/ArchWiki:Requests#Broken_package_links "ArchWiki:Requests"): package not found]
```

  * **systemd-cron** -- предоставляет юнитам systemd запускать скрипты cron; используя _systemd-crontab-generator_ для конвертации crontab'ов

```c
<https://github.com/systemd-cron/systemd-cron> || [systemd-cron](https://aur.archlinux.org/packages/systemd-cron/)AUR
```

  * [Systemd Timers for Scheduling Tasks](https://fedoramagazine.org/systemd-timers-for-scheduling-tasks/)

Retrieved from "[https://wiki.archlinux.org/index.php?title=Systemd_(Русский)/Timers_(Русский)&oldid=874980](https://wiki.archlinux.org/index.php?title=Systemd_\(Русский\)/Timers_\(Русский\)&oldid=874980)"

[Category](/title/Special:Categories "Special:Categories"):

  * [System administration (Русский)](/title/Category:System_administration_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Category:System administration \(Русский\)")

Hidden category:

  * [Pages with broken package links](/title/Category:Pages_with_broken_package_links "Category:Pages with broken package links")

**********

[Linux](/tags/linux.md)
[systemd timers](/tags/systemd_timers.md)
