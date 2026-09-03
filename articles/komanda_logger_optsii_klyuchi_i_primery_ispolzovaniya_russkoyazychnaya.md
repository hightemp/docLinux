# Команда logger: опции, ключи и примеры использования

Источник: [Команда logger: опции, ключи и примеры использования — русскоязычная tldr-шпаргалка по `logger`: запись сообщения в системный журнал, отправка stdin, запись на удалённый syslog-сервер через `--server`/`--port`, установка тега через `--tag` и приоритета через `--priority`.](https://900913.ru/tldr/linux/ru/logger/)

See also [logger - Общие команды (in english)](/tldr/common/en/logger/?utm_source=translate-text)

Переведено в рамках проекта [tldr-ru](https://github.com/learn-it-in-russian/tldr-ru). Licensed under the [CC-BY](https://creativecommons.org/licenses/by/4.0/) ([original work](https://github.com/tldr-pages/tldr)).

[![](/images/18f499563f506690a496244b64320149.png)](/tldr/common/en/logger/?utm_source=translate-flag "logger - Общие команды \(in english\)")

# logger

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

[ ![Изображение Шпаргалка по командам Linux, FreeBSD и MacOS](/images/00ff4d3edff25fc4c539a8535816fc73.png) ](https://900913.ru/osnovnye-komandy-linux-freebsd-i-macos-shpargalka/?utm_source=promo-badge "Перейти к Шпаргалка по командам Linux, FreeBSD и MacOS")

[ Linux Операционная система Linux (Линукс или Лайнакс) во многом похожая на проприетарную Unix. Линукс распространён на серверах, что означает, что изучая её вы улучшаете свой навык администрирования, DevOps и программирования. Открытая …  ](/tag/linux/) [ FreeBSD Заметки об Операционной Системе FreeBSD (фри бсд). Один из старейших Unix (Юникс), прародитель многих ОС, а также по мнению многих - самая свободная операционная система. Разработан в рамках общего проекта …  ](/tag/freebsd/) [ Трюки Bash Полезные заметки по работе с командной строкой: bash и прочие *sh. Однострочники, скрипты, позволяющие решать большие и малые задачи администрирования и настройки Юникс систем. Zsh для современного MacOS, Bash для …  ](/tag/bash100/) [ Терминал/Консоль Команды и инструкции терминала (консоли) Linux, MacOS, Windows и прочих операционных систем. Трюки и особенности командных оболочек, скрипты для администрирования Unix. Программирование и скриптование Windows и Linux, тонкая настройка Macos. …  ](/tag/terminal/)

Также может быть вам интересно:

  * [Как установить PostgreSQL на Linux и создать базу и пользователя](/2021/08/12/install-postgresql-and-create-user-and-database/)
  * [Так ли безопасен Linux? Несколько коммитов с уязвимосятми в stable](/2021/04/22/linux-kernel-security-experiment/)
  * [Пример своей консольной команды в Django проекте](/2021/02/05/django-custom-management-command-example/)
  * [Как на Bash посчитать число строк в проекте (директории)](/2021/02/03/calculate-lines-in-project-in-bash/)
  * [И снова sudo, и снова "решето"](/2021/01/27/broken-sudo/)

[ __](/tldr/linux/ru/login/ "login")

**********

[Linux](/tags/linux.md)
[logger](/tags/logger.md)
