# Примеры sed

Манипуляции с текстом (Обратите внимание, sed использует stdin и stdout, так что если Вы хотите редактировать файлы, добавляйте newfile)

## Заменить foo на too.

```
$ sed -i 's/foo/too/'

```

* * *



## Удалить 14ю строку.

```
$ sed -i '14d' /file

```

* * *



## Удалить строку содержащую Network или network.

```
$ sed -i '/[Nn]etwork/d' /file

```

* * *



## Добавить в конец файла "\[mounts\]" затем перенос на новую строка и "user root".

```
$ sed -i '$ a \\n[mounts]\nuser root' /etc/munin/config 

```

* * *



## После 14ой строки добавить "echo "graph\_category logger"".

```
$ sed '14a\ echo \"graph_category logger\"' /etc/munin/plugins/command 

```

* * *



## Вставить в начало файла '# vim: ft=ruby' и перенос строки.

```
$ sed '1i # vim: ft=ruby\n'  

```

* * *



## Заменить повторяющиеся пустые строки на одну пустую строку

```
$ sed -e ':a;/^$/N;/\n$/{D;ba}' file.txt

```

* * *



## Конвертация переносов строк DOS (CR/LF) в Unix (LF)

```
$ sed 's/.$//' dosfile.txt > unixfile.txt

```

* * *



## Заменить строку string1 строкой string2

```
$ sed 's/string1/string2/g'

```

* * *



## Изменить строку anystring1 на anystring2

```
$ sed 's/\(.*\)1/\12/g'

```

* * *



## Убрать комментарии и пустые строки

```
$ sed '/ *#/d; /^ *$/d'

```

* * *



## Соединить строки (линии) с предшествующим \\

```
$ sed ':a; /\\$/N; s/\\\n//; ta'

```

* * *



## Удалить предшествующие пробелы с строк

```
$ sed 's/[ \t]*$//'

```

* * *



## Заескейпить активные метасимволы оболочки двумя ковычками

```
$ sed 's/\([\\`\\"$\\\\]\)/\\\1/g'

```

* * *



## Выровнять числа по правой границе

```
$ seq 10 | sed "s/^/      /; s/ *\(.\{7,\}\)/\1/"

```

* * *



## Напечатать 1000-ную строку

```
$ sed -n '1000p;1000q'

```

* * *



## Напечатать строки с 10 по 20-ую

```
$ sed -n '10,20p;20q'

```

* * *



## Получить title из HTML страницы

```
$ sed -n 's/.*<title>\(.*\)<\/title>.*/\1/ip;T;q'

```

* * *



## Убрать пустые строки из файла

```
$ sed '/^$/d' input.txt > output.txt

```

* * *



## Удаляем из всех .html файлов начало до тега , и от - до конца файла. Включая и сами теги.

```
$ cat *.html | sed '1,/<pre>/d; /<\/pre>/,$d' > final.file

```

-----------

Источники:  

*   1-6 -[ru.wikibooks.org](http://ru.wikibooks.org/wiki/Linux-hand-book)
*   7 -[xtips.ru](http://xtips.ru/?act=tview&tid=71)
*   8 -[xtips.ru](http://xtips.ru/?act=tview&tid=47)
*   9-18 -[www.pixelbeat.org](http://www.pixelbeat.org/cmdline_ru_RU.html)
*   19 -[www.cyberciti.biz](http://www.cyberciti.biz/faq/howto-linux-unix-command-remove-all-blank-lines/)