# rsync, статья 2: Окружение (2022)

Источник: [rsync, article 2: Surroundings (2022)](https://michael.stapelberg.ch/posts/2022-07-02-rsync-surroundings/)

Опубликовано 2022-07-02 · Автор · [оригинал](https://michael.stapelberg.ch/posts/2022-07-02-rsync-surroundings/)

Это вторая статья в серии постов о rsync, [см. обзор серии](https://michael.stapelberg.ch/posts/2022-06-18-rsync-overview/).

Теперь, когда мы знаем, для чего использовать rsync, как лучше всего встроить rsync в мониторинг и оповещения (alerting), и на каких операционных системах он работает?

## Мониторинг и оповещения для заданий rsync с помощью Prometheus

Когда у вас появляется одно-два важных задания `rsync`, может иметь смысл настроить оповещение на случай, если задание завершилось не так, как ожидалось.

Я использую [Prometheus](https://prometheus.io/) для всего моего мониторинга и оповещений.

Поскольку Prometheus _забирает_ (pull) метрики со своих целей (которые, как правило, работают постоянно), нам нужен дополнительный компонент: [Prometheus Pushgateway](https://prometheus.io/docs/practices/pushing/). Pushgateway хранит метрики, отправленные короткоживущими заданиями вроде передач `rsync`, и делает их доступными для последующих опросов Prometheus.

Чтобы интегрировать `rsync` с Prometheus Pushgateway, я написал [`rsyncprom`](https://github.com/stapelberg/rsyncprom) — небольшой инструмент, который оборачивает `rsync` или разбирает вывод rsync, предоставленный вами. Когда `rsync` завершает работу, `rsyncprom` отправляет в ваш Pushgateway код выхода rsync и разобранную статистику о передаче.

### Настройка на стороне сервера Prometheus

Сначала я развернул Prometheus Pushgateway (через Docker и systemd) на своём сервере.

Затем в файле `prometheus.conf` я указал Prometheus забирать данные из моего Pushgateway:

```yaml
# prometheus.conf

rule_files:
- backups.rules.yml

scrape_configs:
# […]
- job_name: pushgateway
  honor_labels: true
  static_configs:
  - targets: ['pushgateway:9091']
```

Наконец, в `backups.rules.yml` я настраиваю оповещение по временному ряду `rsync_exit_code`:

```yaml
# backups.rules.yml

groups:
- name: backups.rules
  rules:
  - alert: RsyncFailing
    expr: rsync_exit_code{job="rsync"} > 0
    for: 1m
    labels:
      job: rsync
    annotations:
      description: rsync {{ $labels.instance }} is failing
      summary: rsync {{ $labels.instance }} is failing
```

Это оповещение срабатывает каждый раз, когда задание rsync, отслыкуемое через `rsyncprom`, завершается с ненулевым кодом выхода.

### Настройка на стороне клиента rsync

На каждой машине, где выполняются отслеживаемые задания `rsync`, я сначала устанавливаю `rsyncprom`:

```bash
go install github.com/stapelberg/rsyncprom/cmd/rsync-prom@latest
```

Затем я просто оборачиваю передачи `rsync` там, где это удобнее всего, например в моём [`crontab(5)`](https://manpages.debian.org/crontab.5):

```bash
# crontab -e
9 9 * * * /home/michael/go/bin/rsync-prom --job="cron" --instance="gphotos-sync@midna" -- /home/michael/gphotos-sync/sync.sh
```

Тот же приём с обёрткой работает в [shell-скриптах или файлах systemd-сервисов](https://github.com/stapelberg/rsyncprom#setup-example-systemd).

Вывод `rsync` можно также передавать [из кода на Go](https://github.com/stapelberg/zkj-nas-tools/blob/02d46d718df60c413844d9218f6dd702ad94e5f1/dornroeschen/sshutil.go#L134-L139) (этот пример запускает `rsync` через SSH).

### Архитектура мониторинга

Вот как вся эта схема выглядит архитектурно:

![архитектура rsync-prom](https://michael.stapelberg.ch/posts/2022-07-02-rsync-surroundings/2022-05-29-rsync-prom-architecture.svg)

Планировщик rsync работает на Raspberry Pi под управлением [gokrazy](https://gokrazy.org/). Планировщик запускает задание `rsync` для резервного копирования _websrv.zekjur.net_ по SSH и отправляет вывод в Prometheus, который работает на (другом) сервере у интернет-провайдера.

### Дашборд мониторинга

Дашборд grafana выглядит в работе так:

[![дашборд rsync в grafana](/images/206f8133cb1202814ec1f77c064ee1e3.png)](https://michael.stapelberg.ch/posts/2022-07-02-rsync-surroundings/2022-06-12-rsync-grafana-featured.jpg)

  * Таблица в левом верхнем углу показывает последний код выхода rsync; зелёный означает 0 (успех).
  * График в правом верхнем углу показывает время работы rsync (время по настенным часам, wall-clock time) с течением времени. Причиной долгого времени работы может быть любое количество узких мест: сетевые соединения, устройства хранения, медленные CPU.
  * График в левом нижнем углу показывает размер набора данных rsync с течением времени. Это позволяет быстро выявить передачи, которые заполняют ваш диск.
  * График в правом нижнем углу показывает количество переданных байт на один запуск rsync с течением времени. Чем выше значение, тем больше объём изменений в вашем наборе данных между запусками синхронизации.

## Доступность rsync в операционных системах

Теперь, когда мы узнали о нескольких типичных сценариях использования, где можно применять `rsync` для этих сценариев? Ответ: в большинстве окружений, поскольку `rsync` широко доступен в различных версиях Linux и BSD.

На Mac `rsync` доступен по умолчанию (но это старая пропатченная версия), а OpenBSD по умолчанию поставляется с реализацией под лицензией BSD под названием [openrsync](https://www.openrsync.org/).

На Windows можно использовать [Windows Subsystem for Linux](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux).

Операционная система | Реализация | Версия
---|---|---
FreeBSD 13.1 (ports) | tridge | [3.2.3](https://www.freebsd.org/cgi/man.cgi?query=rsync&manpath=FreeBSD+13.1-RELEASE+and+Ports)
OpenBSD 7.1 | openrsync | (7.1)
OpenBSD 7.1 (ports) | tridge | [3.2.4](https://openports.se/net/rsync)
NetBSD 9.2 (pkgsrc) | tridge | [3.2.4](https://ftp.netbsd.org/pub/pkgsrc/current/pkgsrc/net/rsync/index.html)
Linux | tridge | [repology](https://repology.org/project/rsync/versions)
macOS | tridge | [2.6.9](https://www.unix.com/man-page/osx/1/rsync/)

## Что дальше

Третья статья в этой серии — [rsync, статья 3: Как работает rsync?](https://michael.stapelberg.ch/posts/2022-07-02-rsync-how-does-it-work/). Теперь, когда rsync запущен и работает, пора заглянуть под капот rsync, чтобы лучше понять, как он устроен.

**********

[rsync](/tags/rsync.md)
[monitoring](/tags/monitoring.md)
[backup](/tags/backup.md)