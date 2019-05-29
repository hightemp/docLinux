# Операции сравнения

## сравнение целых чисел

* **\-eq**

	равно

	**if \[ "$a" -eq "$b" \]**

* **\-ne**

	не равно

	**if \[ "$a" -ne "$b" \]**

* **\-gt**

	больше

	**if \[ "$a" -gt "$b" \]**

* **\-ge**

	больше или равно

	**if \[ "$a" -ge "$b" \]**

* **\-lt**

	меньше

	**if \[ "$a" -lt "$b" \]**

* **\-le**

	меньше или равно

	**if \[ "$a" -le "$b" \]**

* **<**

	меньше (внутри [двойных круглых скобок](https://www.opennet.ru/docs/RUS/bash_scripting_guide/x4862.html))

	**(("$a" < "$b"))**

* **<=**

	меньше или равно (внутри двойных круглых скобок)

	**(("$a" <= "$b"))**

* **\>**

	больше (внутри двойных круглых скобок)

	**(("$a" > "$b"))**

* **\>=**

	больше или равно (внутри двойных круглых скобок)

	**(("$a" >= "$b"))**

## сравнение строк

\=

равно

**if \[ "$a" = "$b" \]**

\==

равно

**if \[ "$a" == "$b" \]**

Синоним оператора\=.

\[\[ $a == z\* \]\]    # истина, если $a начинается с символа "z" (сравнение по шаблону)
\[\[ $a == "z\*" \]\]  # истина, если $a равна z\*

\[ $a == z\* \]      # имеют место подстановка имен файлов и разбиение на слова
\[ "$a" == "z\*" \]  # истина, если $a равна z\*

# Спасибо S.C.

  
  

!=

не равно

**if \[ "$a" != "$b" \]**

Этот оператор используется при поиске по шаблону внутри[\[\[ ... \]\]](https://www.opennet.ru/docs/RUS/bash_scripting_guide/c2171.html#DBLBRACKETS).

<

меньше, в смысле величины ASCII-кодов

**if \[\[ "$a" < "$b" \]\]**

**if \[ "$a" \\< "$b" \]**

Обратите внимание! Символ"<"необходимо экранировать внутри**\[ \]**.

\>

больше, в смысле величины ASCII-кодов

**if \[\[ "$a" > "$b" \]\]**

**if \[ "$a" \\> "$b" \]**

Обратите внимание! Символ">"необходимо экранировать внутри**\[ \]**.

См.[Пример 25-6](https://www.opennet.ru/docs/RUS/bash_scripting_guide/c12790.html#BUBBLE)относительно применения этого оператора сравнения.

\-z

строка"пустая", т.е. имеет нулевую длину

\-n

строка не"пустая".

<table class="CAUTION" width="90%" border="0"><tbody><tr><td width="25" align="center" valign="top" style="font-size: 11pt;"><img src="https://www.opennet.ru/docs/RUS/bash_scripting_guide/misc/abs-book/images/caution.gif" hspace="5" alt="Caution"></td><td align="left" valign="top" style="font-size: 11pt;"><p>Оператор<span>&nbsp;</span><tt class="USERINPUT"><strong>-n</strong></tt><span>&nbsp;</span>требует, чтобы строка была заключена в кавычки внутри квадратных скобок. Как правило, проверка строк, не заключенных в кавычки, оператором<span>&nbsp;</span><tt class="USERINPUT"><strong>! -z</strong></tt>, или просто указание строки без кавычек внутри квадратных скобок (см.<span>&nbsp;</span><a href="https://www.opennet.ru/docs/RUS/bash_scripting_guide/x2565.html#STRTEST" style="text-decoration: none; color: rgb(96, 96, 144);">Пример 7-6</a>), проходит нормально, однако это небезопасная, с точки зрения отказоустойчивости, практика.<span>&nbsp;</span><span class="emphasis"><em class="EMPHASIS">Всегда</em></span><span>&nbsp;</span>заключайте проверяемую строку в кавычки.<span>&nbsp;</span><a name="AEN2722" href="https://www.opennet.ru/docs/RUS/bash_scripting_guide/x2565.html#FTN.AEN2722" style="text-decoration: none; color: rgb(96, 96, 144);"><span class="footnote">[1]</span></a></p></td></tr></tbody></table>