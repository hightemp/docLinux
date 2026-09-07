# Команда logger: опции, ключи и примеры использования

Источник: [Команда logger: опции, ключи и примеры использования — русскоязычная tldr-шпаргалка по `logger`: запись сообщения в системный журнал, отправка stdin, запись на удалённый syslog-сервер через `--server`/`--port`, установка тега через `--tag` и приоритета через `--priority`.](https://900913.ru/tldr/linux/ru/logger/)

Переведено в рамках проекта [tldr-ru](https://github.com/learn-it-in-russian/tldr-ru). Licensed under the [CC-BY](https://creativecommons.org/licenses/by/4.0/) ([original work](https://github.com/tldr-pages/tldr)).

## logger

> Добавляет сообщение в системный журнал (/var/log/syslog).

  * Записать сообщение в системный журнал:

`logger {{message}}`

  * Записать в системный журнал сообщение со стандартного ввода:

`echo {{log_entry}} | logger`

  * Записать сообщение в сервер syslog, запущенный на заданном порту. Порт по умолчанию - 514:

`echo {{log_entry}} | logger --server {{hostname}} --port {{port}}`

  * Пометить заданным тегом каждую строку сообщения. Если эта опция не указана, то в качестве тега используется имя пользователя:

`echo {{log_entry}} | logger --tag {{tag}}`

  * Указать приоритет сообщения. Значение по умолчанию - `user.notice`, прочие варианты перечислены в `man logger`.

`echo {{log_entry}} | logger --priority {{user.warning}}`

**********

[Linux](/tags/linux.md)
[logger](/tags/logger.md)
