# Максимизируем число одновременных подключений к веб-серверу

Источник: [Maximize your concurrent web server connections](https://wakatime.com/blog/47-maximize-your-concurrent-web-server-connections)

Alan Hamlett · 23 апреля 2021 · 5 мин

Для продакшн-веб-серверов большинство людей считает, что масштабирование означает необходимость в более быстром (и более дорогом) железе. Прежде чем тратить больше денег на серверы, сначала убедитесь, что процесс вашего веб-сервера использует максимум доступных подключений, поддерживаемых вашим ядром Linux. Есть 3 уровня, которые нужно проверить и настроить:

  1. file-max ядра
  2. file-max процесса (ulimit)
  3. file-max в конфигурации systemd/сервера (LimitNOFILE)

Любой из этих уровней может ограничить максимальное число подключений, доступных процессу вашего веб-сервера.

Это становится по-настоящему полезным, когда ваш веб-сервер не упирается в RAM или CPU. Например, при использовании [HAProxy для балансировки нагрузки веб-серверов Nginx](https://wakatime.com/blog/23-how-to-scale-ssl-with-haproxy-and-nginx). HAProxy не обрабатывает запросы и почти не нагружает CPU, но ему нужно удерживать большое количество одновременных подключений. Увеличение file-max также полезно для продакшн-серверов Nginx, Apache и даже для ваших серверов баз данных Redis и Postgres.

### Максимум открытых файловых дескрипторов (Kernel file-max)

Каждое ядро Linux поддерживает определённое максимальное количество открытых файлов (или socket'ов) на процесс. Далее мы будем называть это `file-max`. Чтобы проверить текущий file-max ядра, выполните:

```bash
cat /proc/sys/fs/file-max
```

Например, у инстансов DigitalOcean за $5/мес file-max равен 9 триллионам:

```text
$ cat /proc/sys/fs/file-max
9223372036854775807
```

![размер небольшого дроплета DigitalOcean](https://wakatime.com/static/img/blog/digitalocean-small-droplet.png)

Вы всё равно никогда не сможете использовать эти 9 трлн одновременных подключений. Дело в том, что каждое открытое подключение [использует порядка 1 КБ RAM](https://serverfault.com/questions/330795/what-are-the-ramifications-of-increasing-the-maximum-of-open-file-descriptors/330981#answer-330981:~:text=One%20file%20with%20associated%20inode%20and%20dcache%20is%20very%20roughly%201K.), а DigitalOcean не предлагает ни одного инстанса с таким количеством RAM.

Если ваш file-max по умолчанию слишком мал, увеличьте его, добавив эту строку в файл `/etc/sysctl.conf`:

```bash
fs.file-max = 1000000
```

Загрузите новый file-max, выполнив `sysctl -p` от root. Теперь file-max вашего ядра должен показывать 1 млн доступных одновременных подключений:

```text
$ cat /proc/sys/fs/file-max
1000000
```

Однако, если проверить file-max вашего текущего процесса, вы увидите, что он намного ниже file-max ядра:

```text
$ ulimit -Sn
1024
```

Если вы используете Node.js, это максимум 1 тыс. одновременных подключений, но если ваш веб-сервер запускает несколько рабочих процессов, умножьте 1 тыс. на количество процессов, чтобы получить ваш максимум подключений. Так или иначе, для продакшн-веб-сервера это немного одновременных подключений. Чтобы реально использовать эти 1 млн одновременных подключений, процессу вашего веб-сервера нужно поднять ulimit.

### Ulimit (file-max процесса)

У вашего ядра Linux file-max равен 1 млн, но давайте проверим file-max процесса вашего веб-сервера nginx:

```bash
$ cat /proc/`ps -aux | grep -m 1 nginx | awk -F ' ' '{print $2}'`/limits | grep "open files" | awk -F ' ' '{print $4}'
1024
```

Что это? Nginx может обрабатывать лишь 1 тыс. одновременных подключений, когда ядро поддерживает 1 млн?

Это потому, что нам нужно увеличить настройку file-max для пользователя `nginx`. Для этого добавьте эти строки в ваш файл `/etc/security/limits.conf`:

```text
* soft nofile 1000000
* hard nofile 1000000
```

`*` означает всех пользователей, кроме пользователя `root`, а можно указать конкретное имя пользователя, например `nginx soft nofile 1000000`. Теперь ваш пользователь Nginx имеет право открывать 1 миллион подключений, но ваш процесс Nginx всё ещё не будет использовать эти 1 млн подключений. Потому что вам также нужно отредактировать unit-файл systemd для Nginx.

### File-max в systemd (LimitNOFILE)

При запуске Nginx под управлением [systemd](https://www.freedesktop.org/software/systemd/man/systemd.service.html) вы заметите, что процессы Nginx не показывают доступный лимит file-max в 1 млн. Это потому, что процесс может задавать собственный ulimit, а systemd по умолчанию устанавливает низкий лимит. Чтобы это исправить, добавьте `LimitNOFILE=1000000` в ваш файл `/etc/systemd/system/nginx.service` в блок `[Service]`:

```ini
[Unit]
Description=A high performance web server and a reverse proxy server
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
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
```

Выполните `systemctl daemon-reload`, чтобы применить изменения, и теперь ваши процессы Nginx показывают 1 млн при проверке их лимита file-max:

```text
$ cat /proc/`ps -aux | grep -m 1 nginx | awk -F ' ' '{print $2}'`/limits | grep "open files" | awk -F ' ' '{print $4}'
1000000
```

### Haproxy

Другое ПО, например [haproxy](https://cbonte.github.io/haproxy-dconv/2.0/configuration.html#maxconn), иногда задаёт собственный ulimit file-max. Если вы увеличили указанные выше лимиты, а дочерний процесс haproxy всё ещё не показывает 1 млн, попробуйте добавить `maxconn 1000000` в ваш файл `haproxy.cfg`. Мы также перешли с init.d на systemd для управления haproxy, поскольку задавать `LimitNOFILE` в systemd крайне просто:

```ini
[Unit]
Description=HAProxy Service

[Service]
ExecStart=/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg
ExecReload=/bin/kill -USR2 $MAINPID
Restart=always
KillSignal=SIGTERM
TimeoutStopSec=5
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
```

### Postgres

Это касается не только веб-серверов. Базы данных вроде Postgres тоже используют socket'ы, когда ваши веб-серверы подключаются к вашей базе данных. По умолчанию Postgres использует file-max в 1 тыс. на процесс. Иногда это превышает ваш ulimit по умолчанию, и вы начнёте видеть ошибку `Too many Open files` в логах Postgres. Вместо того чтобы снижать конфиг `max_files_per_process` в Postgres, просто отредактируйте ваш файл `/etc/security/limits.conf`, добавив:

```text
postgres soft nofile 1000
postgres hard nofile 1000
```

Затем перезапустите Postgres и проверьте его file-max:

```text
$ cat /proc/`ps -aux | grep -m 1 postgres | awk -F ' ' '{print $2}'`/limits | grep "open files" | awk -F ' ' '{print $4}'
1000
```

### Sysctl

Наконец, после увеличения file-max процесса вашего сервера вам также нужно подстроить сетевые настройки TCP вашего ядра через sysctl:

  * `net.ipv4.tcp_max_syn_backlog` — максимум полуоткрытых подключений, которые клиент ещё не подтвердил (ACK)
  * `net.core.somaxconn` — максимум отложенных (backlogged) подключений, которые клиент подтвердил (ACK)
  * `net.core.netdev_max_backlog` — максимум пакетов в очереди приёма

Указанные 3 — самые важные, но есть и другие:

  * `net.core.rmem_max`
  * `net.core.wmem_max`
  * `net.ipv4.tcp_rmem`
  * `net.ipv4.tcp_wmem`
  * `net.ipv4.tcp_tw_reuse`
  * `net.ipv4.ip_local_port_range`
  * `net.ipv4.tcp_max_tw_buckets`

Посмотрите [этот пост на Medium](https://medium.com/@pawilon/tuning-your-linux-kernel-and-haproxy-instance-for-high-loads-1a2105ea553e#edfd), [заметки по sysctl от Peter Mescalchin](https://bl.ocks.org/magnetikonline/2760f98f6bf654d5ad79) и [документацию по sysctl](https://www.kernel.org/doc/Documentation/sysctl/net.txt). Используйте `sysctl -a`, чтобы вывести все поддерживаемые на вашей машине конфигурации и увидеть их значения по умолчанию. Добавьте любые изменения в ваш файл `/etc/sysctl.conf`, затем выполните `sysctl -p`, чтобы применить их без необходимости перезагрузки.

### Заключение

Один последний инструмент, о котором стоит упомянуть, — [c1000k](https://github.com/ideawu/c1000k), для проверки, поддерживает ли ваша ОС 1 миллион подключений. Увеличение лимита file-max и, вероятно, несколько подстроек ядра через sysctl раскроют полный потенциал вашего веб-сервера. Если вам понравился этот пост, посмотрите также наш предыдущий пост о [дисковом совместимом с Redis сервере под названием SSDB](https://wakatime.com/blog/45-using-a-diskbased-redis-clone-to-reduce-aws-s3-bill). Он устраняет главное ограничение Redis: необходимость помещаться вашему набору данных в доступную RAM.

Эта статья с открытым исходным кодом — смело открывайте [PR на GitHub](https://github.com/wakatime/wakatime-blog/blob/master/posts/47-maximize-your-concurrent-web-server-connections.md).

**********

[nginx](/tags/nginx.md)
[file_descriptors](/tags/file_descriptors.md)
[systemd](/tags/systemd.md)