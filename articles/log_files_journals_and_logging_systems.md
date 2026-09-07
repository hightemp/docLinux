# Файлы журналов, джоналы и системы логирования

Источник: [Log Files, Journals, and Logging Systems](https://adamdjellouli.com/articles/linux_notes/log_files_and_journals)

Адам Джеллули (adamdjellouli.com) · обновлено 6 июня 2026

Понимание того, как работает логирование в Linux, похоже на изучение языка, на котором ваша система общается. Журналы (логи) — это подробные записи, которые система ведёт о своей деятельности, и они бесценны для устранения неисправностей, мониторинга производительности и обеспечения безопасности. Отправимся в путешествие, чтобы разобрать по полочкам файлы журналов, джоналы и различные системы логирования, используемые в Linux.

## Что такое журнал (лог)?

**Лог** — это запись событий, создаваемая операционной системой, приложением, службой, скриптом, устройством или компонентом безопасности.

Логи отвечают на вопросы вроде:

* Что произошло?
* Когда это произошло?
* Кто или что это вызвало?
* Это было нормально, подозрительно или сломано?
* Где искать дальше?

Типичная запись журнала содержит:

```text
+--------------------------------------------------------------------------------+
| TIMESTAMP           | SEVERITY | SOURCE / SERVICE | MESSAGE                    |
|---------------------|----------|------------------|----------------------------|
| 2026-05-03 09:00:01 | INFO     | nginx            | Server started             |
| 2026-05-03 09:01:10 | WARNING  | kernel           | CPU temperature high       |
| 2026-05-03 09:02:44 | ERROR    | myapp            | Database connection failed |
+--------------------------------------------------------------------------------+
```

### Важные части записи журнала

```text
May 03 09:02:44 web01 myapp[1234]: ERROR Database connection failed
│              │     │     │        │
│              │     │     │        └── Message
│              │     │     └────────── Process ID
│              │     └──────────────── Service / program name
│              └────────────────────── Hostname
└───────────────────────────────────── Timestamp
```

### Почему логи важны

Логи используются для:

| Цель | Пример
|---|---
| Устранение неисправностей | Почему nginx не запустился?
| Безопасность | Кто пытался подключиться по SSH к серверу?
| Аудит | Кто использовал sudo?
| Мониторинг | Заполняется ли дисковое пространство?
| Производительность | Почему приложение тормозит?
| Соответствие требованиям | Можем ли мы доказать, что попытки доступа фиксировались?

* Без логов вы не можете по-настоящему отлаживать — можете только гадать.
* С логами отладка превращается в расследование.

## Ландшафт логирования в Linux

В системах Linux обычно работает совместно больше одной системы логирования.

```text
                         +----------------------+
                         |      Applications    |
                         | Python, nginx, SSHD  |
                         +----------+-----------+
                                    |
                                    v
+-------------+           +---------+----------+          +----------------+
|   Kernel    |---------> | systemd-journald   | -------> | journalctl     |
|  hardware   |           | binary journal     |          | query journal  |
+-------------+           +---------+----------+          +----------------+
                                    |
                                    v
                         +----------+-----------+
                         | rsyslog / syslog     |
                         | text log routing     |
                         +----------+-----------+
                                    |
                                    v
                         +----------+-----------+
                         | /var/log/*.log       |
                         | plain text logs      |
                         +----------------------+
```

Современные системы Linux обычно используют:

| Система | Назначение
|---|---
| journald | Собирает структурированные логи от systemd, ядра, приложений
| journalctl | Читает и фильтрует логи journald
| rsyslog | Маршрутизирует логи в текстовые файлы или на удалённые лог-серверы
| /var/log | Каталог, где живут многие текстовые логи
| logrotate | Ротирует, сжимает и удаляет старые текстовые логи
| logger | Отправляет кастомные сообщения журнала из shell-скриптов
| dmesg | Читает сообщения кольцевого буфера ядра

## Распространённые расположения логов Linux

Большинство традиционных логов живёт в:

```text
/var/log
```

Пример:

```text
/var/log/
├── syslog
├── auth.log
├── kern.log
├── dmesg
├── boot.log
├── dpkg.log
├── apt/
│   ├── history.log
│   └── term.log
├── nginx/
│   ├── access.log
│   └── error.log
├── apache2/
│   ├── access.log
│   └── error.log
├── mysql/
├── postgresql/
├── journal/
└── rotated logs:
    ├── syslog.1
    ├── syslog.2.gz
    └── auth.log.1.gz
```

Разные дистрибутивы используют разные файлы.

Например:

```text
Debian / Ubuntu:
  /var/log/syslog
  /var/log/auth.log

RHEL / CentOS / Fedora:
  /var/log/messages
  /var/log/secure
```

## Текстовые логи

Текстовые логи — это обычные файлы, которые можно читать инструментами вроде:

* `cat`
* `less`
* `tail`
* `grep`
* `awk`
* `sed`

Пример:

```bash
sudo tail -n 50 /var/log/syslog
```

Примеры строк журнала:

```text
May 03 10:15:42 web01 NetworkManager[1234]: device eth0 state changed
May 03 10:15:45 web01 kernel: eth0: Link is Down
May 03 10:16:01 web01 CRON[2222]: (root) CMD (/usr/local/bin/backup.sh)
```

### Анатомия строки syslog

```text
May 03 10:16:01 web01 CRON[2222]: (root) CMD (/usr/local/bin/backup.sh)
│              │     │    │       │
│              │     │    │       └── Message
│              │     │    └────────── PID
│              │     └─────────────── Program
│              └──────────────────── Hostname
└─────────────────────────────────── Timestamp
```

## Journald и `journalctl`

Многие современные дистрибутивы Linux используют **systemd-journald**.

`journald` собирает логи из:

```text
+-------------------------+
|     systemd-journald    |
+-----------+-------------+

            |
+-----------+------------+----------------+----------------+----------------+
|                        |                |                |                |
| systemd services       | kernel         | applications   | stdout/stderr  |
| nginx.service          | hardware       | custom apps    | service logs   |
+------------------------+----------------+----------------+----------------+
```

В отличие от текстовых логов, systemd-джонал структурирован и обычно хранится в бинарном формате.

Обычно вы не читаете файл джонала напрямую.

Вы используете:

```text
journalctl
```

### Базовые команды `journalctl`

Просмотреть все логи:

```bash
journalctl
```

Эта команда отображает все логи, хранящиеся в systemd-джонале. Она показывает логи от системных служб, сообщения ядра, пользовательские сессии, активность загрузки и другие системные события. По умолчанию вывод показывается в пейджере, так что вы можете прокручивать его с помощью клавиатуры.

Пример вывода:

```text
May 03 09:15:01 server systemd[1]: Started Session 12 of User root.
May 03 09:15:05 server sshd[1245]: Accepted publickey for admin from 192.168.1.20
May 03 09:15:10 server sudo[1302]: admin : TTY=pts/0 ; COMMAND=/usr/bin/systemctl status nginx
```

Пояснение:

* Показывает все доступные записи джонала.
* Полезно для общей отладки.
* Может выдать большой объём вывода на активных системах.
* Нажмите `q` для выхода из просмотрщика логов.

Просмотреть новейшие логи:

```bash
journalctl -n 50
```

Эта команда показывает 50 новейших записей журнала. Полезно, когда вы хотите взглянуть только на самую последнюю активность системы, а не прокручивать весь джонал.

Пример вывода:

```text
May 03 10:01:22 server nginx[2210]: Configuration file /etc/nginx/nginx.conf test is successful
May 03 10:01:23 server systemd[1]: Reloaded nginx.service - A high performance web server
May 03 10:02:01 server CRON[2250]: pam_unix(cron:session): session opened for user root
```

Пояснение:

* `-n 50` ограничивает вывод последними 50 строками журнала.
* Полезно для проверки недавних ошибок или недавней активности служб.
* Вы можете заменить `50` на любое число, например `100` или `200`.

Следить за логами в реальном времени:

```bash
journalctl -f
```

Эта команда следит за логами в реальном времени. Новые записи появляются автоматически по мере записи в джонал. Работает аналогично `tail -f`.

Пример вывода:

```text
May 03 10:05:12 server sshd[2401]: Failed password for invalid user test from 203.0.113.10
May 03 10:05:15 server sshd[2401]: Connection closed by invalid user test 203.0.113.10
May 03 10:05:20 server nginx[2410]: 192.168.1.25 - - "GET / HTTP/1.1" 200
```

Пояснение:

* Показывает новые записи журнала по мере их появления.
* Полезно для отладки вживую.
* Часто используется при перезапуске службы или воспроизведении проблемы.
* Нажмите `Ctrl + C`, чтобы прекратить следование.

Просмотреть логи с момента загрузки:

```bash
journalctl -b
```

Эта команда показывает логи только текущей загрузки системы. Она отфильтровывает логи предыдущих загрузок и показывает, что происходило с момента последнего запуска машины.

Пример вывода:

```text
May 03 08:00:01 server kernel: Linux version 6.8.0
May 03 08:00:04 server systemd[1]: Starting system initialization...
May 03 08:00:15 server systemd[1]: Started ssh.service - OpenSSH server daemon
```

Пояснение:

* `-b` означает текущую загрузку.
* Полезно для расследования проблем запуска.
* Помогает отделить текущие проблемы от старых исторических логов.
* Часто используется после перезагрузки или сбоя.

Просмотреть предыдущую загрузку:

```bash
journalctl -b -1
```

Эта команда показывает логи предыдущей загрузки. Полезно, когда система упала, перезагрузилась неожиданно или имела проблему до текущего запуска.

Пример вывода:

```text
May 02 22:41:03 server kernel: Out of memory: Killed process 1884
May 02 22:41:10 server systemd[1]: nginx.service: Failed with result 'exit-code'
May 02 22:42:01 server systemd[1]: Reached target Reboot
```

Пояснение:

* `-b -1` означает одну загрузку до текущей.
* Полезно для проверки, почему система перезапустилась.
* Помогает разбирать сбои, неудачные выключения и циклы перезагрузки.
* `journalctl --list-boots` можно использовать для просмотра доступных записей загрузок.

Просмотреть логи за последний час:

```bash
journalctl --since "1 hour ago"
```

Эта команда отображает логи, сгенерированные за последний час. Помогает, когда проблема случилась недавно и вы не хотите искать по старым логам.

Пример вывода:

```text
May 03 09:12:44 server docker[1805]: Container web_app started
May 03 09:25:10 server nginx[1921]: connect() failed while connecting to upstream
May 03 09:58:31 server sshd[2150]: Accepted password for deploy from 192.168.1.30
```

Пояснение:

* `--since` фильтрует логи по времени начала.
* `"1 hour ago"` — относительное выражение времени.
* Полезно для недавнего устранения неисправностей.
* Другие примеры: `"10 minutes ago"` или `"yesterday"`.

Просмотреть логи за диапазон времени:

```bash
journalctl --since "2026-05-03 09:00" --until "2026-05-03 10:00"
```

Эта команда отображает логи между конкретным временем начала и конца. Полезно, когда вы точно знаете, когда возникла проблема, и хотите изучить только этот период.

Пример вывода:

```text
May 03 09:05:14 server nginx[1602]: 502 Bad Gateway while reading response header from upstream
May 03 09:20:44 server postgresql[1710]: checkpoint complete
May 03 09:45:02 server systemd[1]: Started cleanup temporary files
```

Пояснение:

* `--since` задаёт начало временного диапазона.
* `--until` задаёт конец временного диапазона.
* Полезно для расследования инцидентов.
* Формат времени должен быть ясным и единообразным, например `YYYY-MM-DD HH:MM`.

### Фильтрация по службе

```text
journalctl -u ssh.service
journalctl -u nginx.service
journalctl -u docker.service
journalctl -u postgresql.service
```

Эти команды отображают логи конкретных systemd-служб. Фильтрация по службе — один из самых распространённых способов использования `journalctl`, так как она убирает несвязанные системные сообщения и фокусируется только на службе, которую вы отлаживаете.

Пример вывода:

```text
May 03 10:12:01 server sshd[2501]: Server listening on 0.0.0.0 port 22
May 03 10:12:08 server sshd[2510]: Accepted publickey for admin from 192.168.1.20
May 03 10:12:10 server sshd[2510]: pam_unix(sshd:session): session opened for user admin
```

Пояснение:

* `-u` фильтрует логи по имени systemd-юнита.
* Имена служб обычно заканчиваются на `.service`.
* Полезно для отладки одной службы за раз.
* Распространённые примеры: `ssh.service`, `nginx.service`, `docker.service` и `postgresql.service`.

Следить за одной службой вживую:

```bash
journalctl -u nginx.service -f
```

Эта команда следит только за логами `nginx.service` в реальном времени. Полезно при тестировании изменений конфигурации, наблюдении за запросами или отладке живого поведения службы.

Пример вывода:

```text
May 03 10:20:01 server nginx[2701]: 192.168.1.50 - - "GET /api/status HTTP/1.1" 200
May 03 10:20:08 server nginx[2701]: 192.168.1.51 - - "POST /login HTTP/1.1" 302
May 03 10:20:12 server nginx[2701]: connect() failed while connecting to upstream
```

Пояснение:

* `-u nginx.service` фильтрует логи только по Nginx.
* `-f` следит за новыми записями вживую.
* Полезно во время reload'ов, рестартов и активного тестирования.
* Нажмите `Ctrl + C` для остановки.

Показать только недавние логи службы:

```bash
journalctl -u nginx.service -n 100
```

Эта команда отображает 100 самых недавних записей для `nginx.service`. Полезно, когда нужны недавние логи службы без следования вживую.

Пример вывода:

```text
May 03 10:30:05 server nginx[2801]: signal process started
May 03 10:30:06 server systemd[1]: Reloaded nginx.service - A high performance web server
May 03 10:31:10 server nginx[2801]: 192.168.1.70 - - "GET /health HTTP/1.1" 200
```

Пояснение:

* `-u nginx.service` ограничивает логи службой Nginx.
* `-n 100` показывает последние 100 записей.
* Полезно для быстрых проверок службы.
* Число можно увеличивать или уменьшать в зависимости от нужного объёма истории.

### Фильтрация по критичности

```bash
journalctl -p err
```

Показывает ошибки и всё более серьёзное.

Эта команда фильтрует логи по уровню приоритета. Уровень `err` показывает сообщения об ошибках и более серьёзные — критические, тревожные и аварийные логи. Полезно, когда нужно быстро найти серьёзные проблемы, не читая информационные логи.

Пример вывода:

```text
May 03 10:40:11 server nginx[3001]: connect() failed while connecting to upstream
May 03 10:41:03 server kernel: EXT4-fs error on device sda1
May 03 10:42:18 server systemd[1]: docker.service: Failed with result 'exit-code'
```

Пояснение:

* `-p err` показывает уровень приоритета `err` и всё более серьёзное.
* Полезно для быстрого поиска сбоев.
* Меньше шума, чем просмотр всех логов.
* Можно комбинировать с `-u` для фильтрации ошибок конкретной службы.

Уровни приоритета:

| Имя | Код | Значение
|---|---|---
| emerg | 0 | Система непригодна
| alert | 1 | Требуется немедленное действие
| crit | 2 | Критическое состояние
| err | 3 | Ошибка
| warning | 4 | Предупреждение
| notice | 5 | Нормально, но важно
| info | 6 | Информационное
| debug | 7 | Отладочные сообщения

Примеры:

```bash
journalctl -p warning
```

Эта команда показывает предупреждения и всё более серьёзное. Полезно, когда вы хотите увидеть потенциальные проблемы до того, как они станут ошибками.

Пример вывода:

```text
May 03 10:50:01 server nginx[3100]: conflicting server name ignored
May 03 10:51:22 server kernel: CPU temperature above threshold
May 03 10:52:05 server systemd[1]: service restart operation timed out
```

Пояснение:

* Показывает сообщения `warning`, `err`, `crit`, `alert` и `emerg`.
* Хорошо для проактивного устранения неисправностей.
* Подробнее, чем `-p err`.
* Может включать предупреждения, не ломающие службы.

```bash
journalctl -p err -u ssh.service
```

Эта команда показывает только логи уровня ошибки и выше для службы SSH. Полезно при отладке неудачных SSH-входов, сбоев службы SSH или проблем аутентификации.

Пример вывода:

```text
May 03 11:00:12 server sshd[3301]: error: kex_exchange_identification: client sent invalid protocol identifier
May 03 11:01:44 server sshd[3310]: fatal: Timeout before authentication
May 03 11:03:01 server sshd[3322]: error: PAM: Authentication failure for illegal user test
```

Пояснение:

* `-p err` фильтрует по критичности ошибки.
* `-u ssh.service` ограничивает логи SSH.
* Полезно для отладки аутентификации и соединений.
* Убирает шум обычных сообщений входа SSH.

```bash
journalctl -p debug -u myapp.service
```

Эта команда показывает логи уровня debug для `myapp.service`. Поскольку `debug` — самый низкий приоритет, сюда могут попадать очень детальные сообщения, в зависимости от того, как служба ведёт вывод.

Пример вывода:

```text
May 03 11:10:01 server myapp[3500]: DEBUG Loading configuration from /etc/myapp/config.yml
May 03 11:10:02 server myapp[3500]: DEBUG Database connection pool initialized
May 03 11:10:03 server myapp[3500]: INFO Application started successfully
```

Пояснение:

* `-p debug` включает debug-логи и все более приоритетные сообщения.
* Полезно при разработке или глубокой отладке.
* Может дать очень многословный вывод.
* Лучше комбинировать с `-u`, чтобы избежать лишнего вывода.

### Форматы вывода джонала

Обычный вывод:

```bash
journalctl -u nginx
```

Эта команда показывает логи службы Nginx в формате вывода джонала по умолчанию. Формат по умолчанию читабелен и подходит для большинства задач ручной отладки.

Пример вывода:

```text
May 03 11:20:01 server nginx[3700]: 192.168.1.80 - - "GET / HTTP/1.1" 200
May 03 11:20:05 server nginx[3700]: 192.168.1.81 - - "GET /favicon.ico HTTP/1.1" 404
May 03 11:20:10 server systemd[1]: Reloaded nginx.service - A high performance web server
```

Пояснение:

* Отображает логи службы в стандартном человекочитаемом формате.
* Хорошо для повседневной отладки.
* Показывает метку времени, имя хоста, имя процесса, ID процесса и сообщение.
* Легко читать прямо в терминале.

Короткие ISO-метки времени:

```bash
journalctl -u nginx -o short-iso
```

Эта команда показывает логи Nginx с метками времени в стиле ISO. Формат полезен, когда нужны более ясные метки времени, особенно для сравнения логов между системами или сопоставления с внешними средствами мониторинга.

Пример вывода:

```text
2026-05-03T11:25:01+0200 server nginx[3800]: 192.168.1.90 - - "GET / HTTP/1.1" 200
2026-05-03T11:25:03+0200 server nginx[3800]: 192.168.1.91 - - "POST /api/login HTTP/1.1" 401
2026-05-03T11:25:08+0200 server nginx[3800]: upstream timed out while reading response header
```

Пояснение:

* `-o short-iso` меняет формат вывода.
* Метки времени в стиле ISO.
* Полезно для корреляции логов.
* Легче сортировать, сравнивать и копировать в отчёты.

Подробные метаданные:

```bash
journalctl -u nginx -o verbose
```

Эта команда показывает детальные метаданные каждой записи джонала. Включает поля вроде имени systemd-юнита, ID процесса, пути исполняемого файла, имени хоста, приоритета и других внутренних полей джонала.

Пример вывода:

```text
MESSAGE=192.168.1.90 - - "GET / HTTP/1.1" 200
_PID=3800
_UID=33
_GID=33
_SYSTEMD_UNIT=nginx.service
_COMM=nginx
_HOSTNAME=server
PRIORITY=6
```

Пояснение:

* `-o verbose` показывает детальные поля джонала.
* Полезно для продвинутой отладки.
* Помогает определить точные процессы, юниты, пользователей и приоритеты.
* Подробнее обычного вывода и менее удобно для быстрого чтения.

JSON-вывод:

```bash
journalctl -u nginx -o json
```

Эта команда выводит каждую запись джонала как единый JSON-объект. Полезно, когда логи должны обрабатываться скриптами, инструментами командной строки или системами агрегации логов.

Пример вывода:

```text
{"MESSAGE":"192.168.1.90 - - \"GET / HTTP/1.1\" 200","_PID":"3800","_SYSTEMD_UNIT":"nginx.service","PRIORITY":"6","_HOSTNAME":"server"}
{"MESSAGE":"upstream timed out while reading response header","_PID":"3800","_SYSTEMD_UNIT":"nginx.service","PRIORITY":"3","_HOSTNAME":"server"}
```

Пояснение:

* `-o json` печатает логи как JSON.
* Каждая запись — на одной строке.
* Полезно для парсинга инструментами вроде `jq`.
* Хорошо для автоматизации, скриптов и лог-конвейеров.

Красивый JSON:

```bash
journalctl -u nginx -o json-pretty
```

Эта команда выводит записи джонала как форматированный JSON. Людям читать его легче, чем обычный JSON, потому что поля разбиты по строкам с отступами.

Пример вывода:

```text
{
  "MESSAGE" : "192.168.1.90 - - \"GET / HTTP/1.1\" 200",
  "_PID" : "3800",
  "_SYSTEMD_UNIT" : "nginx.service",
  "PRIORITY" : "6",
  "_HOSTNAME" : "server"
}
```

Пояснение:

* `-o json-pretty` форматирует JSON по нескольким строкам.
* Легче инспектировать вручную, чем компактный JSON.
* Полезно при просмотре записей, богатых метаданными.
* Менее удобно для построчной обработки логов, чем `-o json`.

Это полезно при передаче логов в скрипты или системы агрегации. JSON-форматы позволяют инструментам читать поля вроде имени службы, приоритета, ID процесса, имени хоста и сообщения без текстового парсинга. Для быстрой ручной отладки обычный или short-вывод обычно легче читать. Для автоматизации и структурированных лог-процессов JSON-вывод обычно лучше.

## Логи Linux по слоям системы

Полезный способ понять логи — по слоям.

| Слой | Компоненты
|---|---
| Слой приложений | Python-приложения, nginx, Apache, PostgreSQL, Docker-приложения
| Слой служб | systemd-службы, cron, SSH, NetworkManager
| Слой ОС | менеджер пакетов, sudo, auth, syslog
| Слой ядра | драйверы, железо, память, диск, CPU, сеть
| Слой загрузки | загрузчик, initramfs, запуск systemd

### Логи ядра

Логи ядра полезны для отладки:

* железа
* драйверов
* сетевых интерфейсов
* USB-устройств
* дисков
* ошибок памяти
* предупреждений CPU
* проблем файловых систем

Логи ядра исходят от ядра Linux, а не от обычных приложений userspace. Они особенно полезны при устранении низкоуровневых системных проблем: сбоящего диска, отключения сетевой карты, необнаружения USB-устройства, падения драйвера или сообщений системы о предупреждениях CPU или памяти.

Команды:

```bash
dmesg
```

Эта команда показывает сообщения из кольцевого буфера ядра. Обычно включают сообщения загрузки, обнаружение устройств, сообщения драйверов, предупреждения железа и ошибки уровня ядра.

Пример вывода:

```text
[    0.000000] Linux version 6.8.0-31-generic
[    1.245011] usb 1-1: new high-speed USB device number 2 using xhci_hcd
[    2.884310] eth0: renamed from enp0s3
[   15.902144] EXT4-fs (sda1): mounted filesystem
```

Пояснение:

* Показывает сообщения ядра, хранящиеся в кольцевом буфере ядра.
* Полезно для проверки событий железа и драйверов.
* Метки времени — секунды с момента загрузки.
* Вывод может очищаться после перезагрузки или перезаписываться на загруженных системах.

```bash
dmesg -T
```

Эта команда показывает сообщения ядра с человекочитаемыми метками времени. Вместо секунд с загрузки она преобразует метки в обычный формат даты и времени.

Пример вывода:

```text
[Sun May  3 09:01:10 2026] Linux version 6.8.0-31-generic
[Sun May  3 09:01:12 2026] usb 1-1: new high-speed USB device number 2 using xhci_hcd
[Sun May  3 09:01:15 2026] eth0: renamed from enp0s3
[Sun May  3 09:02:01 2026] EXT4-fs (sda1): mounted filesystem
```

Пояснение:

* `-T` показывает читаемые метки времени.
* Легче сопоставлять события ядра с инцидентами.
* Полезно при проверке, когда устройство отключилось или произошла ошибка.
* Преобразование меток может быть менее точным, если системные часы менялись после загрузки.

```bash
journalctl -k
```

Эта команда показывает сообщения ядра из systemd-джонала. Похожа на `dmesg`, но читает логи ядра из джонала, а не только из кольцевого буфера ядра.

Пример вывода:

```text
May 03 09:01:10 server kernel: Linux version 6.8.0-31-generic
May 03 09:01:12 server kernel: usb 1-1: new high-speed USB device number 2 using xhci_hcd
May 03 09:01:15 server kernel: eth0: renamed from enp0s3
May 03 09:02:01 server kernel: EXT4-fs (sda1): mounted filesystem
```

Пояснение:

* `-k` показывает сообщения ядра из джонала.
* Использует обычные метки времени джонала.
* Может включать сохранённые логи ядра предыдущих загрузок, если включена персистентность джонала.
* Полезно, когда нужны логи ядра с опциями фильтрации `journalctl`.

```bash
journalctl -k -b
```

Эта команда показывает сообщения ядра только текущей загрузки. Полезно при отладке проблем железа, драйверов или загрузки в текущей сессии.

Пример вывода:

```text
May 03 09:01:10 server kernel: Linux version 6.8.0-31-generic
May 03 09:01:13 server kernel: ACPI: bus type USB registered
May 03 09:01:18 server kernel: e1000e 0000:00:19.0 eth0: NIC Link is Up
May 03 09:04:44 server kernel: EXT4-fs (sda1): re-mounted filesystem
```

Пояснение:

* `-k` фильтрует записи джонала по сообщенияам ядра.
* `-b` ограничивает вывод текущей загрузкой.
* Полезно для проверки запуска и инициализации железа.
* Помогает не смешивать текущие сообщения ядра со старыми логами загрузок.

Примеры:

```bash
dmesg | grep -i error
```

Эта команда ищет в сообщениях ядра слово `error` без учёта регистра. Полезно для быстрого поиска сбоев уровня ядра.

Пример вывода:

```text
[ 1234.442100] EXT4-fs error (device sda1): ext4_find_entry: inode read error
[ 1240.112901] blk_update_request: I/O error, dev sda, sector 884120
[ 1244.650331] usb 2-1: device descriptor read/64, error -71
```

Пояснение:

* `grep -i error` ищет `error`, `Error` или `ERROR`.
* Полезно для поиска ошибок диска, USB, файловой системы и драйверов.
* Может пропустить проблемы, описанные словами `failed`, `timeout` или `reset`.
* Для более широкого поиска проверяйте также `fail`, `warn` и `timeout`.

```bash
dmesg | grep -i usb
```

Эта команда фильтрует сообщения ядра, связанные с USB-устройствами. Полезно проверять, корректно ли обнаружен USB-диск, клавиатура, сетевой адаптер или другое USB-устройство.

Пример вывода:

```text
[    1.245011] usb 1-1: new high-speed USB device number 2 using xhci_hcd
[    1.601233] usb 1-1: New USB device found, idVendor=0781, idProduct=5567
[    1.604811] usb-storage 1-1:1.0: USB Mass Storage device detected
```

Пояснение:

* Показывает обнаружение USB и сообщения драйверов.
* Полезно, когда USB-устройство не появляется.
* Может показать сбросы устройств, отключения и ошибки дескрипторов.
* Помогает при отладке внешних дисков и USB-адаптеров.

```bash
dmesg | grep -i eth
```

Эта команда ищет в сообщениях ядра записи, связанные с Ethernet. Полезно при проверке обнаружения сетевых интерфейсов, изменений состояния линка и сообщений сетевых драйверов.

Пример вывода:

```text
[    2.884310] eth0: renamed from enp0s3
[   45.812001] e1000e 0000:00:19.0 eth0: NIC Link is Up 1000 Mbps Full Duplex
[  300.441221] eth0: Link is Down
```

Пояснение:

* Ищет сообщения, содержащие `eth`.
* Полезно для отладки Ethernet-интерфейсов.
* Может показать, поднят ли сетевой линк или опущен.
* В некоторых системах используются имена вроде `enp0s3`, `ens160` или `eno1` вместо `eth0`.

```bash
journalctl -k -p warning
```

Эта команда показывает предупреждения ядра и всё более серьёзное. Полезно, когда нужно сфокусироваться на проблемах ядра, не читая обычные информационные сообщения.

Пример вывода:

```text
May 03 10:12:44 server kernel: CPU0: Core temperature above threshold
May 03 10:13:02 server kernel: blk_update_request: I/O error, dev sda, sector 884120
May 03 10:13:10 server kernel: EXT4-fs warning (device sda1): mounting fs with errors
```

Пояснение:

* `-k` фильтрует логи по сообщенияам ядра.
* `-p warning` показывает предупреждения, ошибки, критические, тревожные и аварийные сообщения.
* Полезно для быстрого поиска серьёзных проблем железа или ядра.
* Можно комбинировать с `-b`, чтобы показать предупреждения только текущей загрузки.

Пример лога ядра:

```text
[12345.678901] eth0: Link is Down
[12346.123456] EXT4-fs error: I/O error while writing superblock
[12347.222222] CPU0: Core temperature above threshold
```

Этот пример показывает три разные проблемы уровня ядра. Первая строка указывает на проблему линка сетевого интерфейса, вторая — на проблему записи в файловую систему или диск, третья — на предупреждение о температуре CPU.

Интерпретация:

```text
eth0 Link is Down        → network interface disconnected
EXT4-fs error            → filesystem or disk issue
temperature threshold    → cooling or hardware problem
```

Пояснение:

* `eth0 Link is Down` обычно означает, что сетевой кабель выдернут, виртуальный интерфейс отключился или порт коммутатора погас.
* `EXT4-fs error` обычно указывает на повреждение файловой системы, ошибки дискового ввода-вывода, проблемы хранения или небезопасное выключение.
* `I/O error while writing superblock` серьёзно, потому что суперблок содержит важные метаданные файловой системы.
* `CPU temperature above threshold` означает, что CPU перегревается и может сбрасывать производительность или выключаться для защиты железа.
* Повторяющиеся сообщения о диске, файловой системе или температуре нужно расследовать немедленно.

### Логи аутентификации

Логи аутентификации записывают:

* попытки входа по SSH
* использование sudo
* неверные пароли
* пользовательские сессии
* PAM-аутентификацию

Ubuntu/Debian:

```bash
sudo less /var/log/auth.log
```

Системы на базе RHEL:

```bash
sudo less /var/log/secure
```

Через journald:

```text
journalctl -u ssh.service
journalctl _COMM=sshd
```

Распространённые поиски:

```text
sudo grep "Failed password" /var/log/auth.log
sudo grep "Accepted password" /var/log/auth.log
sudo grep "sudo" /var/log/auth.log
sudo grep "session opened" /var/log/auth.log
```

Пример:

```text
May 03 11:00:01 server sshd[23456]: Failed password for invalid user admin from 203.0.113.10 port 54323 ssh2
```

Разбор:

```text
Failed password       → login failed
invalid user admin    → account does not exist
203.0.113.10          → source IP
sshd                  → SSH daemon
```

### Логи systemd-служб

Большинство служб, управляемых systemd, можно отлаживать так:

```text
systemctl status service-name
journalctl -u service-name
```

Пример:

```text
systemctl status nginx
journalctl -u nginx
journalctl -u nginx -f
```

Полезный паттерн:

```bash
sudo systemctl restart nginx
journalctl -u nginx -n 50 --no-pager
```

Это позволяет перезапустить службу и сразу посмотреть самые свежие логи.

### Логи cron

Cron логирует запланированные задания.

В зависимости от дистрибутива логи cron могут быть в:

```text
/var/log/syslog
/var/log/cron
journalctl -u cron
journalctl -u crond
```

Примеры:

```text
grep CRON /var/log/syslog
journalctl -u cron
```

Пример:

```text
May 03 12:00:01 server CRON[4567]: (root) CMD (/usr/local/bin/backup.sh)
```

Это значит, что cron запустил скрипт.

Это **не** гарантирует, что скрипт succeeded.

Для правильной отладки скрипта сам скрипт должен логировать успех и неудачу.

### Логи менеджеров пакетов

Полезно при вопросах:

```text
What changed recently?
Was a package upgraded?
Did an update break something?
```

Debian/Ubuntu:

```text
less /var/log/dpkg.log
less /var/log/apt/history.log
less /var/log/apt/term.log
```

Примеры:

```text
grep "install " /var/log/dpkg.log
grep "upgrade " /var/log/dpkg.log
grep nginx /var/log/apt/history.log
```

RHEL/Fedora:

```text
less /var/log/dnf.log
less /var/log/yum.log
rpm -qa --last
```

### Логи веб-серверов

#### Nginx

Распространённые файлы:

```text
/var/log/nginx/access.log
/var/log/nginx/error.log
```

Пример access-лога:

```text
192.168.1.50 - - [03/May/2026:13:00:01 +0200] "GET /index.html HTTP/1.1" 200 612
```

Значение:

```text
192.168.1.50    → client IP
GET /index.html → requested path
200             → HTTP status code
612             → bytes sent
```

Пример error-лога:

```text
2026/05/03 13:01:22 [error] 1234#1234: *55 connect() failed while connecting to upstream
```

Это часто значит, что nginx не может достучаться до бэкенд-приложения.

Полезные команды:

```text
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
sudo grep " 500 " /var/log/nginx/access.log
sudo grep "connect() failed" /var/log/nginx/error.log
```

#### Apache

Распространённые файлы:

```text
/var/log/apache2/access.log
/var/log/apache2/error.log
```

или:

```text
/var/log/httpd/access_log
/var/log/httpd/error_log
```

### Логи баз данных

Логи PostgreSQL могут быть в:

```text
/var/log/postgresql/
journalctl -u postgresql
```

Логи MySQL/MariaDB могут быть в:

```text
/var/log/mysql/
journalctl -u mysql
journalctl -u mariadb
```

Распространённые поиски:

```text
grep -i error /var/log/postgresql/*.log
grep -i "connection refused" /var/log/mysql/error.log
journalctl -u postgresql -p err
```

### Логи Docker

У Docker свой путь логирования.

Просмотр логов контейнера:

```text
docker logs container_name
docker logs -f container_name
docker logs --tail 100 container_name
docker logs --since 1h container_name
```

Логи службы Docker:

```text
journalctl -u docker
```

Логи Docker Compose:

```text
docker compose logs
docker compose logs -f
docker compose logs api
docker compose logs --tail 100
```

Типичный порядок отладки Docker:

```text
docker ps
docker ps -a
docker logs container_name
docker inspect container_name
journalctl -u docker
```

## Создание логов из Python-приложений

Python-приложения не должны полагаться только на `print()`.

Используйте встроенный модуль `logging`.

### Базовое логирование в Python

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger("myapp")

logger.info("Application started")
logger.warning("Disk space is getting low")
logger.error("Database connection failed")
```

Пример вывода:

```text
2026-05-03 14:00:01 INFO myapp: Application started
2026-05-03 14:00:02 WARNING myapp: Disk space is getting low
2026-05-03 14:00:03 ERROR myapp: Database connection failed
```

### Логирование в файл

```python
import logging

logging.basicConfig(
    filename="/var/log/myapp.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(process)d]: %(message)s"
)

logger = logging.getLogger("myapp")

logger.info("Server started")
logger.error("Could not connect to database")
```

Важно:

```text
The application user must have permission to write to the log file.
```

Пример:

```bash
sudo touch /var/log/myapp.log
sudo chown myappuser:myappuser /var/log/myapp.log
```

### Логирование в консоль для systemd

Если ваше Python-приложение работает как systemd-служба, логирование в stdout/stderr часто лучше всего.

Python-приложение:

```python
import logging
import sys

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("Application started")
logger.error("Something failed")
```

Systemd-служба:

```text
[Unit]
Description=My Python App
After=network.target

[Service]
User=myappuser
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python3 /opt/myapp/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Просмотр логов:

```text
journalctl -u myapp.service
journalctl -u myapp.service -f
```

Поток:

```text
Python stdout/stderr
        |
        v
systemd service manager
        |
        v
systemd-journald
        |
        v
journalctl -u myapp.service
```

### Ротация логов в Python

Для автономных приложений можно ротировать логи изнутри Python.

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "/var/log/myapp.log",
    maxBytes=5_000_000,
    backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("App started")
logger.warning("Something looks suspicious")
logger.error("Something failed")
```

Это создаёт файлы вроде:

```text
/var/log/myapp.log
/var/log/myapp.log.1
/var/log/myapp.log.2
/var/log/myapp.log.3
```

Используйте это, когда приложение владеет своими логами.

Используйте `logrotate`, когда Linux должен управлять файлами логов извне.

### Логи с ротацией по времени в Python

Ротировать каждый день:

```python
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    "/var/log/myapp.log",
    when="midnight",
    interval=1,
    backupCount=14
)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Daily rotating logger started")
```

Результат:

```text
myapp.log
myapp.log.2026-05-01
myapp.log.2026-05-02
myapp.log.2026-05-03
```

### JSON-логи в Python

JSON-логи проще парсить машинам.

```python
import logging
import json
import sys
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "process": record.process,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

