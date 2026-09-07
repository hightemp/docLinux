# Как собирать, обрабатывать и пересылать логи с помощью Rsyslog

Источник: [How to Collect, Process, and Ship Log Data with Rsyslog](https://betterstack.com/community/guides/logging/rsyslog-explained/)

Stanley Ulili · Обновлено 14 января 2026

Современные вычислительные системы генерируют разнообразные лог-сообщения, охватывающие жизненно важную информацию из системных журналов (включая сообщения ядра и загрузки), приложений, баз данных и сетевых сервисов или демонов. Эти логи играют crucial роль в поиске и диагностике неисправностей, когда они возникают, и часто наиболее эффективны, когда они централизованы.

Для централизации логов можно использовать [log shipper](https://betterstack.com/community/guides/logging/log-shippers-explained/) — инструмент, предназначенный для сбора логов из различных источников и пересылки их в разные места. [Rsyslog](https://www.rsyslog.com/) — это известный log shipper, работающий на основе протокола [syslog](https://en.wikipedia.org/wiki/Syslog).

Rsyslog поставляется с продвинутыми возможностями, такими как фильтрация, и поддерживает как протокол [TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol), так и [UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol) для передачи сообщений. Он может обрабатывать логи, связанные с почтой, авторизациями, сообщениями ядра и многим другим.

Это всеобъемлющее руководство проведёт вас через использование Rsyslog для сбора, обработки и пересылки логов в центральное место. Сначала вы настроите Rsyslog на чтение логов из файла. Затем вы изучите, как обрабатывать логи с помощью Rsyslog. Наконец, вы централизуете логи в Better Stack.

## Предварительные требования

Перед началом убедитесь, что у вас есть доступ к системе с учётной записью не-root пользователя с привилегиями `sudo`.

Подтвердив эти предварительные требования, создайте директорию для хранения конфигурационных файлов и приложений:

```bash
mkdir log-processing-stack
```

Затем перейдите в созданную директорию:

```bash
cd log-processing-stack
```

С настроенной директорией вы готовы установить Rsyslog.

## Заметка на полях: пересылайте логи Rsyslog в Better Stack

Когда вы начнёте собирать интересные вам логи, вы можете пересылать их в [Better Stack](https://betterstack.com/telemetry?utm_content=callout&utm_medium=guides&utm_source=community&utm_term=rsyslog-explained) для централизованного хранения, мгновенного поиска, live tail и оповещений, не запуская собственный бэкенд логирования.

## Установка Rsyslog

Rsyslog предустановлен на многих системах и иногда нуждается в обновлении. Считается лучшей практикой устанавливать последнюю версию, чтобы у вас был доступ к самым свежим возможностям и улучшениям безопасности.

Ниже приведены инструкции по установке, проверенные на Ubuntu 22.04. Для других систем обратитесь к [документации Rsyslog](https://www.rsyslog.com/doc/v8-stable/installation/index.html) за руководством по установке.

Сначала установите последнюю версию Rsyslog:

```bash
sudo apt-get install rsyslog
```

Если вы видите сообщение «rsyslog is already the newest version», это означает, что у вас установлена последняя версия.

Подтвердите установку и проверьте версию Rsyslog следующей командой:

```bash
rsyslogd -v
```

Вы должны увидеть вывод, подобный этому:

```text
rsyslogd  8.2312.0 (aka 2023.12) compiled with:
    PLATFORM:               x86_64-pc-linux-gnu
    PLATFORM (lsb_release -d):
    FEATURE_REGEXP:             Yes
    GSSAPI Kerberos 5 support:      Yes
    FEATURE_DEBUG (debug build, slow code): No
    32bit Atomic operations supported:  Yes
    64bit Atomic operations supported:  Yes
    memory allocator:           system default
    Runtime Instrumentation (slow code):    No
    uuid support:               Yes
    systemd support:            Yes
    Config file:                /etc/rsyslog.conf
    PID file:               /run/rsyslogd.pid
    Number of Bits in RainerScript integers: 64
```

Кроме того, убедитесь, что сервис Rsyslog активен и работает:

```bash
systemctl status rsyslog
```

Вы должны увидеть статус «active (running)», подтверждающий, что Rsyslog работоспособен:

```text
● rsyslog.service - System Logging Service
     Loaded: loaded (/usr/lib/systemd/system/rsyslog.service; enabled; preset: enabled)

     Active: active (running) since Thu 2025-05-22 09:36:01 UTC; 2 weeks 0 days ago

TriggeredBy: ● syslog.socket
       Docs: man:rsyslogd(8)
             man:rsyslog.conf(5)
             https://www.rsyslog.com/doc/
   Main PID: 927 (rsyslogd)
      Tasks: 4 (limit: 4540)
      Memory: 64.3M (peak: 65.0M)
         CPU: 1min 6.787s
      CGroup: /system.slice/rsyslog.service
              └─927 /usr/sbin/rsyslogd -n -iNONE

Warning: some journal files were not opened due to insufficient permissions.
```

С успешно установленным и работающим Rsyslog давайте разберёмся, как он работает.

## Как работает Rsyslog

Прежде чем углубляться в то, как Rsyslog собирает логи приложений, важно понять, как он работает с системными логами.

![Диаграмма, показывающая демонов, отправляющих логи в Rsyslog и перенаправляющих их в отдельные файлы](/images/939365a18ce8346a55c8e5485e26f8b8.png)

В вашей системе различные приложения вроде SSHD, почтовых клиентов/серверов и задач cron генерируют логи через частые интервалы. Эти приложения записывают лог-сообщения в файл `/dev/log`, как если бы это был обычный файл (псевдоустройство).

Демон Rsyslog следит за этим файлом, собирая логи по мере их записи, и перенаправляет их в отдельные текстовые файлы в директории `/var/log`, включая файл `/var/log/syslog`. Rsyslog может маршрутизировать логи в подходящие файлы,.inspecting информацию заголовков, такую как приоритет и источник сообщения, которую он использует для фильтрации.

Маршрутизация этих сообщений основана на правилах, определённых в файле `50-default.conf`, расположенном в директории `/etc/rsyslog.d/`, который мы вскоре рассмотрим. Rsyslog работает с конфигурациями по умолчанию, будь то свежая установка или уже существующая система.

Однако данные поступают из разных источников, и у этих источников может не быть правил в конфигурациях по умолчанию.

Опираясь на это знание, Rsyslog можно расширить, чтобы собирать логи из дополнительных входов и перенаправлять их в разные места назначения, включая удалённые, как показано на диаграмме ниже:

![Диаграмма Rsyslog](/images/e28b7c27537acd79d7b2df67fbaa3d54.png)

Чтобы понять этот процесс, представьте Rsyslog как конвейер. С одного конца Rsyslog собирает входные данные, преобразует их и пересылает на другой конец — место назначения.

Это можно сделать с помощью пользовательского конфигурационного файла в директории `/etc/rsyslog.d/` со следующей структурой:

```text
module(load="<module_name>")

# Collect logs
input(...)

# Modify logs
template(name="<template_name>") {}

# Redirect logs to the destination
action(type="<module_name>")
```

Основные компоненты:

  * `input`: собирает логи из различных источников.
  * `template`: изменяет формат лог-сообщений.
  * `action`: доставляет логи в разные места назначения.

Rsyslog широко использует модули для выполнения своих задач.

### Входы Rsyslog

В Rsyslog есть модули, предназначенные для сбора логов из различных источников, определяемые по именам с префиксом `im`. Вот несколько примеров таких модулей ввода:

  * [imhttp](https://www.rsyslog.com/doc/master/configuration/modules/imhttp.html): собирает текстовые сообщения через HTTP.

  * [imjournal](https://www.rsyslog.com/doc/master/configuration/modules/imjournal.html): извлекает сообщения системного журнала в Syslog.

  * [imfile](https://www.rsyslog.com/doc/master/configuration/modules/imfile.html): читает текстовые файлы и преобразует их содержимое в сообщения Syslog.

  * [imdocker](https://www.rsyslog.com/doc/master/configuration/modules/imdocker.html): собирает логи из Docker-контейнеров с помощью Docker REST API.

### Модули изменения сообщений Rsyslog

Для изменения лог-сообщений Rsyslog предоставляет [модули изменения сообщений](https://www.rsyslog.com/doc/master/configuration/modules/idx_messagemod.html), обычно с префиксом `mm`:

  * [mmjsonparse](https://www.rsyslog.com/doc/master/configuration/modules/mmjsonparse.html): разбирает структурированные лог-сообщения, соответствующие спецификации CEE/lumberjack.

  * [mmfields](https://www.rsyslog.com/doc/master/configuration/modules/mmfields.html): извлекает определённые поля из записей логов.

  * [mmkubernetes](https://www.rsyslog.com/doc/master/configuration/modules/mmkubernetes.html): добавляет метаданные Kubernetes к каждому событию лога.

  * [mmanon](https://www.rsyslog.com/doc/master/configuration/modules/mmanon.html): анонимизирует IP-адреса для приватности.

### Выходные модули Rsyslog

Rsyslog предлагает широкий набор [выходных модулей](https://www.rsyslog.com/doc/master/configuration/modules/idx_output.html), определяемых по именам с префиксом `om`. Эти модули позволяют пересылать лог-сообщения в разные места назначения:

  * [omfile](https://www.rsyslog.com/doc/master/configuration/modules/omfile.html): записывает записи логов в файл на локальной системе.

  * [ommysql](https://www.rsyslog.com/doc/master/configuration/modules/ommysql.html): отправляет записи логов в базу данных MySQL.

  * [omrabbitmq](https://www.rsyslog.com/doc/master/configuration/modules/omrabbitmq.html): пересылает данные логов в RabbitMQ — популярный брокер сообщений.

  * [omelasticsearch](https://www.rsyslog.com/doc/master/configuration/modules/omelasticsearch.html): доставляет вывод логов в Elasticsearch — мощный поисковый и аналитический движок.

Теперь, когда у вас есть представление о доступных модулях Rsyslog и том, что они делают, давайте подробнее разберём конфигурационный файл Rsyslog.

## Понимание конфигурации Rsyslog

Когда Rsyslog запускается в вашей системе, он работает с конфигурационным файлом по умолчанию. Он собирает логи из различных процессов и направляет их в текстовые файлы в директориях `/var/log`.

Rsyslog полагается на правила, предопределённые в конфигурационном файле по умолчанию. Вы также можете определять собственные правила, глобальные директивы или модули.

### Правила Rsyslog

Чтобы понять, как работают правила, откройте конфигурационный файл `50-default.conf` в вашем любимом текстовом редакторе. Это руководство использует `nano` — текстовый редактор командной строки:

```bash
sudo nano /etc/rsyslog.d/50-default.conf
```

В начальной части файла вы найдёте содержимое, подобное этому (сокращено для краткости):

```text
...
auth,authpriv.*                 /var/log/auth.log
*.*;auth,authpriv.none          -/var/log/syslog
#cron.*                         /var/log/cron.log
#daemon.*                       -/var/log/daemon.log
kern.*                          -/var/log/kern.log
...
```

Строки в файле — это правила. Правило состоит из фильтра для выбора лог-сообщений и действия, указывающего путь для отправки логов. Строки, начинающиеся с `#`, — комментарии, они не выполняются.

Рассмотрим эту строку:

```text
kern.*                          -/var/log/kern.log
```

Эту строку можно разделить на селектор, фильтрующий сообщения syslog, — `kern.*` — и действие, указывающее путь для пересылки логов, — `-/var/log/kern.log`.

Давайте детально рассмотрим селектор `kern.*`. `kern.*` — это фильтр на основе Facility/Priority, часто используемый метод фильтрации сообщений syslog.

`kern.*` можно интерпретировать так:

```text
FACILITY.PRIORITY
```

  * **FACILITY**: подсистема, генерирующая лог-сообщения. `kern` — пример средства (facility) наряду с другими подсистемами вроде `authpriv`, `cron`, `user`, `daemon`, `mail`, `auth`, `syslog`, `lpr`, `news`, `uucp` и т.д. Чтобы определить все средства, можно использовать `*`.

  * **PRIORITY**: задаёт приоритет лог-сообщения. Приоритеты включают `debug`, `info`, `notice`, `warning`, `warn` (то же, что `warning`), `err`, `error` (то же, что err), `crit`, `alert`, `emerg`, `panic`. Если вы хотите отправлять логи с любым уровнем приоритета, можно использовать `*`. Опционально можно использовать ключевое слово приоритета `none` для средств без указанных приоритетов.

Фильтр и действие разделяются одним или несколькими пробелами или табами.

Последняя часть, `-/var/log/kern.log`, — это действие, указывающее целевой файл, куда отправляется содержимое.

В этом конфигурационном файле большинство правил направляет вывод в различные файлы, которые вы можете найти в `/var/log`.

Закройте конфигурационный файл и выполните следующую команду, чтобы вывести всё содержимое директории `/var/log`:

```bash
ls -l /var/log/
```

Вывод будет включать такие файлы:

```text
total 44
total 44
-rw-r--r--  1 root      root                 0 Oct 22 04:33 alternatives.log
drwxr-xr-x  2 root      root              4096 Oct 27 08:37 apt

-rw-r-----  1 syslog    adm               7596 Oct 27 08:44 auth.log

-rw-r--r--  1 root      root                 0 Oct 22 04:33 bootstrap.log
-rw-rw----  1 root      utmp                 0 Feb 17  2023 btmp

-rw-r-----  1 syslog    adm             105503 Oct 27 08:33 cloud-init.log

-rw-r-----  1 root      adm               5769 Oct 27 08:33 cloud-init-output.log

drwxr-xr-x  2 root      root              4096 Feb 10  2023 dist-upgrade

-rw-r-----  1 root      adm              46597 Oct 27 08:33 dmesg

-rw-r--r--  1 root      root              6664 Oct 27 08:37 dpkg.log
-rw-r--r--  1 root      root             32032 Oct 27 08:33 faillog
drwxr-sr-x+ 4 root      systemd-journal   4096 Oct 27 08:33 journal

-rw-r-----  1 syslog    adm              70510 Oct 27 08:44 kern.log

drwxr-xr-x  2 landscape landscape         4096 Oct 27 08:33 landscape
-rw-rw-r--  1 root      utmp            292292 Oct 27 08:35 lastlog
drwx------  2 root      root              4096 Feb 17  2023 private

-rw-r-----  1 syslog    adm              136675 Oct 27 08:44 syslog

-rw-r--r--  1 root      root              4748 Oct 27 08:37 ubuntu-advantage.log

-rw-r-----  1 syslog    adm              10487 Oct 27 08:44 ufw.log

drwxr-x---  2 root      adm               4096 Oct 22 04:28 unattended-upgrades

-rw-rw-r--  1 root      utmp              3840 Oct 27 08:35 wtmp
```

Большинство файлов, создаваемых Rsyslog, принадлежат пользователю `syslog` и группе `adm`. Другие приложения помимо Rsyslog также создают логи в этой директории, например MySQL и Nginx.

Такое поведение создания файлов с этими атрибутами определено в другом конфигурационном файле по умолчанию — `/etc/rsyslog.conf`.

### Глобальные директивы и модули Rsyslog

Когда Rsyslog работает, он читает файл `/etc/rsyslog.conf` — ещё одну предопределённую конфигурацию по умолчанию. Этот файл содержит глобальные директивы, модули и ссылки на все конфигурационные файлы в директории `/etc/rsyslog.d/`, включая уже рассмотренный нами `/etc/rsyslog.d/50-default.conf`.

Откройте конфигурационный файл `/etc/rsyslog.conf` следующей командой:

```bash
nano /etc/rsyslog.conf
```

Найдите следующую секцию ближе к концу файла:

```text
...
#
# Set the default permissions for all log files.
#
$FileOwner syslog
$FileGroup adm
$FileCreateMode 0640
$DirCreateMode 0755
$Umask 0022
$PrivDropToUser syslog
$PrivDropToGroup syslog
...
```

В этом файле есть свойства вроде `$FileOwner` и `$FileGroup`, которые задают владельца и группу файла, а также права доступа к файлам. Если вам нужно изменить владение, обратите внимание на эту секцию. Любое ключевое слово с префиксом `$` — это переменная, которую вы можете изменить.

Ниже по конфигурационному файлу вы найдёте строки вроде:

```text
...
#
# Where to place spool and state files
#
$WorkDirectory /var/spool/rsyslog

#
# Include all config files in /etc/rsyslog.d/
#
$IncludeConfig /etc/rsyslog.d/*.conf
```

`$WorkDirectory` задаёт расположение, которое Rsyslog использует для хранения файлов состояния, а `$IncludeConfig` подключает все конфигурационные файлы, определённые в директории `/etc/rsyslog.d`. Rsyslog прочитает любой конфигурационный файл, который вы создадите в этой директории. Здесь вы будете определять свои пользовательские конфигурации.

Теперь, когда вы понимаете, что у Rsyslog есть конфигурации по умолчанию, которые маршрутизируют большинство системных логов в разные файлы в `/var/log`, вы готовы создать демо-приложение, генерирующее логи. Позже вы настроите Rsyslog на чтение этих логов.

## Разработка демо-приложения логирования

В этом разделе вы создадите приложение логирования, написанное на скриптовом языке [Bash](https://en.wikipedia.org/wiki/Bash_\(Unix_shell\)). Приложение будет генерировать JSON-логи через регулярные интервалы, имитируя реальное приложение с высоким трафиком.

Для начала убедитесь, что вы находитесь в директории `processing-stack/logify`, и создайте поддиректорию для демо-приложения логирования:

```bash
mkdir logify
```

Перейдите в директорию:

```bash
cd logify
```

Затем создайте файл `logify.sh`:

```bash
nano logify.sh
```

В файл `logify.sh` добавьте следующий код для генерации логов:

```bash
#!/bin/bash
filepath="/var/log/logify/app.log"

create_log_entry() {
    local info_messages=("Connected to database" "Task completed successfully" "Operation finished" "Initialized application")
    local random_message=${info_messages[$RANDOM % ${#info_messages[@]}]}
    local http_status_code=200
    local ip_address="127.0.0.1"
    local level=30
    local pid=$$
    local ssn="407-01-2433"
    local time=$(date +%s)
    local log='{"status": '$http_status_code', "ip": "'$ip_address'", "level": '$level', "msg": "'$random_message'", "pid": '$pid', "ssn": "'$ssn'", "time": '$time'}'
    echo "$log"
}

while true; do
    log_record=$(create_log_entry)
    echo "${log_record}" >> "${filepath}"
    sleep 3
done
```

Функция `create_log_entry()` генерирует структурированные логи в формате JSON с такими деталями, как уровень серьёзности, сообщение и код статуса HTTP. Затем скрипт входит в бесконечный цикл, который многократно вызывает функцию `create_log_entry()` для записи логов в указанный файл в директории `/var/log/logify`.

Закончив писать код, сохраните и закройте файл. Затем сделайте файл исполняемым:

```bash
chmod +x logify.sh
```

Затем создайте директорию `/var/log/logify` для хранения логов приложения:

```bash
sudo mkdir /var/log/logify
```

Назначьте текущего вошедшего пользователя из переменной `$USER` владельцем директории `/var/log/logify`:

```bash
sudo chown -R $USER:$USER /var/log/logify/
```

Запустите скрипт `logify.sh` в фоне:

```bash
./logify.sh &
```

Знак `&` говорит ОС запустить скрипт в фоне, позволяя вам продолжать использовать терминал для других задач, пока программа работает.

Когда вы нажмёте Enter, скрипт начнёт работать, и вы увидите что-то вроде:

```text
[1] 652089
```

Здесь `652089` — это ID процесса, который можно использовать для завершения скрипта при необходимости.

Теперь посмотрите содержимое `app.log` командой `tail`:

```bash
tail -n 4 /var/log/logify/app.log
```

Вывод покажет структурированные JSON-логи, подобные этим:

```text
{"status": 200, "ip": "127.0.0.1", "level": 30, "emailAddress": "user@mail.com", "msg": "Connected to database", "pid": 169516, "ssn": "407-01-2433", "timestamp": 1749119648}
{"status": 200, "ip": "127.0.0.1", "level": 30, "msg": "Operation finished", "pid": 652089, "ssn": "407-01-2433", "time": 1749119651}
{"status": 200, "ip": "127.0.0.1", "level": 30, "emailAddress": "user@mail.com", "msg": "Task completed successfully", "pid": 169516, "ssn": "407-01-2433", "timestamp": 1749119651}
{"status": 200, "ip": "127.0.0.1", "level": 30, "msg": "Task completed successfully", "pid": 652089, "ssn": "407-01-2433", "time": 1749119654}
```

С приложением, генерирующим структурированные JSON-логи, вы готовы использовать Rsyslog для чтения этих записей логов.

## Начало работы с Rsyslog

Теперь, когда вы разработали приложение, производящее логи через регулярные интервалы, вы будете использовать Rsyslog для чтения логов из файла и преобразования их в syslog-сообщения, сохраняемые в файл `/var/log/syslog`.

Для начала создайте конфигурационный файл с выбранным вами именем в директории `/etc/rsyslog.d`:

```bash
sudo nano /etc/rsyslog.d/51-rsyslog-logify.conf
```

В файл `51-rsyslog-logify.conf` добавьте следующую конфигурацию:

```text
global(
  workDirectory="/var/spool/rsyslog"
)

# Load the imfile module to read logs from a file
module(load="imfile")

# Define a new input for reading logs from a file
input(type="imfile"
      File="/var/log/logify/app.log"
      Tag="FileLogs"
      PersistStateInterval="10"
      Facility="local0")

# Send logs with the specified tag to the console
if $syslogtag == 'FileLogs' then {
    action(type="omfile"
           file="/var/log/syslog")
}
```

В первой строке директива `global()` настраивает рабочую директорию для хранения файлов состояния. Эти файлы позволяют Rsyslog отслеживать, какие части логов он уже обработал.

Далее метод `module()` используется для загрузки модуля [`imfile`](https://www.rsyslog.com/doc/v8-stable/configuration/modules/imfile.html), который используется для чтения логов из файлов.

После этого вы определяете вход с помощью модуля `imfile` для чтения логов с указанного пути в параметре `File`. Затем вы добавляете тег `FileLogs` к каждой обработанной записи лога, а параметр `PersistStateInterval` указывает, как часто должен записываться файл состояния при чтении логов.

Наконец, условное выражение проверяет, равен ли тег лога тегу `FileLogs`. Если это так, определяется действие с использованием модуля `omfile` для пересылки логов в файл `/var/log/syslog`.

Закончив, сохраните и закройте конфигурационный файл.

Перед перезапуском Rsyslog полезно проверить конфигурационный файл на синтаксические ошибки. Введите следующую команду, чтобы проверить, нет ли в конфигурационном файле синтаксических ошибок:

```bash
rsyslogd -f /etc/rsyslog.d/51-rsyslog-logify.conf -N1
```

Когда в конфигурационном файле нет ошибок, вы увидите вывод, подобный этому:

```text
rsyslogd: version 8.2312.0, config validation run (level 1), master config /etc/rsyslog.d/51-rsyslog-logify.conf
rsyslogd: End of config validation run. Bye.
```

Теперь перезапустите Rsyslog:

```bash
sudo systemctl restart rsyslog.service
```

Когда Rsyslog перезапустится, он начнёт отправлять логи в `/var/log/syslog`. Чтобы смотреть логи в реальном времени по мере их записи, введите следующую команду:

```bash
sudo tail -f /var/log/syslog
```

Записи логов будут отображаться, показывая метку времени, имя хоста, тег лога и само сообщение:

```text
2025-06-05T10:35:36.187305+00:00 ubuntu FileLogs {"status": 200, "ip": "127.0.0.1", "level": 30, "emailAddress": "user@mail.com", "msg": "Task completed successfully", "pid": 169516, "ssn": "407-01-2433", "timestamp": 1749119736}
2025-06-05T10:35:36.187305+00:00 ubuntu FileLogs {"status": 200, "ip": "127.0.0.1", "level": 30, "emailAddress": "user@mail.com", "msg": "Task completed successfully", "pid": 169516, "ssn": "407-01-2433", "timestamp": 1749119736}
2025-06-05T10:35:38.913045+00:00 ubuntu FileLogs {"status": 200, "ip": "127.0.0.1", "level": 30, "msg": "Initialized application", "pid": 652089, "ssn": "407-01-2433", "time": 1749119738}
2025-06-05T10:35:38.913045+00:00 ubuntu FileLogs {"status": 200, "ip": "127.0.0.1", "level": 30, "msg": "Initialized application", "pid": 652089, "ssn": "407-01-2433", "time": 1749119738}
...
```

Поскольку файл `/var/log/syslog` содержит логи и других процессов, часто можно видеть логи из таких источников, как `kernel`.

Теперь, когда Rsyslog может читать логи приложений, вы можете дополнительно обрабатывать лог-сообщения по мере необходимости.

## Преобразование логов с помощью Rsyslog

Когда Rsyslog читает записи логов, вы можете преобразовывать их перед отправкой на выход. Вы можете обогатить их новыми полями или отформатировать иначе. Одно из распространённых преобразований — форматирование логов в JSON с помощью шаблонов Rsyslog.

### Форматирование логов в JSON с помощью шаблонов Rsyslog

Rsyslog позволяет форматировать логи в различные форматы с помощью [шаблонов](https://www.rsyslog.com/doc/v8-stable/configuration/templates.html). По умолчанию Rsyslog автоматически форматирует лог-сообщения, даже если шаблоны не указаны, используя встроенные шаблоны. Однако вы можете захотеть форматировать логи в JSON — структурированном и машиночитаемом виде.

Если посмотреть на логи, которые Rsyslog сейчас форматирует, вы заметите, что они не структурированы:

```text
2025-06-05T10:35:38.913045+00:00 ubuntu FileLogs {"status": 200, "ip": "127.0.0.1", "level": 30, "msg": "Initialized application", "pid": 652089, "ssn": "407-01-2433", "time": 1749119738}
```

Многие удалённые места назначения предпочитают структурированные логи, поэтому структурировать лог-сообщения — хорошая практика.

В Rsyslog вы можете использовать шаблоны с объектом `template()` для изменения и структурирования логов. Откройте конфигурационный файл:

```bash
sudo nano /etc/rsyslog.d/51-rsyslog-logify.conf
```

Добавьте шаблон в конфигурационный файл:

```text
...
input(type="imfile"
      File="/var/log/logify/app.log"
      Tag="FileLogs"
      PersistStateInterval="10"
      Facility="local0")

template(name="json-template" type="list" option.jsonf="on") {

    property(outname="@timestamp" name="timereported" dateFormat="rfc3339" format="jsonf")

    property(outname="host" name="hostname" format="jsonf")

    property(outname="severity" name="syslogseverity" caseConversion="upper" format="jsonf" datatype="number")

    property(outname="facility" name="syslogfacility" format="jsonf" datatype="number")

    property(outname="syslog-tag" name="syslogtag" format="jsonf")

    property(outname="source" name="app-name" format="jsonf" onEmpty="null")

    property(outname="message" name="msg" format="jsonf")

}

if $syslogtag == 'FileLogs' then {
    action(
        type="omfile"
        file="/var/log/syslog"

        template="json-template"

    )
}
```

В приведённой конфигурации вы определяете шаблон `json-template` с помощью объекта `template()`. Этот шаблон форматирует syslog-сообщение как JSON. Шаблон включает различные [property-инструкции](https://www.rsyslog.com/doc/v8-stable/configuration/templates.html#property-statement) для добавления полей к syslog-сообщению. Каждая property-инструкция указывает `name` свойства для доступа и `outname`, который определяет имя выходного поля в JSON-объекте. Параметр `format` установлен в `"jsonf"`, чтобы форматировать свойство как JSON. Некоторые свойства включают метку времени, хост, syslog-тег и само syslog-сообщение.

Наконец, вы добавляете параметр `template` в секцию action, ссылаясь на только что определённый `json-template`.

После сохранения файла перезапустите Rsyslog:

```bash
sudo systemctl restart rsyslog
```

Теперь проверьте записываемые логи:

```bash
sudo tail -f /var/log/syslog
```

Вывод показывает, что syslog-сообщения теперь отформатированы как JSON. Они также включают дополнительные поля, дающие больше контекста:

```text
{"@timestamp":"2025-06-05T10:40:25.189748+00:00", "host":"ubuntu", "severity":5, "facility":16, "syslog-tag":"FileLogs", "source":"FileLogs", "message":"{\"status\": 200, \"ip\": \"127.0.0.1\", \"level\": 30, \"emailAddress\": \"user@mail.com\", \"msg\": \"Task completed successfully\", \"pid\": 169516, \"ssn\": \"407-01-2433\", \"timestamp\": 1749120025}"}
...
```

Логи в выводе теперь структурированы в формате JSON и содержат более детальную информацию. Далее вы добавите пользовательские поля к событию лога.

### Добавление пользовательских полей с помощью Rsyslog

В Rsyslog вы можете добавлять пользовательские поля к записям логов с помощью [constant-инструкций](https://www.rsyslog.com/doc/v8-stable/configuration/templates.html#constant-statement). Эти инструкции позволяют вставлять фиксированные значения в лог-сообщения.

Сначала откройте конфигурационный файл:

```bash
sudo nano /etc/rsyslog.d/51-rsyslog-logify.conf
```

Добавьте новую constant-инструкцию, чтобы включить пользовательское поле с именем `environment` со значением `dev`:

```text
template(name="json-template" type="list" option.jsonf="on") {
    property(outname="@timestamp" name="timereported" dateFormat="rfc3339" format="jsonf")
    property(outname="host" name="hostname" format="jsonf")
    property(outname="severity" name="syslogseverity" caseConversion="upper" format="jsonf" datatype="number")
    property(outname="facility" name="syslogfacility" format="jsonf" datatype="number")
    property(outname="syslog-tag" name="syslogtag" format="jsonf")
    property(outname="source" name="app-name" format="jsonf" onEmpty="null")
    property(outname="message" name="msg" format="jsonf")

    constant(outname="environment" value="dev" format="jsonf")

}
```

В приведённой конфигурации добавлена инструкция `constant` с `outname`, установленным в `environment`, и `value`, установленным в `dev`. Эта constant-инструкция вставляет фиксированное поле с именем `environment` со значением `dev` в каждую запись лога.

Сохраните и закройте конфигурационный файл. Затем перезапустите Rsyslog, чтобы применить изменения:

```bash
sudo systemctl restart rsyslog
```

Чтобы проверить, добавлено ли пользовательское поле, выполните tail файла syslog:

```bash
sudo tail -f /var/log/syslog
```

Вы увидите, что Rsyslog включил поле `environment` в каждую запись лога в конце события:

```text
{"@timestamp":"2025-06-05T10:42:31.631819+00:00", "host":"ubuntu", "severity":5, "facility":16, "syslog-tag":"FileLogs", "source":"FileLogs", "message":"{\"status\": 200, \"ip\": \"127.0.0.1\", \"level\": 30, \"emailAddress\": \"user@mail.com\", \"msg\": \"Operation finished\", \"pid\": 169516, \"ssn\": \"407-01-2433\", \"timestamp\": 1749120151}", "environment": "dev"}
```

Теперь, когда вы можете добавлять пользовательские поля к событиям логов, вы готовы пересылать логи в Better Stack.

## Настройка Rsyslog с Better Stack

Better Stack предоставляет автоматизированный скрипт установки, который настраивает Rsyslog для пересылки логов. Выполните следующую команду, заменив `$SOURCE_TOKEN` на ваш фактический source token из Better Stack:

```bash
wget -qO- https://telemetry.betterstack.com/rsyslog/$SOURCE_TOKEN | sudo sh
```

Этот скрипт автоматически: — Определит конфигурацию вашей системы — Создаст необходимую конфигурацию Rsyslog для Better Stack как `70-logtail.conf` — Настроит защищённые TLS-соединения с серверами Better Stack

Если вы хотите simplest путь, посмотрите краткое руководство ниже. Оно показывает, как настроить коллектор Better Stack и начать отправку логов из окружения Docker или Kubernetes за считанные минуты с разумными значениями по умолчанию для батчинга, сжатия и сэмплирования.

Если вы предпочитаете продолжать использовать существующий пайплайн Rsyslog, пропустите видео и следуйте пошаговым инструкциям в этом разделе.

Сначала установите требуемый TLS-пакет для защищённой пересылки логов:

```bash
sudo apt-get install rsyslog-gnutls
```

Затем создайте бесплатный [аккаунт Better Stack](https://telemetry.betterstack.com/users/sign_up). После регистрации перейдите в секцию **Sources** на дашборде и нажмите кнопку **Connect source**:

![Скриншот со стрелкой, указывающей на «Connect source»](/images/13b7403ce4e5d7f6ac1e4c7b72a7fa30.png)

Укажите имя для вашего источника, например «Logify logs», и выберите «Rsyslog» в качестве платформы:

![Скриншот интерфейса Better Stack с источником «Logify logs» и платформой «Rsyslog»](/images/d40016054edc0da54aa1629aa835b73e.png)

После создания источника скопируйте **Source Token** и **Ingesting Host**, предоставленные Better Stack:

![Скриншот со стрелкой, указывающей на поле «Source Token»](/images/d911aa1039dab8a9e75af7140ee5ac9e.png)

Выполните следующую команду, заменив `$SOURCE_TOKEN` на ваш фактический source token из Better Stack:

```bash
wget -qO- https://telemetry.betterstack.com/rsyslog/$SOURCE_TOKEN | sudo sh
```

```text
Starting Betterstackdata.com automatic rsyslog setup

Setting up rsyslog...

[0/3] Checking prerequisites
- wget OK

[1/3] Testing Let's Encrypt SSL certificates setup
- curl OK
- OK

[2/3] Writing rsyslog configuration into /etc/rsyslog.d/70-logtail.conf

[3/3] Restarting rsyslog

Better Stack rsyslog setup is complete.
```

Этот скрипт автоматически: — Определит конфигурацию вашей системы — Создаст необходимую конфигурацию Rsyslog для Better Stack — Настроит защищённые TLS-соединения с серверами Better Stack

Однако, поскольку вы хотите отправлять только логи вашего приложения logify (а не все системные логи), вам нужно изменить сгенерированную конфигурацию, чтобы она нацеливалась именно на логи вашего приложения.

После запуска скрипта установки Better Stack вам нужно кастомизировать файл `70-logtail.conf`, чтобы читать логи вашего приложения logify.

Откройте конфигурационный файл Better Stack для редактирования:

```bash
sudo nano /etc/rsyslog.d/70-logtail.conf
```

Файл будет содержать конфигурацию пересылки Better Stack. Вам нужно добавить конфигурацию чтения файла в начало этого файла. Добавьте следующие строки в самое начало файла, перед любым существующим содержимым:

```text
global(DefaultNetstreamDriverCAFile="/etc/ssl/certs/ca-certificates.crt")

global(
  workDirectory="/var/spool/rsyslog"
)

# Load the imfile module to read logs from a file
module(load="imfile")

# Define a new input for reading logs from a file
input(type="imfile"
      File="/var/log/logify/app.log"
      Tag="FileLogs"
      PersistStateInterval="10"
      Facility="local0")

template(name="LogtailFormat" type="list") {
  ...
}
# Existing Better Stack configuration below...
```

Далее вам нужно изменить секцию action, чтобы отправлять в Better Stack только ваши логи logify. Найдите секцию `action` в файле (она будет содержать `type="omfwd"`) и оберните её условным выражением.

Сгенерированная конфигурация будет выглядеть так:

```text
...
action(
 type="omfwd"
 protocol="tcp"
 target="YOUR_INGESTING_HOST"
 port="6514"
 template="LogtailFormat"
 TCP_Framing="octet-counted"
 StreamDriver="gtls"
 StreamDriverMode="1"
 StreamDriverAuthMode="x509/name"
 StreamDriverPermittedPeers="*.betterstackdata.com"
 queue.spoolDirectory="/var/spool/rsyslog"
 queue.filename="logtail"
 queue.maxdiskspace="75m"
 queue.type="LinkedList"
 queue.saveonshutdown="on"
)
```

**Важно**: вы должны обернуть весь этот блок `action` условным выражением, чтобы фильтровать только ваши логи logify. Измените его так:

```text
# Send only FileLogs (our logify application) to Better Stack
if $syslogtag == 'FileLogs' then {
    action(
     type="omfwd"
     protocol="tcp"
     target="YOUR_INGESTING_HOST"
     port="6514"
     template="LogtailFormat"
     TCP_Framing="octet-counted"
     StreamDriver="gtls"
     StreamDriverMode="1"
     StreamDriverAuthMode="x509/name"
     StreamDriverPermittedPeers="*.betterstackdata.com"
     queue.spoolDirectory="/var/spool/rsyslog"
     queue.filename="logtail"
     queue.maxdiskspace="75m"
     queue.type="LinkedList"
     queue.saveonshutdown="on"
    )
}
```

Без этого условного выражения Rsyslog будет отправлять ВСЕ системные логи в Better Stack, а не только логи вашего приложения logify.

Поскольку вы теперь читаете логи напрямую в конфигурации Better Stack, удалите предыдущую локальную конфигурацию, чтобы избежать конфликтов:

```bash
sudo rm /etc/rsyslog.d/51-rsyslog-logify.conf
```

Перед перезапуском Rsyslog проверьте конфигурационный файл на синтаксические ошибки:

```bash
rsyslogd -f /etc/rsyslog.d/70-logtail.conf -N1
```

Когда в конфигурационном файле нет ошибок, вы увидите вывод, подобный этому:

```text
rsyslogd: version 8.2312.0, config validation run (level 1), master config /etc/rsyslog.d/70-logtail.conf
rsyslogd: End of config validation run. Bye.
```

Теперь перезапустите Rsyslog, чтобы применить новую конфигурацию:

```bash
sudo systemctl restart rsyslog
```

Чтобы убедиться, что ваши логи отправляются в Better Stack, сначала проверьте, что скрипт logify всё ещё работает:

```bash
ps aux | grep logify
```

```text
dev       169516  0.0  0.0   7740  3456 ?        S    Jun02   3:06 /bin/bash ./logify.sh
```

Если скрипт не работает, перезапустите его:

```bash
cd log-processing-stack/logify
./logify.sh &
```

Для мониторинга процесса пересылки логов проверьте статус сервиса Rsyslog:

```bash
sudo systemctl status rsyslog
```

Вы также можете наблюдать активность Rsyslog в реальном времени:

```bash
sudo journalctl -u rsyslog -f
```

Через несколько мгновений перейдите на дашборд Better Stack и откройте «Live tail». Вы должны увидеть логи вашего приложения logify, появляющиеся в реальном времени:

![Просмотр логов в реальном времени в Live Tail](/images/2903ffba3c137feda224be982e65e712.png)

Нажмите на любую запись лога, чтобы посмотреть её детальную информацию:

![Просмотр деталей записи лога](/images/31b44d8983e68d7791270c653203e35b.png)

## Заметка на полях: визуализируйте и исследуйте свои логи в Better Stack

Когда логи потекут, вы можете выйти за рамки поиска и использовать Better Stack для визуализации паттернов во времени.

## Заключение

В этом всеобъемлющем руководстве вы изучили функциональность и гибкость Rsyslog для эффективного управления логами. Вы начали с понимания того, как работает Rsyslog, затем перешли к его использованию для чтения логов из различных программ, преобразования данных логов в формат JSON и добавления пользовательских полей.

Наконец, вы настроили Rsyslog на пересылку логов в Better Stack.

С этой основой вы теперь хорошо подготовлены к интеграции Rsyslog в собственные проекты. Чтобы углубить понимание, обратитесь к [официальной документации Rsyslog](https://www.rsyslog.com/).

Хотя Rsyslog — мощный log shipper, доступно и несколько других инструментов. Чтобы сравнить альтернативы и выбрать правильное решение для ваших нужд, изучите наше [руководство по log shipper'ам](https://betterstack.com/community/guides/logging/log-shippers-explained/).

Спасибо и счастливого логирования!

**********

[rsyslog](/tags/rsyslog.md)
[syslog](/tags/syslog.md)
[logs](/tags/logs.md)