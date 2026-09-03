# Продолжение: блокировка bash-скриптов с flock

Источник: [Follow-Up: Bash script locking with flock](https://www.tobru.ch/follow-up-bash-script-locking-with-flock/)

Tobias Brunner · 29 января 2013 · 1 мин

После моего поста [Easy bash script locking with mkdir](http://tobrunet.ch/2013/01/easy-bash-script-locking-with-mkdir/?ref=tobru.ch) я получил много откликов и многое узнал о блокировках (спасибо моему коллеге [@nine_ch](http://twitter.com/nine_ch?ref=tobru.ch)).

Одно из того, что я узнал: в Linux есть flock. Это функция ядра, к которой можно обращаться с помощью одноимённой утилиты flock. С её помощью можно легко организовать блокировку для bash-скриптов. Пример:

```bash
# stop on errors
set -e

scriptname=$(basename $0)
pidfile="/var/run/${scriptname}"

# lock it
exec 200>$pidfile
flock -n 200 || exit 1
pid=$$
echo $pid 1>&200

## Your code:
```

Требуются пояснения:

  * Строка 8 открывает файловый дескриптор с номером 200 на `$pidfile`.
  * Строка 9 использует `flock` для эксклюзивной блокировки дескриптора 200.
  Параметр `-n` означает «завершиться с ошибкой (код выхода 1), а не ждать, если блокировку нельзя получить немедленно».
  Это отлавливается конструкцией с `||`, и скрипт завершится, если блокировка не удалась — например, когда дескриптор уже заблокирован.
  * Строка 10 записывает PID в файловый дескриптор.

Всё, что идёт после `Your code`, выполняется, только если получена эксклюзивная блокировка дескриптора 200. Это гарантирует одновременный запуск только одного экземпляра.

Отличная статья на эту тему: [using flock to protect critical sections in shell scripts](http://jdimpson.livejournal.com/5685.html?ref=tobru.ch).

Мой вывод: я использую flock — это гораздо проще и надёжнее, чем подход с mkdir. Но если вам нужны кроссплатформенные bash-скрипты (Linux, BSD, ...) — лучше не полагаться на flock: в таком виде он доступен только в Linux.

**********

[flock](/tags/flock.md)
[bash](/tags/bash.md)
[Linux](/tags/linux.md)