# Поиск больших файлов в Linux/macOS

Источник: [Find large files Linux/macOS](https://www.vanwerkhoven.org/blog/2024/find-large-files-linux-macos/)

19 января 2024

Несколько команд для поиска больших файлов в Linux/macOS. Для некоторых может понадобиться GNU find (поэтому в примерах есть префикс `g`).

Найти большие файлы, вывести имя файла:

```bash
find . -type f -name IMG\*MOV -size +25M
```

Найти большие файлы, вывести имя файла и размер:

```bash
find . -type f -name IMG\*MOV -size +10M -print0 | gdu --files0-from=- -hc
```

Найти большие файлы, вывести имя файла, размер и дату:

```bash
gfind . -type f -name IMG\*MOV -size +10M -printf '%TY-%Tm-%Td %s %f\n'
```

Найти большие файлы в текущем каталоге и проверить, существуют ли они где-то ещё в системе. Здесь нужно получить только имя файла без пути ('./'):

```bash
gfind . -type f -name IMG\*MOV -size +10M -printf '%TY-%Tm-%Td %s %p\n ' -exec sh -c 'gfind ~/Pictures/ -name $(basename "$0")' '{}' ';'
gfind . -type f -name IMG\*HEIC -size +2M -printf '%TY-%Tm-%Td %s %p\n ' -exec sh -c 'gfind ~/Pictures/ -name $(basename "$0")' '{}' ';'

find . -type f -name IMG\*HEIC -size +2000k -print0
```

Найти файлы, сгруппировать по дате изменения и посчитать суммарный размер:

```bash
gfind ./ -maxdepth 1 -type f -printf '%TY-%Tm-%Td %s\n'|awk '{sum[$1]+= $2;}END{for (date in sum){print date, sum[date];}}'|sort
```

**********

[find](/tags/find.md)
[Linux](/tags/linux.md)