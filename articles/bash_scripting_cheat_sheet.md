# Шпаргалка по Bash-скриптингу

### Пример

```bash
#!/usr/bin/env bash

NAME="John"
echo "Hello $NAME!"

```

### Переменные

```bash
NAME="John"
echo $NAME
echo "$NAME"
echo "${NAME}!"

```

### Строковые кавычки

```bash
NAME="John"
echo "Hi $NAME"  #=> Hi John
echo 'Hi $NAME'  #=> Hi $NAME

```

### Shell исполнение

```bash
echo "I'm in $(pwd)"
echo "I'm in `pwd`"
# Same

```

Смотрите [Подстановка команд](http://wiki.bash-hackers.org/syntax/expansion/cmdsubst)

### Условное исполнение

```bash
git commit && git push
git commit || echo "Commit failed"

```

### Функции

```bash
get_name() {
  echo "John"
}

echo "You are $(get_name)"

```

См: [Функции](https://devhints.io/bash#functions)

### Условия

```bash
if [[ -z "$string" ]]; then
  echo "String is empty"
elif [[ -n "$string" ]]; then
  echo "String is not empty"
fi

```

См: [Условия](https://devhints.io/bash#conditionals)

### Строгий режим

```bash
set -euo pipefail
IFS=$'\n\t'

```

Смотрите: [Неофициальный bash строгий режим](http://redsymbol.net/articles/unofficial-bash-strict-mode/)

### Расширение скобки

```bash
echo {A,B}.js

```

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top: 1px solid rgba(102, 119, 136, 0.05);"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">{A,B}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Такой же как<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">A B</code></td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">{A,B}.js</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Такой же как<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">A.js B.js</code></td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">{1..5}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Такой же как<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">1 2 3 4 5</code></td></tr></tbody></table>

Смотрите: [Расширение скобок](http://wiki.bash-hackers.org/syntax/expansion/brace)

## Расширения параметров

### Основы

```bash
name="John"
echo ${name}
echo ${name/J/j}    #=> "john" (substitution)
echo ${name:0:2}    #=> "Jo" (slicing)
echo ${name::2}     #=> "Jo" (slicing)
echo ${name::-1}    #=> "Joh" (slicing)
echo ${name:(-1)}   #=> "n" (slicing from right)
echo ${name:(-2):1} #=> "h" (slicing from right)
echo ${food:-Cake}  #=> $food or "Cake"

```

```bash
length=2
echo ${name:0:length}  #=> "Jo"

```

Смотрите: [Расширение параметра](http://wiki.bash-hackers.org/syntax/pe)

```bash
STR="/path/to/foo.cpp"
echo ${STR%.cpp}    # /path/to/foo
echo ${STR%.cpp}.o  # /path/to/foo.o

echo ${STR##*.}     # cpp (extension)
echo ${STR##*/}     # foo.cpp (basepath)

echo ${STR#*/}      # path/to/foo.cpp
echo ${STR##*/}     # foo.cpp

echo ${STR/foo/bar} # /path/to/bar.cpp

```

```bash
STR="Hello world"
echo ${STR:6:5}   # "world"
echo ${STR:-5:5}  # "world"

```

```bash
SRC="/path/to/foo.cpp"
BASE=${SRC##*/}   #=> "foo.cpp" (basepath)
DIR=${SRC%$BASE}  #=> "/path/to/" (dirpath)

```

### Подмена

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO%suffix}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Удалить суффикс</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO#prefix}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Удалить префикс</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO%%suffix}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Удалить длинный суффикс</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO##prefix}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Удалить длинный префикс</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO/from/to}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить первый матч</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO//from/to}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить все</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO/%from/to}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить суффикс</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO/#from/to}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить префикс</td></tr></tbody></table>

### Комментарии

```bash
# Однострочный комментарий

```

```bash
: '
Это
многострочный
комментарий
'

```

### Подстроки

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:0:3}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Подстрока<span>&nbsp;</span><em style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; font-style: normal; color: rgb(102, 119, 136);">(положение, длина)</em></td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:-3:3}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Подстрока справа</td></tr></tbody></table>

### Длина

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${#FOO}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Длина<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">$FOO</code></td></tr></tbody></table>

### Значения по умолчанию

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:-val}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">$FOO</code>, или же<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">val</code><span>&nbsp;</span>если не установлено</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:=val}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Задать <span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">$FOO</code><span>&nbsp;</span>в<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">val</code><span>&nbsp;</span>если не установлено</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:+val}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">val</code><span>&nbsp;</span>если<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">$FOO</code><span>&nbsp;</span>установлено</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">${FOO:?message}</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Показать сообщение об ошибке и выйти, если<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">$FOO</code><span>&nbsp;</span>не установлен</td></tr></tbody></table>

`:` Является необязательным (например, `${FOO=word}` работает)

## Циклы

### Основной цикл

```bash
for i in /etc/rc.*; do
  echo $i
done

```

### C-подобный цикл

```bash
for ((i = 0 ; i < 100 ; i++)); do
  echo $i
done

```

### Диапазоны

```bash
for i in {1..5}; do
    echo "Welcome $i"
done

```

#### С размером шага 

```bash
for i in {5..50..5}; do
    echo "Welcome $i"
done

```

### Чтение линий

```bash
< file.txt | while read line; do
  echo $line
done

```

### Вечный цикл

```bash
while true; do
  ···
done

```

## Функции

### Определение функции

```bash
myfunc() {
    echo "hello $1"
}

```

```bash
# Same as above (alternate syntax)
function myfunc() {
    echo "hello $1"
}

```

```bash
myfunc "John"

```

### Возврат значений

```bash
myfunc() {
    local myresult='some value'
    echo $myresult
}

```

```bash
result="$(myfunc)"

```

### Ошибки

```bash
myfunc() {
  return 1
}

```

```bash
if myfunc; then
  echo "success"
else
  echo "failure"
fi

```

### Аргументы

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$#</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Количество аргументов</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$*</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Все аргументы</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$@</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Все аргументы, начиная с первого</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$1</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Первый аргумент</td></tr></tbody></table>

См. [специальные параметры](http://wiki.bash-hackers.org/syntax/shellvars#special_parameters_and_shell_variables).

## Условия

### Условия

Обратите внимание, что ` [[`- это на самом деле команда/программа, которая возвращает `0` (true) или `1` (ложь). Любая программа, которая подчиняется той же логике (как и все базовые утилиты, такие как `grep(1)` или `ping(1)`) можно использовать как условие, см. примеры.

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top: 1px solid rgba(102, 119, 136, 0.05);"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -z STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Пустая строка</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -n STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Не пустая строка</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING == STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Равно</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING != STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Не равно</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -eq NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Равно</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -ne NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Не равно</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -lt NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Меньше</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -le NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Меньше или равно</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -gt NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Больше</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -ge NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Больше чем или равный</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING =~ STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Регулярное выражение</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">(( NUM &lt; NUM ))</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Числовые условия</td></tr></tbody></table>

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-bottom-left-radius: 3px; border-bottom-right-radius: 3px; border-top: 1px solid rgba(102, 119, 136, 0.05);"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -o noclobber ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Если OPTIONNAME включено</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ ! EXPR ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Не</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ X ]] &amp;&amp; [[ Y ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">И</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ X ]] || [[ Y ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Или</td></tr></tbody></table>

### Файловые условия

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -e FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Существует</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -r FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Разрешение на чтение</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -h FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Симлинк</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -d FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Каталог</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -w FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Разрешение на запись</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -s FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Размер &gt; 0 байт</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -f FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Файл</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -x FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Исполняемый</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -nt FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">1 более поздняя, чем 2</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -ot FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">2 более свежая, чем 1</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -ef FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Те же файлы</td></tr></tbody></table>

### Пример

```bash
if ping -c 1 google.com; then
  echo "It appears you have a working internet connection"
fi

```

```bash
if grep -q 'foo' ~/.bash_history; then
  echo "You appear to have typed 'foo' in the past"
fi

```

```bash
# String
if [[ -z "$string" ]]; then
  echo "String is empty"
elif [[ -n "$string" ]]; then
  echo "String is not empty"
fi

```

```bash
# Combinations
if [[ X ]] && [[ Y ]]; then
  ...
fi

```

```bash
# Equal
if [[ "$A" == "$B" ]]

```

```bash
# Regex
if [[ "A" =~ "." ]]

```

```bash
if (( $a < $b )); then
   echo "$a is smaller than $b"
fi

```

```bash
if [[ -e "file.txt" ]]; then
  echo "file exists"
fi

```

## Массивы

### Определение массивов

```bash
Fruits=('Apple' 'Banana' 'Orange')

```

```bash
Fruits[0]="Apple"
Fruits[1]="Banana"
Fruits[2]="Orange"

```

### Работа с массивами

```bash
echo ${Fruits[0]}           # Элемент #0
echo ${Fruits[@]}           # Всех элементов, разделенных пробелами
echo ${#Fruits[@]}          # Количество элементов
echo ${#Fruits}             # Длина строки 1-го элемента
echo ${#Fruits[3]}          # Длина строки n-го элемента
echo ${Fruits[@]:3:2}       # Дальность (из положения 3, Длина 2)

```

### Операции

```bash
Fruits=("${Fruits[@]}" "Watermelon")    # Вставить
Fruits+=('Watermelon')                  # Вставить
Fruits=( ${Fruits[@]/Ap*/} )            # Удалить с помощью регулярного выражения
unset Fruits[2]                         # Удалить один элемент
Fruits=("${Fruits[@]}")                 # Дубликат
Fruits=("${Fruits[@]}" "${Veggies[@]}") # Обединить
lines=(`cat "logfile"`)                 # Прочитать из файла

```

### Итерации

```bash
for i in "${arrayName[@]}"; do
  echo $i
done

```

## Словари

### Определение

```bash
declare -A sounds

```

```bash
sounds[dog]="bark"
sounds[cow]="moo"
sounds[bird]="tweet"
sounds[wolf]="howl"

```

Объявляет "звук" как объект словаря (он же ассоциативный массив).

### Работа со словарями

```bash
echo ${sounds[dog]} # Собачий звук
echo ${sounds[@]}   # Все значения
echo ${!sounds[@]}  # Все ключи
echo ${#sounds[@]}  # Количество элементов
unset sounds[dog]   # Удалить собаку

```

### Итерации

#### Перебор значений

```bash
for val in "${sounds[@]}"; do
  echo $val
done

```

#### Перебирать ключи

```bash
for key in "${!sounds[@]}"; do
  echo $key
done

```

## Опции

### Опции

```bash
set -o noclobber  # Избегайте наложения файлов (echo "hi" > foo)
set -o errexit    # Используется для выхода при ошибке, избегая каскадных ошибок
set -o pipefail   # Раскрывает скрытые неудачи
set -o nounset    # Выставляет неустановленные переменные

```

### Опции Glob 

```bash
set -o nullglob    # Несоответствующие удаляются ('* .foo' => '')
set -o failglob    # При несоответствующих кидаются ошибки
set -o nocaseglob  # Нечувствительные к регистру
set -o globdots    # Подстановочные знаки соответствуют точечным файлам ("*.sh" => ".foo.sh")
set -o globstar    # Разрешить ** для рекурсивных совпадений ('lib/**/*.rb' => 'lib/a/b/c.rb')

```

Установите `GLOBIGNORE` в качестве списка шаблонов, разделенных двоеточиями, которые будут удалены из совпадений.

## История

### Команды

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">history</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Показать историю</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">shopt -s histverify</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Немедленно не выполнить развернутый результат </td></tr></tbody></table>

### Расширения

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть последний параметр последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!*</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть все параметры последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!-n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code> самых последних команд</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code> команд в истории</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!&lt;command&gt;</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть последний вызов команды<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;command&gt;</code></td></tr></tbody></table>

### Операции

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Повторно выполнить последнюю команду </td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:s/&lt;FROM&gt;/&lt;TO&gt;/</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить первое вхождение<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;FROM&gt;</code><span>&nbsp;</span>на<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;TO&gt;</code><span>&nbsp;</span>в последней команде</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:gs/&lt;FROM&gt;/&lt;TO&gt;/</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Заменить все вхождения<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;FROM&gt;</code><span>&nbsp;</span>на<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;TO&gt;</code><span>&nbsp;</span>в последней команде</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$:t</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Расширить только базовое имя из последнего параметра последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$:h</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть каталог только с последним параметром последней команды</td></tr></tbody></table>

`!!` и `!$` можно заменить любым допустимым расширением.

### Ломтики

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Расширить только<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code> токена самой последней команды (команда - <span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">0</code>; Первый аргумент - <span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">1</code>)</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!^</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть первый аргумент последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Развернуть последний маркер из последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n-m</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Расширить диапазон токенов из последней команды</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n-$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Расширить<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code> токенов до последней из последней команды</td></tr></tbody></table>

`!!` можно заменить любым допустимым расширением, т.е. `!cat`,`!-2`, `!42` и т.д.

## Разное

### Числовые расчеты

```bash
$((a + 200))      # Добавить 200 к $a

```

```bash
$((RANDOM % 200))  # Случайное число 0..199

```

### Подоболочки

```bash
(cd somedir; echo "I'm now in $PWD")
pwd # еще в первом каталоге

```

### Перенаправление

```bash
python hello.py > output.txt   # stdout to (file)
python hello.py >> output.txt  # stdout to (file), append
python hello.py 2> error.log   # stderr to (file)
python hello.py 2>&1           # stderr to stdout
python hello.py 2>/dev/null    # stderr to (null)
python hello.py &>/dev/null    # stdout and stderr to (null)

```

```bash
python hello.py < foo.txt      # подать foo.txt в stdin для python

```

### Проверка команды

```bash
command -V cd
#=> "cd is a function/alias/whatever"

```

### Ловушки ошибок

```bash
trap 'echo Error at about $LINENO' ERR

```

или же

```bash
traperr() {
  echo "ERROR: ${BASH_SOURCE[1]} at about ${BASH_LINENO[0]}"
}

set -o errtrace
trap traperr ERR

```

### Case/switch

```bash
case "$1" in
  start | up)
    vagrant up
    ;;

  *)
    echo "Usage: $0 {start|stop|ssh}"
    ;;
esac

```

### Source

```bash
source "${0%/*}/../share/foo.sh"

```

### printf

```bash
printf "Hello %s, I'm %s" Sven Olga
#=> "Hello Sven, I'm Olga

```

### Каталог скрипта

```bash
DIR="${0%/*}"

```

### Получение опций

```bash
while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
  -V | --version )
    echo $version
    exit
    ;;
  -s | --string )
    shift; string=$1
    ;;
  -f | --flag )
    flag=1
    ;;
esac; shift; done
if [[ "$1" == '--' ]]; then shift; fi

```

### Heredoc

```sh
cat <<END
hello world
END

```

### Чтение ввода

```bash
echo -n "Proceed? [y/n]: "
read ans
echo $ans

```

```bash
read -n 1 ans    # Только один символ

```

### Специальные переменные

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$?</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Значение выходного статуса (exit) последней задачи</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$!</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">PID последней фоновой задачи</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">PID оболочки</td></tr></tbody></table>

Смотрите [Специальные параметры](http://wiki.bash-hackers.org/syntax/shellvars#special_parameters_and_shell_variables).

### Перейти в предыдущий каталог

```bash
pwd # /home/user/foo
cd bar/
pwd # /home/user/foo/bar
cd -
pwd # /home/user/foo

```

## Смотрите также

*   [Bash-hackers wiki](http://wiki.bash-hackers.org/) _(bash-hackers.org)_
*   [Shell vars](http://wiki.bash-hackers.org/syntax/shellvars) _(bash-hackers.org)_
*   [Learn bash in y minutes](https://learnxinyminutes.com/docs/bash/) _(learnxinyminutes.com)_
*   [Bash Guide](http://mywiki.wooledge.org/BashGuide) _(mywiki.wooledge.org)_
*   [ShellCheck](https://www.shellcheck.net/) _(shellcheck.net)_
**********
[bash](/tags/bash.md)
