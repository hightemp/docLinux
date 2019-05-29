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

## [#](https://devhints.io/bash#loops)Loops

### Basic for loop

```bash
for i in /etc/rc.*; do
  echo $i
done

```

### C-like for loop

```bash
for ((i = 0 ; i < 100 ; i++)); do
  echo $i
done

```

### Ranges

```bash
for i in {1..5}; do
    echo "Welcome $i"
done

```

#### With step size

```bash
for i in {5..50..5}; do
    echo "Welcome $i"
done

```

### Reading lines

```bash
< file.txt | while read line; do
  echo $line
done

```

### Forever

```bash
while true; do
  ···
done

```

## [#](https://devhints.io/bash#functions)Functions

### Defining functions

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

### Returning values

```bash
myfunc() {
    local myresult='some value'
    echo $myresult
}

```

```bash
result="$(myfunc)"

```

### Raising errors

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

### Arguments

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$#</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Number of arguments</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$*</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">All arguments</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$@</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">All arguments, starting from first</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$1</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">First argument</td></tr></tbody></table>

See[Special parameters](http://wiki.bash-hackers.org/syntax/shellvars#special_parameters_and_shell_variables).

## [#](https://devhints.io/bash#conditionals)Conditionals

### Conditions

Note that`[[`is actually a command/program that returns either`0`(true) or`1`(false). Any program that obeys the same logic (like all base utils, such as`grep(1)`or`ping(1)`) can be used as condition, see examples.

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-top: 1px solid rgba(102, 119, 136, 0.05);"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -z STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Empty string</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -n STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Not empty string</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING == STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Equal</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING != STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Not Equal</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -eq NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Equal</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -ne NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Not equal</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -lt NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Less than</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -le NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Less than or equal</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -gt NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Greater than</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ NUM -ge NUM ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Greater than or equal</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ STRING =~ STRING ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Regexp</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">(( NUM &lt; NUM ))</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Numeric conditions</td></tr></tbody></table>

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-bottom-left-radius: 3px; border-bottom-right-radius: 3px; border-top: 1px solid rgba(102, 119, 136, 0.05);"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -o noclobber ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">If OPTIONNAME is enabled</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ ! EXPR ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Not</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ X ]] &amp;&amp; [[ Y ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">And</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ X ]] || [[ Y ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Or</td></tr></tbody></table>

### File conditions

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 378px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -e FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Exists</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -r FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Readable</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -h FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Symlink</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -d FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Directory</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -w FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Writable</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -s FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Size is &gt; 0 bytes</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -f FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">File</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ -x FILE ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Executable</td></tr></tbody><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.2);"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -nt FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">1 is more recent than 2</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -ot FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">2 is more recent than 1</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">[[ FILE1 -ef FILE2 ]]</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Same files</td></tr></tbody></table>

### Example

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

## [#](https://devhints.io/bash#arrays)Arrays

### Defining arrays

```bash
Fruits=('Apple' 'Banana' 'Orange')

```

```bash
Fruits[0]="Apple"
Fruits[1]="Banana"
Fruits[2]="Orange"

```

### Working with arrays

```bash
echo ${Fruits[0]}           # Element #0
echo ${Fruits[@]}           # All elements, space-separated
echo ${#Fruits[@]}          # Number of elements
echo ${#Fruits}             # String length of the 1st element
echo ${#Fruits[3]}          # String length of the Nth element
echo ${Fruits[@]:3:2}       # Range (from position 3, length 2)

```

### Operations

```bash
Fruits=("${Fruits[@]}" "Watermelon")    # Push
Fruits+=('Watermelon')                  # Also Push
Fruits=( ${Fruits[@]/Ap*/} )            # Remove by regex match
unset Fruits[2]                         # Remove one item
Fruits=("${Fruits[@]}")                 # Duplicate
Fruits=("${Fruits[@]}" "${Veggies[@]}") # Concatenate
lines=(`cat "logfile"`)                 # Read from file

```

### Iteration

```bash
for i in "${arrayName[@]}"; do
  echo $i
done

```

## [#](https://devhints.io/bash#dictionaries)Dictionaries

### Defining

```bash
declare -A sounds

```

```bash
sounds[dog]="bark"
sounds[cow]="moo"
sounds[bird]="tweet"
sounds[wolf]="howl"

```

Declares`sound`as a Dictionary object (aka associative array).

### Working with dictionaries

```bash
echo ${sounds[dog]} # Dog's sound
echo ${sounds[@]}   # All values
echo ${!sounds[@]}  # All keys
echo ${#sounds[@]}  # Number of elements
unset sounds[dog]   # Delete dog

```

### Iteration

#### Iterate over values

```bash
for val in "${sounds[@]}"; do
  echo $val
done

```

#### Iterate over keys

```bash
for key in "${!sounds[@]}"; do
  echo $key
done

```

## [#](https://devhints.io/bash#options)Options

### Options

```bash
set -o noclobber  # Avoid overlay files (echo "hi" > foo)
set -o errexit    # Used to exit upon error, avoiding cascading errors
set -o pipefail   # Unveils hidden failures
set -o nounset    # Exposes unset variables

```

### Glob options

```bash
set -o nullglob    # Non-matching globs are removed  ('*.foo' => '')
set -o failglob    # Non-matching globs throw errors
set -o nocaseglob  # Case insensitive globs
set -o globdots    # Wildcards match dotfiles ("*.sh" => ".foo.sh")
set -o globstar    # Allow ** for recursive matches ('lib/**/*.rb' => 'lib/a/b/c.rb')

```

Set`GLOBIGNORE`as a colon-separated list of patterns to be removed from glob matches.

## [#](https://devhints.io/bash#history)History

### Commands

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">history</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Show history</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">shopt -s histverify</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Don’t execute expanded result immediately</td></tr></tbody></table>

### Expansions

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand last parameter of most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!*</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand all parameters of most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!-n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code>th most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code>th command in history</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!&lt;command&gt;</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand most recent invocation of command<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;command&gt;</code></td></tr></tbody></table>

### Operations

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Execute last command again</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:s/&lt;FROM&gt;/&lt;TO&gt;/</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Replace first occurrence of<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;FROM&gt;</code><span>&nbsp;</span>to<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;TO&gt;</code><span>&nbsp;</span>in most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:gs/&lt;FROM&gt;/&lt;TO&gt;/</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Replace all occurrences of<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;FROM&gt;</code><span>&nbsp;</span>to<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">&lt;TO&gt;</code><span>&nbsp;</span>in most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$:t</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand only basename from last parameter of most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$:h</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand only directory from last parameter of most recent command</td></tr></tbody></table>

`!!`and`!$`can be replaced with any valid expansion.

### Slices

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand only<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code>th token from most recent command (command is<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">0</code>; first argument is<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">1</code>)</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!^</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand first argument from most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand last token from most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n-m</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand range of tokens from most recent command</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">!!:n-$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Expand<span>&nbsp;</span><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(102, 119, 136);">n</code>th token to last from most recent command</td></tr></tbody></table>

`!!`can be replaced with any valid expansion i.e.`!cat`,`!-2`,`!42`, etc.

## [#](https://devhints.io/bash#miscellaneous)Miscellaneous

### Numeric calculations

```bash
$((a + 200))      # Add 200 to $a

```

```bash
$((RANDOM%=200))  # Random number 0..200

```

### Subshells

```bash
(cd somedir; echo "I'm now in $PWD")
pwd # still in first directory

```

### Redirection

```bash
python hello.py > output.txt   # stdout to (file)
python hello.py >> output.txt  # stdout to (file), append
python hello.py 2> error.log   # stderr to (file)
python hello.py 2>&1           # stderr to stdout
python hello.py 2>/dev/null    # stderr to (null)
python hello.py &>/dev/null    # stdout and stderr to (null)

```

```bash
python hello.py < foo.txt      # feed foo.txt to stdin for python

```

### Inspecting commands

```bash
command -V cd
#=> "cd is a function/alias/whatever"

```

### Trap errors

```bash
trap 'echo Error at about $LINENO' ERR

```

or

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

### Source relative

```bash
source "${0%/*}/../share/foo.sh"

```

### printf

```bash
printf "Hello %s, I'm %s" Sven Olga
#=> "Hello Sven, I'm Olga

```

### Directory of script

```bash
DIR="${0%/*}"

```

### Getting options

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

### Reading input

```bash
echo -n "Proceed? [y/n]: "
read ans
echo $ans

```

```bash
read -n 1 ans    # Just one character

```

### Special variables

<table style="background-repeat: no-repeat; box-sizing: inherit; border-collapse: collapse; -webkit-font-smoothing: antialiased; width: 584px; border-top-left-radius: 3px; border-top-right-radius: 3px;"><tbody style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased;"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$?</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">Exit status of last task</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$!</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">PID of last background task</td></tr><tr style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; border-top: 1px solid rgba(102, 119, 136, 0.05);"><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: left; white-space: nowrap;"><code style="background-repeat: no-repeat; box-sizing: inherit; font-family: cousine, sfmono-regular, Consolas, Menlo, &quot;liberation mono&quot;, &quot;ubuntu mono&quot;, Courier, monospace; font-size: 0.96em; letter-spacing: -0.03em; color: rgb(51, 85, 170);">$$</code></td><td style="background-repeat: no-repeat; box-sizing: inherit; -webkit-font-smoothing: antialiased; padding: 8px 16px; vertical-align: top; text-align: right;">PID of shell</td></tr></tbody></table>

See[Special parameters](http://wiki.bash-hackers.org/syntax/shellvars#special_parameters_and_shell_variables).

### Go to previous directory

```bash
pwd # /home/user/foo
cd bar/
pwd # /home/user/foo/bar
cd -
pwd # /home/user/foo

```

## [#](https://devhints.io/bash#also-see)Also see

*   [Bash-hackers wiki](http://wiki.bash-hackers.org/)_(bash-hackers.org)_
*   [Shell vars](http://wiki.bash-hackers.org/syntax/shellvars)_(bash-hackers.org)_
*   [Learn bash in y minutes](https://learnxinyminutes.com/docs/bash/)_(learnxinyminutes.com)_
*   [Bash Guide](http://mywiki.wooledge.org/BashGuide)_(mywiki.wooledge.org)_
*   [ShellCheck](https://www.shellcheck.net/)_(shellcheck.net)_