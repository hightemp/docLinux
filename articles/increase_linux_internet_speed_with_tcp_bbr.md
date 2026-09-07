# Увеличение скорости интернета в Linux с TCP BBR

Источник: [Increase your Linux server Internet speed with TCP BBR congestion control](https://www.cyberciti.biz/cloud-computing/increase-your-linux-server-internet-speed-with-tcp-bbr-congestion-control/)

Вивек Гите (Vivek Gite), nixCraft

Недавно я [узнал](https://cloudplatform.googleblog.com/2017/07/TCP-BBR-congestion-control-comes-to-GCP-your-Internet-just-got-faster.html), что TCP BBR значительно увеличил пропускную способность и снизил задержки для соединений во внутренних магистральных сетях Google, а пропускную способность веб-серверов google.com и YouTube — в среднем на 4% по всему миру и более чем на 14% в некоторых странах. Патч TCP BBR должен быть применён к ядру Linux. Первый публичный релиз BBR состоялся в сентябре 2016 года. Патч доступен каждому для скачивания и установки. Другой вариант — использование Google Cloud Platform (GCP). GCP по умолчанию включает использование передового нового алгоритма управления перегрузками (congestion control) под названием TCP BBR. Эта страница объясняет, как увеличить скорость интернета вашего Linux-сервера с помощью конфигурации TCP BBR. Эта простая настройка улучшает производительность вашей сети.

## Требования для скорости интернета Linux-сервера с TCP BBR

Убедитесь, что ваше ядро Linux имеет следующие опции, скомпилированные как модуль или встроенные в ядро Linux:

1. CONFIG_TCP_CONG_BBR
2. CONFIG_NET_SCH_FQ

### Управление перегрузками Linux TCP BBR

Вы должны использовать ядро Linux версии 4.9 или выше. В Debian/Ubuntu Linux выполните следующие [команды grep](https://www.cyberciti.biz/faq/howto-use-grep-command-in-linux-unix/ "How to use grep command In Linux / UNIX with examples")/[egrep](https://www.cyberciti.biz/faq/grep-regular-expressions/ "Regular expressions in grep ( regex ) with examples"):

```bash
$ grep 'CONFIG_TCP_CONG_BBR' /boot/config-$(uname -r)
$ grep 'CONFIG_NET_SCH_FQ' /boot/config-$(uname -r)
$ grep -E 'CONFIG_TCP_CONG_BBR|CONFIG_NET_SCH_FQ' /boot/config-$(uname -r)
```

[![Рис.01: Убедитесь, что ваше ядро Linux имеет настроенную опцию TCP BBR](/images/3cabdc2d9ee28179c746ef8dabe8b9bd.png)](https://www.cyberciti.biz/media/new/cms/2017/07/verification-tcp-bbr.png)

Рис.01: Убедитесь, что ваше ядро Linux имеет настроенную опцию TCP BBR

Я использую ядро Linux версии 4.9.0-8-amd64 на Debian и 4.18.0-15-generic на сервере Ubuntu. Если вышеуказанные опции не найдены, вам нужно либо [скомпилировать последнее ядро](https://www.cyberciti.biz/faq/debian-ubuntu-building-installing-a-custom-linux-kernel/), либо [установить последнюю версию ядра Linux](https://www.cyberciti.biz/faq/installing-latest-stable-mainline-linux-kernel-on-ubuntu-with-apt-get/) с помощью команды [apt-get](https://www.cyberciti.biz/tips/linux-debian-package-management-cheat-sheet.html "Ubuntu/Debian Linux apt-get package management cheat sheet")/[apt](https://www.cyberciti.biz/faq/ubuntu-lts-debian-linux-apt-command-examples/ "apt Command Examples for Ubuntu/Debian Linux").

## Запустите тест перед включением TCP BBR для улучшения скорости сети

Выполните следующую команду на Linux-сервере:

```bash
# iperf -s
```

![Как проверить скорость сети Linux-сервера перед включением TCP BBR](/images/08a06bee3a2c16d51b9e4ccee9c23a2b.png)

Выполните следующее на вашем Linux-клиенте:

```bash
$ iperf -c gcvm.backup -i 2 -t 30
```

![Как увеличить скорость интернета Linux-сервера с TCP BBR](/images/379252afc4c0e8f92c9eb03a5499fa1b.png)

## Как включить управление перегрузками TCP BBR в Linux

Отредактируйте [файл /etc/sysctl.conf или создайте новый файл в директории /etc/sysctl.d/](https://www.cyberciti.biz/faq/reload-sysctl-conf-on-linux-using-sysctl/):

```bash
$ sudo vi /etc/sysctl.conf
```

ИЛИ

```bash
$ sudo vi /etc/sysctl.d/10-custom-kernel-bbr.conf
```

Добавьте следующие две строки:

```ini
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
```

[Сохраните и закройте файл, т.е. выйдите из текстового редактора vim/vi](https://www.cyberciti.biz/faq/linux-unix-exit-vim-editor/), введя **:x!**. Далее вы должны либо [перезагрузить Linux-машину](https://www.cyberciti.biz/faq/linux-reboot-command/), либо перезагрузить изменения с помощью команды sysctl:

```bash
$ sudo reboot
```

ИЛИ

```bash
$ sudo sysctl --system
```

Примерные выводы:

```text
* Applying /etc/sysctl.d/10-console-messages.conf ...
kernel.printk = 4 4 1 7
* Applying /etc/sysctl.d/10-custom.conf ...
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
* Applying /etc/sysctl.d/10-ipv6-privacy.conf ...
net.ipv6.conf.all.use_tempaddr = 2
net.ipv6.conf.default.use_tempaddr = 2
* Applying /etc/sysctl.d/10-kernel-hardening.conf ...
kernel.kptr_restrict = 1
* Applying /etc/sysctl.d/10-link-restrictions.conf ...
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
* Applying /etc/sysctl.d/10-lxd-inotify.conf ...
fs.inotify.max_user_instances = 1024
* Applying /etc/sysctl.d/10-magic-sysrq.conf ...
kernel.sysrq = 176
* Applying /etc/sysctl.d/10-network-security.conf ...
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
* Applying /etc/sysctl.d/10-ptrace.conf ...
kernel.yama.ptrace_scope = 1
* Applying /etc/sysctl.d/10-zeropage.conf ...
vm.mmap_min_addr = 65536
* Applying /etc/sysctl.d/99-sysctl.conf ...
* Applying /etc/sysctl.conf ...
```

Вы можете проверить новые настройки следующей командой sysctl. Выполните:

```bash
$ sysctl net.core.default_qdisc
net.core.default_qdisc = fq
$ sysctl net.ipv4.tcp_congestion_control
net.ipv4.tcp_congestion_control = bbr
```

## Тест управления перегрузками BBR в Linux

В моём тестировании между двумя удалёнными Linux-серверами с гигабитными портами, подключёнными к интернету, я смог поднять скорость с 250 Мбит/с до 800 Мбит/с. Вы можете использовать инструменты вроде команды [wget](https://www.cyberciti.biz/tips/linux-wget-your-ultimate-command-line-downloader.html "Wget Command in Linux with Examples") для измерения скорости полосы пропускания:

```bash
$ wget https://your-server-ip/file.iso
```

Я также заметил, что [смог выжать почти 100 Мбит/с для трафика OpenVPN](https://www.cyberciti.biz/faq/howto-setup-openvpn-server-on-ubuntu-linux-14-04-or-16-04-lts/). Ранее я мог выжимать только 30–40 Мбит/с. В целом я вполне доволен опцией управления перегрузками TCP BBR для моей Linux-машины. [Проверьте дисковое пространство](https://www.cyberciti.biz/faq/linux-check-disk-space-command/) с помощью команды [df](https://www.cyberciti.biz/faq/df-command-examples-in-linux-unix/ "How to use df command in Linux / Unix {with examples}") или размер директории с помощью команды du и удалите скачанный ISO-файл с помощью wget. Например:

```bash
$ df -H
$ du -csh
$ rm file.iso
```

## Тест Linux TCP BBR с iperf

iperf — часто используемый инструмент сетевого тестирования для потоков данных TCP/UDP. Он измеряет пропускную способность сети. Этот инструмент может подтвердить важность настроек Linux TCP BBR.

### Выполните команду на Linux-сервере с включённым управлением перегрузками TCP BBR

```bash
# iperf -s
```

Примерные выводы:

```text
------------------------------------------------------------
Server listening on TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[ 4] local 10.128.0.2 port 5001 connected with AAA.BB.C.DDD port 46978
[ ID] Interval       Transfer     Bandwidth
[ 4]  0.0-30.6 sec   127 MBytes  34.7 Mbits/sec
```

### Выполните команду на Linux/Unix-клиенте

```bash
$ iperf -c YOUR-Linux-Server-IP-HERE -i 2 -t 30
```

Примерный вывод при подключении к серверу с включённым TCP BBR:

```text
------------------------------------------------------------
Client connecting to gcp-vm-nginx-www1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  3] local 10.8.0.2 port 46978 connected with xx.yyy.zzz.tt port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 2.0 sec  4.00 MBytes  16.8 Mbits/sec
[  3]  2.0- 4.0 sec  8.50 MBytes  35.7 Mbits/sec
[  3]  4.0- 6.0 sec  10.9 MBytes  45.6 Mbits/sec
[  3]  6.0- 8.0 sec  16.2 MBytes  68.2 Mbits/sec
[  3]  8.0-10.0 sec  5.29 MBytes  22.2 Mbits/sec
[  3] 10.0-12.0 sec  9.38 MBytes  39.3 Mbits/sec
[  3] 12.0-14.0 sec  8.12 MBytes  34.1 Mbits/sec
[  3] 14.0-16.0 sec  8.12 MBytes  34.1 Mbits/sec
[  3] 16.0-18.0 sec  8.38 MBytes  35.1 Mbits/sec
[  3] 18.0-20.0 sec  6.75 MBytes  28.3 Mbits/sec
[  3] 20.0-22.0 sec  8.12 MBytes  34.1 Mbits/sec
[  3] 22.0-24.0 sec  8.12 MBytes  34.1 Mbits/sec
[  3] 24.0-26.0 sec  9.50 MBytes  39.8 Mbits/sec
[  3] 26.0-28.0 sec  7.00 MBytes  29.4 Mbits/sec
[  3] 28.0-30.0 sec  8.12 MBytes  34.1 Mbits/sec
[  3]  0.0-30.3 sec  127 MBytes  35.0 Mbits/sec
```

## Заключение

Средняя статистика управления перегрузками Bottleneck Bandwidth and RTT (BBR) до и после, собранная за 30 секунд с помощью команды iperf:

1. ДО BBR: Передано: 27.5 МБайт. Полоса пропускания: 7.15 Мбит/с
2. ПОСЛЕ BBR: Передано: 127 МБайт. Полоса пропускания: 35.0 Мбит/с

BBR — это, по моему мнению, одно из важнейших улучшений сетевого стека Linux за последние годы. Эта страница показала, как включить и настроить BBR на Linux-системе. Для получения дополнительной информации смотрите следующие страницы:

* [Measure Network Performance: Find Bandwidth, Jitter, Datagram Loss With Iperf](https://www.cyberciti.biz/tips/find-network-throughput-jitter-packet-loss.html)
* Информация о BBR от [Google](https://github.com/google/bbr)
* TCP BBR congestion control comes to GCP. Your Internet just got [faster](https://cloud.google.com/blog/products/gcp/tcp-bbr-congestion-control-comes-to-gcp-your-internet-just-got-faster)

Обязательно изучите документацию с помощью команд [man](https://bash.cyberciti.biz/guide/Man_command "Man command - Linux Bash Shell Scripting Tutorial Wiki") или [help](https://bash.cyberciti.biz/guide/Help_command "help command - Linux Bash Shell Scripting Tutorial Wiki"):

```bash
$ man sysctl
$ man iperf
```

---

[tcp](/tags/tcp.md)
[linux](/tags/linux.md)
[сеть](/tags/networking.md)
