# syslog-ng

Источник: [syslog-ng](https://wiki.archlinux.org/title/Syslog-ng)

Из ArchWiki

Связанные статьи:

  * [rsyslog](/title/Rsyslog "Rsyslog")

[syslog-ng](https://en.wikipedia.org/wiki/syslog-ng "wikipedia:syslog-ng") — это реализация [syslog](https://en.wikipedia.org/wiki/syslog "wikipedia:syslog"), которая может принимать log-сообщения из источников и пересылать их в места назначения на основе мощных директив фильтрации. Хотя его истоки лежат в syslog, это довольно универсальный инструмент управления логами, способный потреблять структурированные и неструктурированные log-сообщения, разбирая и преобразуя их при необходимости.

**Замечание** С [журналом systemd](/title/Systemd/Journal "Systemd/Journal") syslog-ng не нужен, если всё, что вам требуется — локальные логи.

## Обзор

syslog-ng принимает входящие log-сообщения из определённых «источников» и пересылает их в соответствующие места назначения на основе мощных директив фильтрации. В типичной простой настройке syslog-ng читает сообщения из трёх источников:

  1. устройства `/dev/log` по умолчанию, куда отправляется большинство логов;
  2. «внутренних» log-сообщений syslog-ng;
  3. сообщений ядра из `/proc/kmsg`.

Источники определяются директивой «source». Входящие сообщения затем фильтруются согласно определённым фильтрам (ключевое слово «filter»), т. е. по программе-источнику или уровню логирования, и отправляются в соответствующее «место назначения» (destination).

Места назначения включают файлы логов (например, `/var/log/messages.log`), печать сообщений на консоль и удалённые серверы.

Ключевая функция — log. Она определяет, какие фильтры должны применяться к определённому источнику и куда должны отправляться результирующие сообщения.

Помимо локальных источников, описанных выше, syslog-ng также умеет работать с различными источниками по сети. Для работы с ними нужно создать источник `network()`, `udp()` или `tcp()`, как описано ниже.

## Установка

[Установите](/title/Install "Install") пакет [syslog-ng](https://archlinux.org/packages/?name=syslog-ng).

Чтобы использовать syslog-ng с настройками по умолчанию, [запустите](/title/Start "Start")/[включите](/title/Enable "Enable") `syslog-ng@default.service` после корректировки основной конфигурации под место назначения.

## Конфигурация

Пакет предоставляет шаблонный юнит `syslog-ng@.service` и конфигурацию по умолчанию в `/etc/default/syslog-ng@default`, которая включает базовую конфигурацию, расположенную в `/etc/syslog-ng/syslog-ng.conf`. Конфигурация [logrotate](/title/Logrotate "Logrotate") предоставляется в `/etc/logrotate.d/syslog-ng`.

Пакетная конфигурация `syslog-ng.conf` не включает логирование.[[1]](https://gitlab.archlinux.org/archlinux/packaging/packages/syslog-ng/-/blob/main/syslog-ng.install?ref_type=heads&blame=1#L7) Чтобы syslog-ng создавал ожидаемые логи, должно быть определено одно из #Мест назначения (Destinations); найдите первую log-строку ближе к концу файла, которая выглядит так:

```text
log {
        source(s_local);

        # uncomment this line to open port 514 to receive messages
        #source(s_network);
        #destination(d_local);
};
```

Раскомментируйте `destination(d_local)`, чтобы использовать предопределённое расположение `/var/log/messages`, заданное ранее в конфиге. Не раскомментируйте `source(s_network)` — это не связано.

Определение `d_local`, находящееся ранее в конфигурации, не только пишет файл messages, но и включает `messages-kv.log`; этот лог-файл в формате ключ-значение может быть на порядки больше. Если вы его не используете, найдите определение `d_local()` ближе к началу `syslog-ng.conf` и закомментируйте строку `messages-kv.log`.

Добавьте `/var/log/messages` в предоставленную пакетом конфигурацию `/etc/logrotate.d/syslog-ng`. Значения по умолчанию включают все варианты с окончанием `.log`, но в них нет ни `messages`, ни `messages-kv.log`, описанных выше.

### Интеграция с systemd/journald

syslog-ng по умолчанию забирает сообщения из журнала systemd. Рекомендуется держать `ForwardToSyslog=no` в `/etc/systemd/journald.conf`, чтобы избежать накладных расходов, связанных с сокетом, и чтобы избежать [лишних сообщений об ошибках в логе](https://github.com/syslog-ng/syslog-ng/issues/314). Если же, с другой стороны, вы не хотите хранить логи дважды и выставили у _journald_ `Storage=none`, вам **понадобится** `ForwardToSyslog=yes`, так как _syslog-ng_ пытается следить за файлом журнала 'journald'.

Подробнее см. #syslog-ng и журнал systemd.

## Источники

syslog-ng получает log-сообщения из источника. Для определения источника используйте следующий синтаксис:

```text
source <identifier> { source-driver(params); source-driver(params); ... };
```

В простейшем случае вам понадобится единственный драйвер `system()`.

```text
source src { system(); };
```

Он автоматически определит наилучший способ сбора локальных логов и обеспечит сбор логов ядра, приложений и внутренних логов syslog-ng.

Идентификаторы и source-драйверы можно посмотреть в [альтернативных руководствах syslog-ng](https://axoflow.com/docs/axosyslog-core/chapter-sources/) (так как руководства на syslog-ng.com были недоступны).

Драйвер `system()` — на самом деле конструкция более высокого уровня, которая разворачивается в различные источники по мере необходимости для локальной системы. Но можно получить больше контроля, убрав источник `system()` и используя драйверы более низкого уровня напрямую.

Source-драйвер `unix-stream()` открывает заданный AF_UNIX [сокет](https://en.wikipedia.org/wiki/Berkeley_sockets "wikipedia:Berkeley sockets") и начинает слушать на нём сообщения.

Source-драйвер `internal()` «получает» сообщения, генерируемые внутри самим syslog-ng.

Следовательно, следующее означает: `src` получает сообщения из сокета `/dev/log` и от syslog-ng:

```text
source src { unix-stream("/dev/log"); internal(); };
```

Ядро отправляет log-сообщения в `/proc/kmsg`, а драйвер `file()` читает log-сообщения из файлов. Следовательно, следующее означает, что kernsrc получает сообщения из файла `/proc/kmsg`:

```text
source kernsrc { file("/proc/kmsg"); };
```

Чтобы открыть порт для чтения данных с удалённого сервера, источник должен быть определён с таким синтаксисом:

```text
source s_net { network(transport(udp)); };
```

для UDP или

```text
source s_net { network(transport(tcp)); };
```

для получения log-сообщений по TCP. Оба слушают на порту 514, если не переопределено параметром `port()`.

### syslog-ng и журнал systemd

Начиная с версии syslog-ng 3.6.1, источник `system()` по умолчанию в Linux-системах с systemd использует journald как стандартный источник `system()`.

Если вы хотите использовать одновременно journald и syslog-ng, убедитесь, что действуют следующие настройки. Для systemd-journald в файле `/etc/systemd/journald.conf`: `Storage=` либо установлен в `auto`, либо не установлен (по умолчанию — auto), и `ForwardToSyslog=` установлен в `yes`. Для `/etc/syslog-ng/syslog-ng.conf` нужна следующая строка `source`:

```text
/etc/syslog-ng/syslog-ng.conf

source src {
  system();
};
```

Если же, наоборот, вы хотите _не_ сохранять логи journald, а иметь только текстовые логи syslog-ng, установите `Storage=volatile` в `/etc/systemd/journald.conf`. Это будет хранить journald в RAM. Начиная с syslog-ng 3.6.3, syslog-ng использует journald как источник system(); так что если вы установите `Storage=none`, журнал systemd отбросит все сообщения и **не** перешлёт их в syslog-ng.

После изменения [перезапустите](/title/Restart "Restart") демоны `systemd-journald.service` и `syslog-ng@default.service`.

## Места назначения

В syslog-ng log-сообщения отправляются в файлы. Синтаксис очень похож на источники:

```text
destination <identifier> {destination-driver(params); destination-driver(params); ... };
```

Обычно логирование идёт в файл, но можно логировать и в другие destination-драйверы: pipe, unix-сокет, TCP/UDP-порты, терминалы или определённые программы. Простое объявление места назначения не приведёт к доставке сообщений туда: это произойдёт, только когда вы свяжете источники и места назначения с помощью log-строк. Log-строки могут также включать фильтры, реализуя тем самым гибкую маршрутизацию логов.

Это объявление указывает syslog-ng отправлять сообщения в `/var/log/auth.log`:

```text
destination authlog { file("/var/log/auth.log"); };
```

Если пользователь вошёл в систему, `usertty()` отправляет сообщения на терминал указанного пользователя. Если вы хотите отправлять консольные сообщения на терминал root, когда тот вошёл в систему:

```text
destination console { usertty("root"); };
```

Сообщения можно отправлять в pipe с помощью `pipe()`. Следующее отправляет сообщения xconsole в pipe `/dev/xconsole`. Это требует дополнительной настройки — смотрите подраздел xconsole ниже.

```text
destination xconsole { pipe("/dev/xconsole"); };
```

Для отправки сообщений по сети используйте `udp()`. Следующее отправит ваши log-данные на другой сервер.

```text
destination remote_server { udp("10.0.0.2" port(514)); };
```

Можно также использовать более новый синтаксис драйвера `network()` для того же:

```text
destination remote_server { network("10.0.0.2" port(514) transport(udp)); };
```

## Создание фильтров для сообщений

Синтаксис filter-строки:

```text
filter <identifier> { expression; };
```

В выражении можно использовать функции, например `facility()`, которая выбирает сообщения по кодам syslog facility (kern, mail, auth и т. д.). Помимо кодов facility, каждое log-сообщение связано с уровнем серьёзности (severity): debug — самый многословный, panic показывает только серьёзные ошибки. Коды facility, уровни логирования и имена приоритетов можно найти в `/usr/include/sys/syslog.h` или в [RFC 3164](https://tools.ietf.org/html/rfc3164 "rfc:3164"). Чтобы отфильтровать сообщения, приходящие от авторизации, вроде `su(pam_unix)[18569]: session opened for user root by (uid=1000)`, используйте следующее:

```text
filter f_auth { facility(auth); };
```

Выражение facility может использовать булевы операторы `and`, `or` и `not`, так что следующий фильтр выбирает сообщения, приходящие не от авторизации, сетевых новостей или почты:

```text
filter f_debug { not facility(auth, authpriv, news, mail); };
```

Функция `severity()` выбирает сообщения по уровню серьёзности; так, если вы хотите выбрать информационные уровни:

```text
filter f_info { severity(info); };
```

Функции и булевы операторы можно комбинировать в более сложные выражения. Следующая строка фильтрует сообщения с приоритетом от информационного до предупреждения, приходящие не от facility auth, authpriv, mail и news:

```text
filter f_messages { severity(info..warn) and not facility(auth, authpriv, mail, news); };
```

Сообщения можно также выбирать, сопоставляя регулярное выражение в сообщении с функцией `match("regex" value("<macro>"))`. Например, это сопоставит основную часть сообщения с регулярным выражением «failed»:

```text
filter f_failed { match("failed" value("MESSAGE")); };
```

В выражениях фильтров можно использовать как предопределённые, так и пользовательские макросы. Они также называются [«жёсткими» и «мягкими» макросами соответственно](https://axoflow.com/docs/axosyslog-core/chapter-manipulating-messages/customizing-message-format/macros-hard-vs-soft/).

Список и документация всех макросов есть в [документации syslog-ng](https://axoflow.com/docs/axosyslog-core/chapter-manipulating-messages/customizing-message-format/reference-macros/):

```text
 "AMPM", "BSDTAG", "DATE, C_DATE, R_DATE, S_DATE", "DAY, C_DAY, R_DAY, S_DAY", "FACILITY", "FACILITY_NUM", "FULLDATE, C_FULLDATE, R_FULLDATE, S_FULLDATE", "FULLHOST", "FULLHOST_FROM", "HOUR, C_HOUR, R_HOUR, S_HOUR", "HOUR12, C_HOUR12, R_HOUR12, S_HOUR12", "HOST", "HOST_FROM", "ISODATE, C_ISODATE, R_ISODATE, S_ISODATE", "LEVEL_NUM", "LOGHOST", "MIN, C_MIN, R_MIN, S_MIN", "MONTH, C_MONTH, R_MONTH, S_MONTH", "MONTH_ABBREV, C_MONTH_ABBREV, R_MONTH_ABBREV, S_MONTH_ABBREV", "MONTH_NAME, C_MONTH_NAME, R_MONTH_NAME, S_MONTH_NAME", "MONTH_WEEK, C_MONTH_WEEK, R_MONTH_WEEK, S_MONTH_WEEK", "MSEC, C_MSEC, R_MSEC, S_MSEC", "MSG or MESSAGE", "MSGHDR", "MSGID", "MSGONLY", "PID", "PRI", "PRIORITY or LEVEL", "PROGRAM", "SDATA, .SDATA.SDID.SDNAME", "SEC, C_SEC, R_SEC, S_SEC", "SOURCEIP", "SEQNUM", "STAMP, R_STAMP, S_STAMP", "SYSUPTIME", "TAG", "TAGS", "TZ, C_TZ, R_TZ, S_TZ", "TZOFFSET, C_TZOFFSET, R_TZOFFSET, S_TZOFFSET", "UNIXTIME, C_UNIXTIME, R_UNIXTIME, S_UNIXTIME", "USEC, C_USEC, R_USEC, S_USEC", "YEAR, C_YEAR, R_YEAR, S_YEAR", "WEEK, C_WEEK, R_WEEK, S_WEEK", "WEEK_ABBREV, C_WEEK_ABBREV, R_WEEK_ABBREV, S_WEEK_ABBREV", "WEEK_DAY, C_WEEK_DAY, R_WEEK_DAY, S_WEEK_DAY", "WEEKDAY, C_WEEKDAY, R_WEEKDAY, S_WEEKDAY", "WEEK_DAY_NAME, C_WEEK_DAY_NAME, R_WEEK_DAY_NAME, S_WEEK_DAY_NAME".
```

Для фильтрации сообщений, полученных от определённого удалённого хоста (как объявлено в самом входящем сообщении, а не по его IP-адресу), нужно использовать функцию `host()`:

```text
filter f_host { host( "192.168.1.1" ); };
```

Если же вы хотите фильтровать по IP-адресу отправителя, можно использовать фильтр `netmask()`:

```text
filter f_ipaddr { netmask( "192.168.1.1/32" ); };
```

## Log-пути

syslog-ng связывает источники, фильтры и места назначения с помощью log-строк. Синтаксис:

```text
log {source(s1); source(s2); ...
filter(f1); filter(f2); ...
destination(d1); destination(d2); ...
flags(flag1[, flag2...]); };
```

Например, следующее отправляет сообщения из источника `src` в место назначения `mailinfo`, отфильтрованные фильтром `f_info`:

```text
log { source(src); filter(f_mail); filter(f_info); destination(mailinfo); };
```

Log-строка описывает конвейер: она говорит syslog-ng взять сообщения из источника (или нескольких источников) и доставить их в место назначения (или несколько мест назначения) при совпадении связанных фильтров.

Если у вас несколько log-строк, берущих сообщения из одного и того же источника, сообщения будут дублироваться во все эти конвейеры. Конечно, можно применять разный набор фильтров и тем самым маршрутизировать сообщения выборочно в несколько мест назначения.

Помимо фильтрации, syslog-ng может применять разбор (parsing) или перезапись (rewriting) сообщений. Разбор означает извлечение информации из текста сообщения, а перезапись означает, что syslog-ng может изменять/переформатировать сообщения по необходимости.

У оператора `log` есть ещё много возможностей:

  1. Можно остановить обработку последующих log-путей после совпадения текущего с помощью flags(final).
  2. Можно сказать log-строке забирать сообщения, не захваченные другими log-строками, с помощью flags(fallback).
  3. Можно создать произвольный граф из log-конвейеров с помощью вложенных log-строк и junction, которые помогают строить сложные конвейеры обработки.

Подробнее о строках `log` можно прочитать в главе [документации syslog-ng](https://axoflow.com/docs/axosyslog-core/chapter-routing-filters/logpath/).

## Советы и приёмы

После понимания логики syslog-ng возможны многие, в том числе сложные, конфигурации. Вот некоторые примеры.

### Перезагрузка файла конфигурации syslog-ng

Можно заставить syslog-ng заново оценить файл конфигурации. Это можно сделать вручную, отправив `SIGHUP` процессу, или [перечитать конфигурацию](/title/Reload "Reload") `syslog-ng@default.service` (reload).

### Логирование с отказоустойчивостью на удалённый хост

Эта настройка показывает, как отправлять стандартные незашифрованные syslog-пакеты одновременно по протоколам TCP и UDP, используя стандартный порт (514) и альтернативный порт. Это отправка одного и того же вывода на одну машину четырьмя разными способами, чтобы попытаться гарантировать доставку пакетов. В основном полезно при отладке удалённого сервера, который не может перезагрузиться. Разные порты и протоколы — чтобы пройти любые межсетевые фильтры или другие сетевые проблемы. Также полезно для переадресации портов и использования туннелей. Такая настройка идеальна для туннелирования через SSH-соединение, которое host, склонный к отказам, инициирует через обратное соединение.

```text
#sending to a remote syslog server on TCP and UDP ports (not encrypted)
destination askapache_failover_loghost {
    tcp("208.86.158.195" port(25214));
    udp("208.86.158.195" port(25214));
    udp("mysyslog1.dyndns.org" port(514));
};
log {
    source(src);
    destination(askapache_failover_loghost);
};
```

И затем на loghost, принимающем эти логи:

```text
#a USB redirected console for flexible viewing
destination debugging_console {
    file("/dev/ttyU1");
};

# listens on IP addresses and ports, sets the incoming settings
source prone_to_failover_host {
    tcp(ip(208.86.158.195),port(25214));
    udp(ip(208.86.158.195) port(25214));

    udp(default-facility(syslog) default-priority(emerg));
    tcp(default-facility(syslog) default-priority(emerg));
}

# log it
log {
    source(prone_to_failover_host);
    destination(debugging_console);
};
```

### Перенос лога в другой файл

Чтобы перенести некоторый лог из `/var/log/messages` в другой файл:

```text
#sshd configuration
destination ssh { file("/var/log/ssh.log"); };
filter f_ssh { program("sshd"); };
log { source(src); filter(f_ssh); destination(ssh); flags(final); };
```

Убедитесь, что вы добавили этот блок выше ваших обычных log-строк. Из-за `flags(final)` в log-строке всё, что совпадает с фильтром «sshd», будет отправляться только в `ssh.log`, и обработка сообщения остановится в этой точке.

### Настройка в качестве loghost

Настроить вашу систему как loghost довольно просто. Добавьте следующее в конфигурацию и создайте нужный каталог. С этой простой конфигурацией имена файлов логов будут основаны на [FQDN](https://en.wikipedia.org/wiki/FQDN "wikipedia:FQDN") удалённого хоста и располагаться в `/var/log/remote/`. После создания каталога remote перечитайте конфигурацию syslog-ng.

```text
source net { udp(); };
destination remote { file("/var/log/remote/${FULLHOST}-log"); };
log { source(net); destination(remote); };
```

Можно также рассмотреть источник `default-network-drivers()`, который откроет несколько портов, принимая сообщения по нескольким различным syslog-протоколам, обычно развёрнутыми на практике.

### Улучшение производительности

Производительность syslog-ng можно улучшить разными способами:

#### Пишите с определённой периодичностью

Похоже, старая опция `sync(X)` теперь называется `flush_lines(_X_)`, где запись в файл буферизуется для `_X_` строк. По умолчанию — 100.

#### Увеличьте лимиты пакетной обработки источников

syslog-ng выполняет обработку сообщений параллельно, поскольку потоки сообщений принимаются множеством разных механизмов источников. Чтобы один источник не «уморил голодом» остальные, syslog-ng использует как поточность, так и лимиты на то, сколько сообщений он обработает от одного соединения источника за раз.

Это значит, что даже если приложение-источник отправило 1000 сообщений в плотном цикле, syslog-ng обработает их по 100 штук за раз (точный лимит задаётся `log-fetch-limit()`), и после каждых 100 будет перепроверять, есть ли другие соединения, нуждающиеся в обработке. Это вносит накладные расходы, и производительность syslog-ng можно значительно повысить, увеличив `log-fetch-limit()`.

Другой механизм, который можно тюнить под конкретный сценарий — размер окна, используемый для распространения противодавления (backpressure). Это параметр `log-iw-size()`, контролирующий, сколько сообщений может быть «в полёте», прежде чем место назначения подтвердит их. Увеличив `log-iw-size()`, вы позволите работать над большим числом сообщений, прежде чем syslog-ng остановится, чтобы дать местам назначения потребить сообщения.

Увеличение `log-iw-size()` увеличит использование памяти/дискового буфера, так как syslog-ng должен будет куда-то помещать сообщения.

#### Избегайте избыточной обработки и дискового пространства

Одно log-сообщение может отправляться в разные файлы логов несколько раз. Например, в исходном файле конфигурации есть следующие определения:

```text
destination cron { file("/var/log/cron.log"); };
destination messages { file("/var/log/messages"); };
filter f_cron { facility(cron); };
filter f_messages { level(info..warn)
       and not facility(auth, authpriv, mail, news); };
log { source(src); filter(f_cron); destination(cron); };
log { source(src); filter(f_messages); destination(messages); };
```

Одно и то же сообщение от facility `cron` попадёт и в файл `cron.log`, и в `messages`. Чтобы изменить это поведение, можно использовать флаг `final`, завершая дальнейшую обработку сообщения. Так, в этом примере, если мы хотим, чтобы сообщения от facility `cron` не попадали в файл messages, надо изменить log-строку cron на:

```text
log { source(src); filter(f_cron); destination(cron); flags(final); };
```

другой способ — исключить facility `cron` из фильтра `f_messages`:

```text
filter f_messages { level(info..warn) and not facility(cron, auth, authpriv, mail, news); };
```

### Место назначения PostgreSQL

В этом разделе используются две роли: `syslog` и `logwriter`. `syslog` будет администратором базы данных `syslog`, а `logwriter` сможет только добавлять записи в таблицу `logs`.

Создавать таблицу для логов больше не нужно. syslog-ng создаст её автоматически.

```text
psql -U postgres

postgres=# CREATE ROLE syslog WITH LOGIN;
postgres=# \password syslog    # Using the \password function is secure because
postgres=# CREATE ROLE logwriter WITH LOGIN;
postgres=# \password logwriter # the password is not saved in history.
postgres=# CREATE DATABASE syslog OWNER syslog;
postgres=# \q # You are done here for the moment
```

Отредактируйте `pg_hba.conf`, чтобы разрешить `syslog` и `logwriter` устанавливать соединение к PostgreSQL.

```text
/var/lib/postgres/data/pg_hba.conf

# TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD

host    syslog      logwriter   192.168.0.1/24        md5
host    syslog      syslog      192.168.0.10/32       md5
```

Затем [перечитайте](/title/Reload "Reload") конфигурацию `postgresql.service` (reload).

Отредактируйте `/etc/syslog-ng/syslog-ng.conf`, чтобы syslog-ng знал, куда и как писать в PostgreSQL. syslog-ng будет использовать роль `logwriter`.

```text
...
#
# SQL logging support
#

destination d_pgsql {
  sql(type(pgsql)
  host("127.0.0.1") username("logwriter") password("password")
  database("syslog")
  table("logs_${HOST}_${R_YEAR}${R_MONTH}${R_DAY}") #or whatever you want, example ${HOST}" for hosts, ${LEVEL}" for levels.. etc
  columns("datetime timestamp with time zone", "host varchar(32)", "program varchar(16)", "pid varchar(16)", "message varchar(200)")
  values("$R_ISODATE", "$HOST", "$PROGRAM", "$PID", "$MSG")
  indexes("datetime", "host", "program", "pid", "message"));
};

log { source(src); destination(d_pgsql); };
```

Наконец, [перезапустите](/title/Restart "Restart") `syslog-ng.service`.

И проверьте, что логи записываются.

```sql
psql -U logwriter -d syslog
syslog=> SELECT * FROM <your table name> ORDER BY datetime DESC LIMIT 10;
```

### Метки времени ISO 8601

**До**:

```text
#logger These timestamps are not optimal.
#tail -n 1 /var/log/messages.log
Feb 18 14:25:01 hostname logger: These timestamps are not optimal.
#
```

Добавьте `ts_format(iso);` в `/etc/syslog-ng/syslog-ng.conf` в секции options. Пример:

```text
options {
  stats_freq (0);
  flush_lines (0);
  time_reopen (10);
  log_fifo_size (1000);
  long_hostnames(off);
  use_dns (no);
  use_fqdn (no);
  create_dirs (no);
  keep_hostname (yes);
  perm(0640);
  group("log");
  ts_format(iso);      #make ISO-8601 timestamps
  #frac-digits(3);     #optional time to nearest millisecond
};
```

Затем [перечитайте](/title/Reload "Reload") конфигурацию `syslog-ng.service` (reload).

**После**:

```text
#logger Now THAT is a timestamp!
#tail -n 2 /var/log/messages.log
Feb 18 14:25:01 hostname logger: These timestamps are not optimal.
2010-02-18T20:23:58-05:00 electron logger: Now THAT is a timestamp!
#
```

### Метки времени RFC 3339

Так же, как выше, только используйте `rfc3339` вместо `iso` для `ts_format`.

### Уровни логирования

Уровни логирования определяются отдельно для каждого логируемого facility в конфиге syslog-ng. Доступные уровни перечислены в `/usr/include/sys/syslog.h`:

```text
/usr/include/sys/syslog.h
```

```c
define LOG_EMERG       0       /* system is unusable */
define LOG_ALERT       1       /* action must be taken immediately */
define LOG_CRIT        2       /* critical conditions */
define LOG_ERR         3       /* error conditions */
define LOG_WARNING     4       /* warning conditions */
define LOG_NOTICE      5       /* normal but significant condition */
define LOG_INFO        6       /* informational */
define LOG_DEBUG       7       /* debug-level messages */
```

### Макросы и переменные

Макросы можно использовать как в шаблонах, так и в именах файлов мест назначения. [Макросы syslog-ng OSE](https://axoflow.com/docs/axosyslog-core/chapter-manipulating-messages/customizing-message-format/reference-macros/).

Следующий код будет записывать строки лога в `/var/log/test.log` в формате `имямакроса=значение@`.

```text
template t_test { template("PROGRAM=$PROGRAM@PID=$PID@BSDTAG=$BSDTAG@TAG=$TAG@TAGS=$TAGS@FACILITY=$FACILITY@FACILITY_NUM=$FACILITY_NUM@LEVEL=$LEVEL@LEVEL_NUM=$LEVEL_NUM@PRI=$PRI@PRIORITY=$PRIORITY@FULLHOST=$FULLHOST@FULLHOST_FROM=$FULLHOST_FROM@HOST=$HOST@HOST_FROM=$HOST_FROM@LOGHOST=$LOGHOST@MSGHDR=$MSGHDR@MSGID=$MSGID@MSGONLY=$MSGONLY@MSG=$MSG@MESSAGE=$MESSAGE@SOURCE=$SOURCE@SOURCEIP=$SOURCEIP@SOURCE_IP=$SOURCE_IP@SEQNUM=$SEQNUM@UNIXTIME=$UNIXTIME@FULLDATE=$FULLDATE@ISODATE=$ISODATE@DATE=$DATE@STAMP=$STAMP@TZ=$TZ@TZOFFSET=$TZOFFSET@SEC=$SEC@MIN=$MIN@HOUR=$HOUR@HOUR12=$HOUR12@DAY=$DAY@WEEK=$WEEK@WEEK_DAY=$WEEK_DAY@WEEK_DAY_ABBREV=$WEEK_DAY_ABBREV@WEEK_DAY_NAME=$WEEK_DAY_NAME@MONTH=$MONTH@MONTH_ABBREV=$MONTH_ABBREV@MONTH_NAME=$MONTH_NAME@MONTH_WEEK=$MONTH_WEEK@YEAR=$YEAR@YEAR_DAY=$YEAR_DAY
\n"); template_escape(no); };

destination d_test { file("/var/log/test.log" template(t_test)); };

log { source(s_local); destination(d_test); flags(final); };
```

Вы можете создать свой список значений, как показано ниже, после перезапуска syslog-ng с командой: `tail /var/log/test.log|tr "@" "\n"`

```text
PROGRAM=kernel
PID=
BSDTAG=4A
TAG=04
TAGS=.source.s_local
FACILITY=kern
FACILITY_NUM=0
LEVEL=warning
LEVEL_NUM=4
PRI=4
PRIORITY=warning
FULLHOST=www.askapache.com
FULLHOST_FROM=www.askapache.com
HOST=www.askapache.com
HOST_FROM=www.askapache.com
LOGHOST=
MSGHDR=kernel:
MSGID=
MSGONLY=Firewall: *INVALID* IN=eth0 OUT= MAC=00:00 SRC=x.x.x.x DST=198.101.159.98 LEN=40 TOS=0x00 PREC=0x00 TTL=113 ID=7730 DF PROTO=TCP SPT=52369 DPT=80 WINDOW=0 RES=0x00 ACK RST URGP=0
MSG=Firewall: *INVALID* IN=eth0 OUT= MAC=00:00 SRC=x.x.x.x DST=198.101.159.98 LEN=40 TOS=0x00 PREC=0x00 TTL=113 ID=7730 DF PROTO=TCP SPT=52369 DPT=80 WINDOW=0 RES=0x00 ACK RST URGP=0
MESSAGE=Firewall: *INVALID* IN=eth0 OUT= MAC=00:00 SRC=x.x.x.x DST=198.101.159.98 LEN=40 TOS=0x00 PREC=0x00 TTL=113 ID=7730 DF PROTO=TCP SPT=52369 DPT=80 WINDOW=0 RES=0x00 ACK RST URGP=0
SOURCE=s_local
SOURCEIP=127.0.0.1
SOURCE_IP=
UNIXTIME=1369742458
FULLDATE=2013 May 28 08:00:58
ISODATE=2013-05-28T08:00:58-04:00
DATE=May 28 08:00:58
STAMP=2013-05-28T08:00:58-04:00
TZ=-04:00
TZOFFSET=-04:00
SEC=58
MIN=00
HOUR=08
HOUR12=
DAY=28
WEEK=21
WEEK_DAY=3
WEEK_DAY_ABBREV=Tue
WEEK_DAY_NAME=Tuesday
MONTH=05
MONTH_ABBREV=May
MONTH_NAME=May
MONTH_WEEK=4
YEAR=2013
YEAR_DAY=148
```

### Приём и разбор обычных syslog-сообщений

Начиная с версии 3.16, syslog-ng способен принимать и разбирать сообщения на наиболее распространённых портах с наиболее распространёнными парсерами с помощью source-драйвера [default-network-drivers()](https://axoflow.com/docs/axosyslog-core/chapter-sources/source-default-network-drivers/).

  * Порты прослушивания по умолчанию:

```text
* 514, both TCP and UDP, for RFC3164 (BSD-syslog) formatted traffic
* 601 TCP, for RFC5424 (IETF-syslog) formatted traffic
* 6514 TCP, for TLS-encrypted traffic
```

  * Автоматические парсеры:

```text
* Парсер сообщений RFC3164
* Парсер сообщений RFC5424
* [Парсер Cisco](https://axoflow.com/docs/axosyslog-core/chapter-parsers/cisco-parser/)
* Структурированный [парсер EWMM](https://axoflow.com/docs/axosyslog-core/chapter-concepts/concepts-message-structure/syslog-ng-message-format/)
* Другие адаптеры приложений (Splunk Common Information Model (CIM), iptables или sudo)
```

## Смотрите также

  * [Страница проекта syslog-ng на GitHub](https://github.com/syslog-ng/syslog-ng)
  * [Главная страница syslog-ng OSE с syslog-ng.com](https://www.syslog-ng.com/products/open-source-log-management/)
  * [Документация syslog-ng](https://axoflow.com/docs/axosyslog-core/)
  * [Страница документации syslog-ng на GitHub](https://github.com/axoflow/axosyslog-core-docs)
  * [Блоги syslog-ng](https://www.syslog-ng.com/community/)
  * [Блоги Axoflow о syslog-ng](https://axoflow.com/blog/)
  * [Страница проекта syslog-ng на Freecode](https://freshmeat.sourceforge.net/projects/syslog-ng/)
  * [Gentoo:syslog-ng](https://wiki.gentoo.org/wiki/syslog-ng "gentoo:syslog-ng")
  * [Gentoo:Security Handbook/Logging](https://wiki.gentoo.org/wiki/Security_Handbook/Logging "gentoo:Security Handbook/Logging")
  * [What is Syslog? Logging with PostgreSQL HOWTO](https://www.pcwdld.com/what-is-syslog-including-servers-and-ports)
  * [Википедия:ISO 8601](https://en.wikipedia.org/wiki/ISO_8601 "wikipedia:ISO 8601")
  * [RFC 3164](https://tools.ietf.org/html/rfc3164 "rfc:3164") — Протокол BSD syslog
  * [RFC 5424](https://tools.ietf.org/html/rfc5424 "rfc:5424") — Протокол Syslog
  * [RFC 5425](https://tools.ietf.org/html/rfc5425 "rfc:5425") — Отображение транспорта Transport Layer Security (TLS) для Syslog
  * [RFC 5426](https://tools.ietf.org/html/rfc5426 "rfc:5426") — Передача syslog-сообщений по UDP
  * [RFC 5427](https://tools.ietf.org/html/rfc5427 "rfc:5427") — Текстуальные соглашения для управления Syslog
  * [RFC 5428](https://tools.ietf.org/html/rfc5428 "rfc:5428") — MIB для устройств, совместимых с PacketCable и IPCablecom
  * [RFC 3339](https://tools.ietf.org/html/rfc3339 "rfc:3339") — Дата и время в интернете: метки времени
  * [Netconsole](/title/Netconsole "Netconsole") — модуль ядра, который отправляет все лог-сообщения ядра (т. е. [dmesg](/title/Dmesg "Dmesg")) по сети на другой компьютер без участия userspace (например, syslogd)

**********

[linux](/tags/linux.md)
[syslog](/tags/syslog.md)
[logs](/tags/logs.md)