logger.info("Application started")
```

Пример вывода:

```text
{
  "timestamp": "2026-05-03T12:00:01+00:00",
  "level": "INFO",
  "logger": "myapp",
  "message": "Application started",
  "module": "app",
  "line": 31,
  "process": 1234
}
```

JSON-логи хороши для:

```text
Loki
Elasticsearch
OpenSearch
Splunk
Fluent Bit
Vector
Logstash
custom Python parsers
```

### Правильное логирование исключений в Python

Плохо:

```python
try:
    1 / 0
except Exception as e:
    logger.error(f"Error: {e}")
```

Лучше:

```python
try:
    1 / 0
except Exception:
    logger.exception("Unexpected calculation error")
```

`logger.exception()` включает traceback.

Пример:

```text
ERROR myapp: Unexpected calculation error
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    1 / 0
ZeroDivisionError: division by zero
```

Traceback'и крайне важны для отладки.

### Логирование Python-приложения в syslog

Можно отправлять Python-логи в syslog.

```python
import logging
from logging.handlers import SysLogHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = SysLogHandler(address="/dev/log")
formatter = logging.Formatter("myapp: %(levelname)s %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("Application started")
logger.error("Database connection failed")
```

Затем проверьте:

```text
journalctl | grep myapp
grep myapp /var/log/syslog
```

## Создание логов из shell-скриптов

### Использование `logger`

Команда `logger` отправляет сообщения в syslog/journald.

Простой пример:

```bash
logger "Backup completed successfully"
```

С тегом:

```bash
logger -t backup_script "Backup completed successfully"
```

С критичностью:

```text
logger -t backup_script -p local0.info "Backup started"
logger -t backup_script -p local0.err "Backup failed"
```

Пример скрипта:

```bash
#!/bin/bash

SOURCE="/data"
DEST="/backup"

logger -t backup_script -p local0.info "Backup started"

if rsync -a "$SOURCE" "$DEST"; then
    logger -t backup_script -p local0.info "Backup completed successfully"
else
    logger -t backup_script -p local0.err "Backup failed"
    exit 1
fi
```

Просмотр логов:

```text
journalctl -t backup_script
grep backup_script /var/log/syslog
```

## Rsyslog

`rsyslog` — мощный syslog-демон, используемый для:

* приёма логов
* фильтрации логов
* записи логов в файлы
* пересылки логов на удалённые серверы
* разделения логов по facility/критичности/программе

Базовый поток:

```text
Application / Kernel / Service
            |
            v
        journald
            |
            v
        rsyslog
            |
     +------+------+
     |             |
     v             v
 /var/log/syslog   Remote log server
```

### Формат правил rsyslog

Классический формат:

```text
facility.priority    action
```

Пример:

```text
authpriv.*           /var/log/auth.log
kern.*               /var/log/kern.log
mail.info            /var/log/mail.info
*.err                /var/log/errors.log
```

Facility:

| Facility | Значение
|---|---
| auth | Аутентификация
| authpriv | Приватные сообщения аутентификации
| cron | Задания cron
| daemon | Системные демоны
| kern | Сообщения ядра
| mail | Почтовая система
| syslog | Внутренние сообщения syslog
| user | Сообщения уровня пользователя
| local0-7 | Кастомное использование

Приоритеты:

```text
debug < info < notice < warning < err < crit < alert < emerg
```

### Кастомное правило rsyslog

Создайте:

```bash
sudo nano /etc/rsyslog.d/30-myapp.conf
```

Пример:

```text
if $programname == 'myapp' then /var/log/myapp.log
& stop
```

Перезапустите rsyslog:

```bash
sudo systemctl restart rsyslog
```

Проверьте:

```text
logger -t myapp "Hello from myapp"
cat /var/log/myapp.log
```

### Удалённое логирование с rsyslog

#### Сервер

Включите TCP-приёмник:

```text
module(load="imtcp")
input(type="imtcp" port="514")
```

Храните логи по имени хоста:

```text
template(name="RemoteLogs" type="string" string="/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log")
*.* ?RemoteLogs
```

Перезапуск:

```bash
sudo systemctl restart rsyslog
```

#### Клиент

Отправка логов на сервер:

```text
*.* @@logserver.example.com:514
```

`@` означает UDP.

`@@` означает TCP.

Перезапуск:

```bash
sudo systemctl restart rsyslog
```

Архитектура:

```text
+-----------+       TCP 514       +----------------+
| server01  | ------------------> | logserver      |
| server02  | ------------------> | /var/log/remote|
| server03  | ------------------> |                |
+-----------+                     +----------------+
```

## Наведение порядка в логах

Логи растут бесконечно, если ими не управлять.

Наведение порядка (housekeeping) означает:

* ротацию старых логов
* сжатие старых логов
* удаление просроченных логов
* ограничение использования диска
* вакуумирование файлов джонала
* архивирование важных логов

Есть две основные системы наведения порядка:

| Система | Управляет
|---|---
| logrotate | Текстовые логи в /var/log
| конфигурация journald | Размер и хранение systemd-джонала

### Logrotate

`logrotate` управляет традиционными файлами логов.

Расположения конфигурации:

```text
/etc/logrotate.conf
/etc/logrotate.d/
```

Просмотр конфигов:

```text
cat /etc/logrotate.conf
ls /etc/logrotate.d/
cat /etc/logrotate.d/nginx
cat /etc/logrotate.d/rsyslog
```

Пример конфигурации:

```text
/var/log/myapp.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 myappuser adm
    postrotate
        systemctl reload myapp.service > /dev/null 2>&1 || true
    endscript
}
```

Значение:

```text
daily          rotate every day
rotate 14      keep 14 old logs
compress       gzip old logs
delaycompress  wait one cycle before compression
missingok      do not error if file is missing
notifempty     do not rotate empty logs
create         create a new file with permissions/owner/group
postrotate     run command after rotation
```

### Проверка состояния logrotate

Файл состояния logrotate:

```text
cat /var/lib/logrotate/status
```

Отладка logrotate без изменения файлов:

```bash
sudo logrotate -d /etc/logrotate.conf
```

Принудительная ротация:

```bash
sudo logrotate -f /etc/logrotate.conf
```

Принудительная ротация одного конфига:

```bash
sudo logrotate -f /etc/logrotate.d/nginx
```

Проверка ротированных файлов:

```text
ls -lh /var/log/syslog*
ls -lh /var/log/nginx/*
```

Пример:

```text
/var/log/syslog
/var/log/syslog.1
/var/log/syslog.2.gz
/var/log/syslog.3.gz
```

### Как logrotate запускается автоматически

Во многих системах logrotate запускается systemd-таймером:

```text
systemctl status logrotate.timer
systemctl list-timers | grep logrotate
```

Или через cron:

```text
ls /etc/cron.daily/
cat /etc/cron.daily/logrotate
```

Полезная проверка:

```text
systemctl status logrotate.service
journalctl -u logrotate.service
```

### Наведение порядка в journald

Проверка использования диска джоналом:

```bash
journalctl --disk-usage
```

Вакуумирование старых логов джонала по размеру:

```bash
sudo journalctl --vacuum-size=1G
```

Вакуумирование по времени:

```bash
sudo journalctl --vacuum-time=14d
```

Вакуумирование по числу файлов:

```bash
sudo journalctl --vacuum-files=10
```

Файл конфигурации:

```text
/etc/systemd/journald.conf
```

Распространённые настройки:

```text
[Journal]
Storage=persistent
SystemMaxUse=1G
SystemKeepFree=2G
MaxRetentionSec=1month
Compress=yes
```

Перезапустите journald после изменений:

```bash
sudo systemctl restart systemd-journald
```

### Персистентный и волатильный джоналы

Волатильный джонал:

```text
/run/log/journal
```

Теряется после перезагрузки.

Персистентный джонал:

```text
/var/log/journal
```

Выживает после перезагрузки.

Включение персистентного джонала:

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

Проверка:

```text
ls -ld /var/log/journal
journalctl --list-boots
```

## Быстрый поиск и парсинг логов

Именно здесь происходит практическая отладка.

### Базовые инструменты

| Инструмент | Использование
|---|---
| less | Интерактивное чтение больших файлов
| tail | Показ последних строк / следование за логами вживую
| grep | Поиск текста
| awk | Извлечение колонок / суммирование
| sed | Преобразование/фильтрация текста
| cut | Извлечение полей
| sort | Сортировка результатов
| uniq | Подсчёт повторяющихся строк
| wc | Подсчёт строк
| jq | Парсинг JSON-логов
| journalctl | Запросы к systemd-джоналу
| zgrep | Поиск по сжатым .gz-логам
| lnav | Интерактивный просмотрщик логов

### Быстрые примеры

Следить за файлом вживую:

```bash
tail -f /var/log/syslog
```

Следить за несколькими файлами:

```bash
tail -f /var/log/syslog /var/log/auth.log
```

Поиск ошибок:

```bash
grep -i error /var/log/syslog
```

Поиск по сжатым ротированным логам:

```bash
zgrep -i error /var/log/syslog.*.gz
```

Поиск по текущим и ротированным логам:

```text
grep -i error /var/log/syslog /var/log/syslog.1
zgrep -i error /var/log/syslog.*.gz
```

Подсчёт неудачных SSH-попыток по IP:

```bash
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr
```

Топ запрашиваемых URL в access-логе nginx:

```bash
awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head
```

Топ HTTP-кодов состояния:

```bash
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -nr
```

Поиск ошибок 500:

```bash
awk '$9 >= 500 {print}' /var/log/nginx/access.log
```

### Быстрая фильтрация с помощью `journalctl`

Ошибки текущей загрузки:

```bash
journalctl -b -p err
```

Предупреждения и ошибки nginx:

```bash
journalctl -u nginx -p warning
```

Логи за последние 10 минут:

```bash
journalctl --since "10 minutes ago"
```

Логи одного исполняемого файла:

```text
journalctl _COMM=sshd
```

Логи одного PID:

```text
journalctl _PID=1234
```

Логи ядра текущей загрузки:

```bash
journalctl -k -b
```

Логи без пейджера:

```bash
journalctl -u nginx --no-pager
```

### Парсинг JSON-логов с `jq`

Пример JSON-лога:

```text
{"timestamp":"2026-05-03T12:00:00Z","level":"ERROR","service":"api","message":"database timeout"}
```

Показать только ошибки:

```bash
jq 'select(.level == "ERROR")' app.log
```

Вывести метку времени и сообщение:

```bash
jq -r 'select(.level == "ERROR") | "\(.timestamp) \(.message)"' app.log
```

Подсчёт по уровням:

```bash
jq -r '.level' app.log | sort | uniq -c
```

### `lnav`

`lnav` — интерактивный просмотрщик логов, понимающий множество форматов логов.

Установка:

```bash
sudo apt install lnav
```

Открыть логи:

```bash
sudo lnav /var/log/syslog /var/log/auth.log
```

Открыть все логи nginx:

```bash
sudo lnav /var/log/nginx/*.log
```

Преимущества:

* цветные логи
* автоматическое определение меток времени
* поиск
* фильтрация
* SQL-подобные запросы
* несколько файлов вместе

### Сбор логов воедино

Для отладки часто полезно собрать логи в один пакет.

Пример:

```bash
mkdir -p debug-logs

journalctl -b > debug-logs/journal-current-boot.log
journalctl -p err > debug-logs/journal-errors.log
dmesg -T > debug-logs/dmesg.log
systemctl status nginx > debug-logs/nginx-status.txt
journalctl -u nginx > debug-logs/nginx-journal.log
cp /var/log/nginx/error.log debug-logs/

tar -czf debug-logs.tar.gz debug-logs
```

Результат:

```text
debug-logs.tar.gz
```

Можно отправить это другому админу или приложить к баг-репорту.

## Централизованный сбор логов

Для одного сервера локальных логов может быть достаточно.

Для многих серверов лучше централизованное логирование.

```text
+-----------+       +-----------+
| app01     |       | app02     |
+-----+-----+       +-----+-----+
      |                   |
      v                   v
+-------------------------------+
|      Log Collector            |
| rsyslog / Fluent Bit / Vector |
+---------------+---------------+
                |
                v
+-------------------------------+
| Storage / Search              |
| Loki / Elasticsearch / Splunk |
+-------------------------------+
                |
                v
+-------------------------------+
| Dashboard / Alerts            |
| Grafana / Kibana / SIEM       |
+-------------------------------+
```

Распространённые инструменты:

| Инструмент | Назначение
|---|---
| rsyslog | Классическая пересылка и маршрутизация syslog
| syslog-ng | Альтернативный syslog-демон
| Fluent Bit | Легковесный сборщик/пересыльщик логов
| Fluentd | Более тяжёлый сборщик/обработчик логов
| Vector | Быстрый конвейер логов/событий
| Logstash | Конвейер обработки для Elastic/OpenSearch
| Filebeat | Пересылка файлов логов в Elastic/OpenSearch
| Promtail | Пересылка логов в Loki
| Loki | Система хранения/запросов логов от экосистемы Grafana
| Elasticsearch | Поисковое/индексирующее хранилище логов
| OpenSearch | Опенсорсная альтернатива Elasticsearch
| Splunk | Коммерческая платформа аналитики логов
| Grafana | Дашборды для логов и метрик
| Kibana | UI визуализации Elasticsearch

## Отладка с логами: практические сценарии

### Служба не запускается

Пример: nginx падает.

Шаг 1:

```bash
systemctl status nginx
```

Шаг 2:

```bash
journalctl -u nginx -n 100 --no-pager
```

Шаг 3:

```bash
sudo nginx -t
```

Шаг 4:

```bash
sudo tail -n 100 /var/log/nginx/error.log
```

Поток:

```text
Service failed
     |
     v
systemctl status
     |
     v
journalctl -u service
     |
     v
application-specific config test
     |
     v
application-specific error log
```

### Проблемы со входом по SSH

Проверка службы SSH:

```text
systemctl status ssh
journalctl -u ssh
```

Проверка логов аутентификации:

```bash
sudo tail -f /var/log/auth.log
```

Поиск неудач:

```bash
sudo grep "Failed password" /var/log/auth.log
```

Поиск успешных входов:

```bash
sudo grep "Accepted" /var/log/auth.log
```

Распространённые причины:

* неверный пароль
* неверное имя пользователя
* проблема прав SSH-ключа
* блокировка порта файрволом
* отключён PermitRootLogin
* отключён PasswordAuthentication
* fail2ban блокирует IP

### Диск заполнен из-за логов

Проверка диска:

```bash
df -h
```

Поиск крупнейших каталогов логов:

```bash
sudo du -sh /var/log/* | sort -h
```

Поиск огромных файлов логов:

```bash
sudo find /var/log -type f -size +100M -exec ls -lh {} \;
```

Проверка размера джонала:

```bash
journalctl --disk-usage
```

Безопасная очистка джонала:

```bash
sudo journalctl --vacuum-size=1G
```

Принудительный logrotate:

```bash
sudo logrotate -f /etc/logrotate.conf
```

Не удаляйте активные логи вслепую.

Более безопасное усечение при необходимости:

```bash
sudo truncate -s 0 /var/log/huge.log
```

### Веб-приложение отдаёт 502 / 503 / 504

Проверка nginx:

```bash
sudo tail -f /var/log/nginx/error.log
```

Проверка бэкенд-службы:

```text
systemctl status myapp
journalctl -u myapp -n 100
```

Проверка прослушивания портов:

```bash
ss -tulpn
```

Проверка логов приложения:

```bash
journalctl -u myapp -f
```

Типичные значения:

```text
502 Bad Gateway      nginx cannot talk to backend
503 Service Unavailable backend unavailable or overloaded
504 Gateway Timeout backend too slow or unreachable
```

### Система неожиданно перезагрузилась

Список загрузок:

```bash
journalctl --list-boots
```

Ошибки предыдущей загрузки:

```bash
journalctl -b -1 -p err
```

Сообщения ядра предыдущей загрузки:

```bash
journalctl -k -b -1
```

Поиск сообщений выключения/перезагрузки:

```bash
journalctl -b -1 | grep -i "shutdown\|reboot\|panic\|oom\|killed"
```

Проверка OOM killer:

```bash
journalctl -k | grep -i "out of memory\|oom"
```

## Примеры логов с фокусом на безопасность

### Неудачные попытки SSH

```bash
sudo grep "Failed password" /var/log/auth.log
```

Подсчёт по исходным IP:

```bash
sudo grep "Failed password" /var/log/auth.log \
  | awk '{print $(NF-3)}' \
  | sort \
  | uniq -c \
  | sort -nr
```

### Использование sudo

```bash
sudo grep "sudo" /var/log/auth.log
```

Пример:

```text
May 03 14:00:01 server sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/apt update
```

Значение:

```text
alice used sudo
from terminal pts/0
while in /home/alice
to run apt update as root
```

### Логи fail2ban

Распространённые расположения:

```text
/var/log/fail2ban.log
journalctl -u fail2ban
```

Команды:

```text
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## Лучшие практики

### Для Linux-админов

* Используйте journalctl для systemd-служб.
* Используйте /var/log для традиционных текстовых логов.
* Проверяйте логи конкретных служб.
* Знайте различия своего дистрибутива.
* Используйте logrotate.
* Проверяйте использование диска джоналом.
* Централизуйте логи для нескольких серверов.
* Не удаляйте логи вслепую.
* Защищайте права на логи.

### Для разработчиков приложений

* Используйте структурированное логирование.
* Включайте метки времени.
* Включайте уровни критичности.
* Включайте имя службы.
* По возможности включайте ID запросов.
* Логируйте исключения с traceback'ами.
* Не логируйте секреты.
* Отправляйте логи в stdout под systemd или контейнерами.
* Используйте JSON-логи для продакшн-систем.

### Что не логировать

Избегайте логирования:

* паролей
* API-ключей
* приватных токенов
* сессионных cookies
* номеров кредитных карт
* персональных данных без необходимости
* приватных SSH-ключей
* учётных данных баз данных

Плохо:

```text
User login failed with password hunter2
```

Лучше:

```text
User login failed for username alice from 203.0.113.10
```

## Шпаргалка команд

### Общее

```text
tail -f /var/log/syslog
less /var/log/syslog
grep -i error /var/log/syslog
zgrep -i error /var/log/syslog.*.gz
```

### Journald

```text
journalctl
journalctl -n 100
journalctl -f
journalctl -b
journalctl -b -1
journalctl -p err
journalctl -u nginx
journalctl -u nginx -f
journalctl --since "1 hour ago"
journalctl --disk-usage
```

### Ядро

```text
dmesg
dmesg -T
journalctl -k
journalctl -k -b
```

### Службы

```text
systemctl status nginx
journalctl -u nginx -n 100
systemctl restart nginx
```

### Аутентификация

```text
grep "Failed password" /var/log/auth.log
grep "sudo" /var/log/auth.log
journalctl _COMM=sshd
```

### Logrotate

```text
cat /etc/logrotate.conf
ls /etc/logrotate.d/
cat /var/lib/logrotate/status
sudo logrotate -d /etc/logrotate.conf
sudo logrotate -f /etc/logrotate.conf
```

### Использование диска

```text
df -h
du -sh /var/log/*
find /var/log -type f -size +100M -exec ls -lh {} \;
journalctl --disk-usage
```

## Лучшие практики (итоги)

* Регулярный анализ логов стоит автоматизировать инструментами вроде `Logwatch` или `Splunk`, чтобы повысить эффективность и снизить ручной контроль.
* Важно настроить оповещения о критических событиях — с помощью инструментов вроде `Nagios` или `Prometheus` — чтобы обеспечить быструю реакцию на инциденты.
* Для защиты хранилища логов следует внедрить контроль доступа, ограничив права на файлы логов только уполномоченными лицами, чтобы чувствительные данные оставались защищёнными.
* Шифрование данных логов, особенно при передаче по сетям, критично для предотвращения несанкционированного доступа и сохранения конфиденциальности.
* Внедрение политик хранения логов необходимо для соответствия юридическим требованиям, особенно в отраслях с жёсткими мандатами на хранение данных.
* Правильное управление дисковым пространством существенно при хранении логов: нужен баланс между сохранением исторических данных для анализа и тем, чтобы ресурсы хранения не переполнялись.
* Централизованные решения логирования дают значительные преимущества, упрощая управление логами на многих серверах, снижая сложность и улучшая обзорность.
* Стоит использовать платформы вроде ELK Stack (Elasticsearch, Logstash, Kibana) для надёжных возможностей поиска и инструментов визуализации более эффективного анализа логов.
* Регулярные проверки конфигураций логирования нужны, чтобы система фиксировала все релевантные данные и не пропускала важные события.
* Поддержание актуальности ПО логирования важно, чтобы получать последние патчи безопасности и новые функции, снижая риск уязвимостей в системе.

## Задания

1. Обсудите важность логирования в системном администрировании, включая его роль в поддержании здоровья системы, выявлении проблем и содействии аудиту безопасности. Приведите примеры того, как логирование помогает в повседневных административных задачах и долгосрочном мониторинге системы.
2. Изучите и опишите Journald, его функции и преимущества перед традиционными системами логирования на текстовых файлах. Объясните, как Journald работает с systemd, подчёркивая такие возможности, как бинарное хранение, структурированное логирование и то, как он упрощает управление логами для современных систем.
3. Объясните, как работает Rsyslog, и опишите процесс его настройки, включая организацию централизованного логирования. Обсудите уровни критичности, то, как они категоризируют сообщения журнала, и как их можно использовать для фильтрации сообщений определённых типов по важности или срочности.
4. Используйте команду `logger` для создания кастомных сообщений в системных логах. Поэкспериментируйте с разными флагами, такими как указание facility или уровня критичности, и объясните, как `logger` можно использовать для добавления записей вручную или из скриптов для тестирования или информационных целей.
5. Настройте и используйте `logrotate` для автоматизации управления файлами логов. Создайте базовую конфигурацию для ротации, сжатия и удаления файлов логов по расписанию и обсудите, как `logrotate` помогает предотвращать чрезмерное потребление диска логами. Объясните важность ротации логов в продакшн-системах.
6. Изучите распространённые форматы файлов логов, такие как текстовые, JSON и бинарные, и сравните их структуры. Обсудите плюсы и минусы каждого формата, учитывая читаемость, совместимость с инструментами анализа логов и эффективность хранения и поиска.
7. Настройте и используйте фильтры логов для выборочного включения или исключения конкретных сообщений. Используйте Rsyslog или Journald и создайте правило, фильтрующее сообщения по критериям вроде facility, уровня критичности или ключевых слов. Задокументируйте, как фильтрация помогает снизить шум в логах и улучшить читаемость.
8. Используйте инструменты анализа логов вроде `grep`, `journalctl` или `awk` для извлечения значимой информации из файлов логов. Выполните задачи вроде поиска конкретных событий, выявления паттернов и генерации сводных отчётов. Объясните, как анализ логов помогает администраторам выявлять проблемы и следить за здоровьем системы.
9. Изложите лучшие практики управления логами в продакшн-окружении. Обсудите стратегии хранения логов, безопасности логов и обеспечения надёжности и доступности файлов логов. Включите рекомендации по безопасному хранению и передаче логов, особенно для целей комплаенса. Также опишите распространённые проблемы, связанные с логированием, такие как пропавшие логи, повреждение файлов логов или исчерпание дискового пространства из-за роста логов, и объясните шаги диагностики и решения каждой проблемы.
10. Если удалить файл логов приложения на продакшн-сервере, может ли это привести к остановке работы приложения?

**********

[logs](/tags/logs.md)
[linux](/tags/linux.md)
[systemd](/tags/systemd.md)