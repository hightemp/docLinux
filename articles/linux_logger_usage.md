# Как использовать `logger` в Linux

Команда `logger` в [Linux](https://www.networkworld.com/article/3215226/linux/what-is-linux-uses-featres-products-operating-systems.html) позволяет легко добавлять записи в `/var/log/syslog` — из командной строки, сценариев или других файлов. В этой статье рассмотрим, как она работает.

## Насколько это просто?

Очень просто. Введите `logger <сообщение>` в командной строке, и сообщение будет добавлено в конец файла `/var/log/syslog`.

```console
$ logger comment to be added to log
$ tail -1 /var/log/syslog
May 21 18:02:16 butterfly shs: comment to be added to log
```

## Вывод команды

Можно также добавить вывод команды, заключив её в обратные кавычки.

```console
$ logger `who`
$ tail -1 /var/log/syslog
May 21 18:02:43 butterfly shs: shs pts/0 2018-05-21 15:57 (192.168.0.15)
```

## Содержимое файла

Содержимое текстового файла можно добавить с помощью опции `-f`. После неё укажите имя файла, содержимое которого нужно записать в журнал, как показано ниже.

```console
$ cat msg
Backups to off-site facility will run this coming weekend.
System availability will not be affected.
$ logger -f msg
$ tail -2 /var/log/syslog
May 21 18:06:01 butterfly shs: Backups to off-site facility will run this coming weekend.
May 21 18:06:01 butterfly shs: System availability will not be affected.
```

## Использование `logger` в сценариях

Команды `logger` можно добавлять в сценарии, чтобы было проще отслеживать завершение важных задач.

```console
$ grep logger /bin/runme
logger "$0 completed at `date`"
$ sudo runme
$ tail -1 /var/log/syslog
May 21 17:57:36 butterfly shs: ./runme completed at Mon May 21 17:57:36 EDT 2018
```

## Ограничение размера записей `logger`

Если вас беспокоит объём данных, добавляемых в журнал, особенно при записи содержимого файла, его можно ограничить с помощью опции `--size`. В следующем примере задан намеренно маленький размер, чтобы наглядно показать результат.

```console
$ logger --size 10 12345678901234567890123456789012345678901234567890
$ tail -1 /var/log/syslog
May 21 18:18:02 butterfly shs: 1234567890
```

Эта опция работает не совсем так, как можно ожидать: если входные данные содержат пробелы, ограничение применяется к каждой строке, а не ко всему тексту целиком.

```console
$ logger --size 5 `date`
$ tail -5 /var/log/syslog
May 22 08:35:51 butterfly shs: May
May 22 08:35:51 butterfly shs: 22
May 22 08:35:51 butterfly shs: 08:35
May 22 08:35:51 butterfly shs: EDT
May 22 08:35:51 butterfly shs: 2018
```

Пусть эти простые примеры не вводят вас в заблуждение. Обычно опцию `--size` используют для ограничения больших объёмов текста. По умолчанию максимальный размер составляет 1 КиБ (1024 байта).

## Игнорирование пустых строк

Опция `-e` позволяет не записывать в журнал пустые строки: они будут просто проигнорированы. Однако строка, содержащая пробелы, пустой не считается.

```console
$ cat appts
Appts <=== file includes blank line
8 AM -- get to office
8:30 AM -- meet with boss
11:00 AM -- staff meeting
$ logger -e -f appts
May 22 08:17:31 butterfly shs: Appts <=== log does not
May 22 08:17:31 butterfly shs: 8 AM -- get to office
May 22 08:17:31 butterfly shs: 8:30 AM -- meet with boss
May 22 08:17:31 butterfly shs: 11:00 AM -- staff meeting
May 22 08:17:33 butterfly kernel: \[58833.758599\] \[UFW BLOCK\] IN=enp0s25 OUT= MAC=01:00:5e:00:00:fb:ac:63:be:ca:10:cf:08:00 SRC=192.168.0.9 DST=224.0.0.251 LEN=32 TOS=0x00 PREC=0xC0 TTL=1 ID=0 DF PROTO=2
```

## Другие опции

У `logger` есть и другие возможности — например, запись в журнал на другом сервере с помощью опции `-n` или тестовый запуск с `--no-act`. Подробности можно найти на странице руководства.

---

[логи](/tags/logs.md)
[logger](/tags/logger.md)
