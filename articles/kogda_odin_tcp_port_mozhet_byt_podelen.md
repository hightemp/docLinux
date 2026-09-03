# Когда один TCP-порт может быть поделён

Источник: [Когда один TCP-порт может быть поделён](https://habr.com/ru/articles/725144/)

Вы замечали, как простые вопросы иногда приводят к сложным вопросам? Сегодня мы попытаемся подступиться к одному из таких вопросов. Категория — наша любимая: сетевые аспекты Linux.

## Когда два TCP-сокета могут разделять локальный адрес?

Если я перейду по ссылке <https://blog.cloudflare.com/>, мой браузер подключится к удалённому TCP-адресу, в данном случае это может быть 104.16.132.229:443. Подключение пойдёт с локального IP-адреса, присвоенного моей машине с Linux, через выбранный случайным образом локальный TCP-порт, скажем, 192.0.2.42:54321. Что произойдёт, если я затем решу отправиться на другой сайт? Возможно ли установить другое TCP-соединение с того же локального IP-адреса и порта?

Чтобы найти ответ на этот вопрос, давайте [выясним его опытным путём](https://en.wikipedia.org/wiki/Discovery_learning). Мы подготовили для вас восемь вопросов-задачек. Ответив на каждый из них, вы откроете для себя один из аспектов тех правил, что регулируют разделение локальных адресов между TCP-сокетами под Linux. Честно предупреждаем: от этого материала может зайти ум за разум.

Вопросы разделены на две группы в зависимости от тестового сценария:

![](/images/879e965bc45630210829bbe124dff1a3.png)

В первом сценарии два сокета подключаются с одного и того же локального порта на одни и те же удалённые IP и порт. Однако локальный IP для обоих сокетов отличается.

В свою очередь, во втором сценарии локальный IP и порт одинаковы для всех сокетов, но отличается удалённый адрес или, в сущности, только IP-адрес.

Отвечая на поставленные вопросы, мы будем делать одно из двух:

1\. Позволять ОС автоматически выбирать локальный IP и/или порт для сокета или

2\. Явно присваивать локальный адрес при помощи [bind()](https://man7.org/linux/man-pages/man2/bind.2.html), прежде чем подключиться ([connect()](https://man7.org/linux/man-pages/man2/connect.2.html)) к сокету; такой метод также называется [bind-before-connect](https://idea.popcount.org/2014-04-03-bind-before-connect/).

Поскольку мы будем исследовать пограничные случаи, связанные с логикой `bind()`, нам нужно каким-то способом исчерпать все локальные адреса, то есть пары (IP, порт). Можно было бы банально создать много сокетов, но проще было бы [подкрутить конфигурацию системы](https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html?#ip-variables) и предположить, что на машине есть всего один локальный эфемерный порт, который ОС может присваивать сокетам:

```text
sysctl -w net.ipv4.ip_local_port_range='60000 60000'
```

В каждом вопросе-загадке вас ждёт краткий листинг на Python. Ваша задача — спрогнозировать, каков будет итог выполнения кода. Выполнится ли код успешно? Или нет? Спрашивать ChatGPT не разрешается ?.

Всегда есть процедура настройки кода, о которой просто нужно помнить. Для краткости мы исключим её из наших фрагментов кода:

```text
from os import system
from socket import *

# Недостающие константы
IP_BIND_ADDRESS_NO_PORT = 24

# В пространстве имён нашей сети всего *один* эфемерный порт
system("sysctl -w net.ipv4.ip_local_port_range='60000 60000'")

# Открываем слушающий сокет по *:1234. Именно к нему будем подключаться.
ln = socket(AF_INET, SOCK_STREAM)
ln.bind(("", 1234))
ln.listen(SOMAXCONN)
```

Избавившись от этих формальностей, начнём. На старт, внимание, марш!

## Сценарий #1: Когда локальный IP уникален, но локальный порт не меняется

В сценарии #1 мы подключаем два сокета к одному и тому же удалённому адресу: 127.9.9.9:1234. Эти сокеты будут использовать отличающиеся локальные IP-адреса, но достаточно ли этого для разделения локального порта?

Локальный IP| Локальный порт| Удалённый IP| Удалённый порт
---|---|---|---
уникальный| одинаковый| одинаковый| Одинаковый
127.0.0.1
127.1.1.1
127.2.2.2| 60_000| 127.9.9.9| 1234

## Загадка #1

На стороне локальной машины привязываем два сокета к разным, явно указанным IP-адресам. Позволяем ОС выбирать локальный порт. Помните: в диапазоне локальных эфемерных портов на нашей машине содержится всего один порт (60 000).

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.1.1.1', 0))
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.2.2.2', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #1](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_1.py)

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #1
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.bind(('127.1.1.1', 0))
>>> s1.connect(('127.9.9.9', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.1.1.1', 60000), ('127.9.9.9', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.bind(('127.2.2.2', 0))
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.2.2.2', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local port is shared.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #2

Здесь постановка такая же, как и в предыдущей загадке. Однако мы запрашиваем ОС выбрать локальный IP-адрес и порт для первого сокета. Как вы думаете, результат будет отличаться от полученного в предыдущей загадке?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.2.2.2', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #2](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_2.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #2
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.connect(('127.9.9.9', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.bind(('127.2.2.2', 0))
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.2.2.2', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local port is shared.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #3

Загадка сформулирована точно, как и предыдущая. Мы просто поменяли порядок. Сначала мы подключаемся к сокету с явно указанного локального адреса. Затем приказываем системе выбрать для нас локальный адрес. Очевидно, при таком изменении порядка действий никаких изменений произойти не должно, верно?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.1.1.1', 0))
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #3](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_3.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #3
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.bind(('127.1.1.1', 0))
>>> s1.connect(('127.9.9.9', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.1.1.1', 60000), ('127.9.9.9', 1234))

>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.connect(('127.9.9.9', 1234))
Traceback (most recent call last):
  ...
OSError: [Errno 99] Cannot assign requested address

Outcome: FAILURE. Local port can't be shared.

Cleanup:

>>> p1, _ = ln.accept()
>>> p1.close() # TIME-WAIT on server side
>>> s1.close()
>>> s2.close()

Solution #3
-----------

Use `IP_BIND_ADDRESS_NO_PORT` socket option.

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_IP, IP_BIND_ADDRESS_NO_PORT, 1)
>>> s1.bind(('127.1.1.1', 0))
>>> s1.connect(('127.9.9.9', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.1.1.1', 60000), ('127.9.9.9', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local port is shared when using `IP_BIND_ADDRESS_NO_PORT` option.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Сценарий #2: когда локальный IP и порт одинаковы, но удалённый IP отличается

В сценарии #2 рассмотрим обратную постановку. Теперь у нас будет не множество локальных IP и один удалённый адрес, а один локальный адрес `127.0.0.1:60000` и два разных удалённых адреса. Всё тот же вопрос: могут ли два сокета совместно использовать локальный порт? Напоминаю: диапазон эфемерных портов у нас по-прежнему равен единице.

Локальный IP| Локальный порт| Удалённый IP| Удалённый порт
---|---|---|---
одинаковый| одинаковый| уникальный| одинаковый
127.0.0.1| 60_000| 127.8.8.8
127.9.9.9| 1234

## Загадка #4

Начнём с азов. Мы подключаемся (connect()) к двум разным удалённым адресам. Это для затравки ?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #4](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_4.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #4
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local (IP, port) is shared.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #5

Что если явно связаться (`bind()`) с локальным IP, но позволить ОС самой выбрать порт — изменится ли от этого что-либо?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.0.0.1', 0))
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.0.0.1', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #5](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_5.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #5
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.bind(('127.0.0.1', 0))
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.bind(('127.0.0.1', 0))
Traceback (most recent call last):
  ...
OSError: [Errno 98] Address already in use
>>>

Outcome: FAILURE. Local (IP, port) can't be shared.

Cleanup:

>>> p1, _ = ln.accept()
>>> p1.close() # TIME-WAIT on server side
>>> s1.close()
>>> s2.close()

Solution #5
-----------

Use `IP_BIND_ADDRESS_NO_PORT` socket option.

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_IP, IP_BIND_ADDRESS_NO_PORT, 1)
>>> s1.bind(('127.0.0.1', 0))
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.setsockopt(SOL_IP, IP_BIND_ADDRESS_NO_PORT, 1)
>>> s2.bind(('127.0.0.1', 0))
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local (IP, port) is shared when using `IP_BIND_ADDRESS_NO_PORT`.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #6

На этот раз мы явно укажем локальный адрес и порт. Иногда необходимо указывать локальный порт.

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.0.0.1', 60_000))
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.0.0.1', 60_000))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #6](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_6.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #6
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.bind(('127.0.0.1', 60_000))
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.bind(('127.0.0.1', 60_000))
Traceback (most recent call last):
  ...
OSError: [Errno 98] Address already in use
>>>

Outcome: FAILURE. Local (IP, port) can't be shared.

Cleanup:

>>> p1, _ = ln.accept()
>>> p1.close() # TIME-WAIT on server side
>>> s1.close()
>>> s2.close()
>>>

Solution #6
-----------

Use `SO_REUSEADDR` socket option.

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s1.bind(('127.0.0.1', 60_000))
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s2.bind(('127.0.0.1', 60_000))
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local (IP, port) is shared when using `SO_REUSEADDR`.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #7

На случай, если вы полагали, что страннее быть уже не может — давайте добавим в эту смесь [SO_REUSEADDR](https://manpages.debian.org/unstable/manpages/socket.7.en.html#SO_REUSEADDR).

Сперва запрашиваем ОС, чтобы она выделила для нас локальный адрес. Затем явно свяжемся с тем же локальным адресом, который, как мы уже знаем, ОС обязана была присвоить первому сокету. Мы включим возможность переиспользовать локальный адрес для обоих сокетов. Это разрешено?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s2.bind(('127.0.0.1', 60_000))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #7](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_7.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #7
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s1.connect(('127.8.8.8', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.8.8.8', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s2.bind(('127.0.0.1', 60_000))
>>> s2.connect(('127.9.9.9', 1234))
>>> s2.getsockname(), s2.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>

Outcome: SUCCESS. Local (IP, port) is shared.

Cleanup:

>>> s1.close()
>>> s2.close()
"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

## Загадка #8

Наконец, вишенка на торте. Эта загадка — точно как и #7, но наоборот. Здравый смысл не оставляет сомнений, что ответ должен быть точно как в #7, но так ли это?

```text
s1 = socket(AF_INET, SOCK_STREAM)
s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s1.bind(('127.0.0.1', 60_000))
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s2.connect(('127.8.8.8', 1234))
s2.getsockname(), s2.getpeername()
```

А ВОТ [Ответ #8](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_8.py).

```text
#!/usr/bin/env -S unshare --user --map-root-user --net -- strace -e %net -- python

"""
Quiz #8
-------

>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s1.bind(('127.0.0.1', 60_000))
>>> s1.connect(('127.9.9.9', 1234))
>>> s1.getsockname(), s1.getpeername()
(('127.0.0.1', 60000), ('127.9.9.9', 1234))
>>>
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s2.connect(('127.8.8.8', 1234))
Traceback (most recent call last):
  ...
OSError: [Errno 99] Cannot assign requested address
>>>

Outcome: FAILURE. Local (IP, port) can't be shared.

Cleanup:

>>> s1.close()
>>> s2.close()

Solution #8
-----------

There is NONE.

"""

from quiz_common import run_doctest
from socket import *

if __name__ == "__main__":
    run_doctest(__name__)
```

**Тайная жизнь локального TCP-порта в трёх состояниях**

Сейчас всё понятно? Мы как будто занимаемся обратной разработкой чёрного ящика. Пожалуй, ничего не понятно, как и должно быть при обратной разработке чёрного ящика. Так что же происходит за кулисами? Давайте туда заглянем.

Linux отслеживает все находящиеся в использовании TCP-**порты** в хеш-таблице, которая называется [bhash](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L166). Не перепутайте её с таблицей [ehash](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L156); в ней отслеживаются **сокеты** , которым уже присвоены как локальные, так и удалённые адреса.

![](/images/712817ad2424da917f8b27c0be4f42ea.png)

Каждая запись в хеш-таблице указывает на цепочку так называемых «корзин привязки» (bind bucket). В такой корзине группируются сокеты, совместно использующие один локальный порт. Точнее говоря, сокеты группируются в корзины по следующим признакам:

  * Сетевое [пространство имён,](https://man7.org/linux/man-pages/man7/network_namespaces.7.html) к которым они относятся и

  * Устройство [VRF](https://docs.kernel.org/networking/vrf.html), с которым они связаны, и

  * Номер локального порта, с которым они связаны.

Но простейшая возможная конфигурация — всего одно сетевое пространство имён, никаких VRF; можно сказать, что сокеты сгруппированы в корзине привязки по соответствующему им локальному номеру порта.

Набор сокетов в каждой корзине привязки, совместно использующих локальный порт, подкрепляется связным списком именованных обладателей.

Когда мы приказываем ядру присвоить локальный адрес сокету, наша задача
— проверить, не возникает ли конфликт с каким-либо существующим сокетом. Дело в
том, что разделять номер локального порта можно лишь при соблюдении [определённых условий](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L43):

```c
/* Есть несколько простых правил, следуя которым можно переиспользовать локальный порт
 * в приложении.  В сущности:
 *
 *   1) Сокеты, связанные с разными интерфейсами, могут совместно использовать локальный порт
 *      Если это условие не выполняется – переход к тесту 2.
 *   2) Если у всех сокетов есть набор sk->sk_reuse, и ни один из них не находится в состоянии
 *      TCP_LISTEN, допускается совместное использование порта.
 *      Если это условие не выполняется – переход к тесту 3.
 *   3) Если все сокеты связаны с конкретным локальным адресом inet_sk(sk)->rcv_saddr, и
 * одинаковых среди них нет, то допускается совместное использование порта
 *      Если это условие не выполняется, то порт совместно использовать нельзя.
 *
 * Здесь наиболее интересен тест #2.  Именно этим весь день и занимается FTP-сервер.
 * Чтобы оптимизировать этот случай, мы используем конкретный флаговый бит, определённый ниже.
 * Добавляя сокеты в список корзины привязки, мы проверяем:
 * (newsk->sk_reuse && (newsk->sk_state != TCP_LISTEN))
 * В случае, если все сокеты из корзины привязки пройдут этот тест,
 * будет установлен флаговый бит.
 * ...
 */
```

Как следует из вышеприведённого комментария, ядро оптимизирует код в расчёте на оптимистичный случай: конфликта нет. По окончании манипуляций корзина привязки содержит дополнительное состояние, в котором агрегированы свойства сокетов, содержащихся в этой корзине:

```c
struct inet_bind_bucket {
        /* ... */
        signed char          fastreuse;
        signed char          fastreuseport;
        kuid_t               fastuid;
#if IS_ENABLED(CONFIG_IPV6)
        struct in6_addr      fast_v6_rcv_saddr;
#endif
        __be32               fast_rcv_saddr;
        unsigned short       fast_sk_family;
        bool                 fast_ipv6_only;
        /* ... */
};
```

Давайте обратим внимание только на первое совокупное свойство — fastreuse. Оно существует в Linux со времён ныне доисторической версии 2.1.90pre1. Как указано в комментарии, исходно в форме [флагового бита](https://git.kernel.org/pub/scm/linux/kernel/git/history/history.git/tree/include/net/tcp.h?h=2.1.90pre1&id=9d11a5176cc5b9609542b1bd5a827b8618efe681#n76), а в процессе развития он превратился в поле, размер которого определяется в байтах.

Остальные шесть полей появились гораздо позже с введением [SO_REUSEPORT в Linux 3.9](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=da5e36308d9f7151845018369148201a5d28b46d). Ведь они играют роль только при наличии сокетов, у которых установлен флаг [SO_REUSEPORT](https://manpages.debian.org/unstable/manpages/socket.7.en.html#SO_REUSEPORT). В рамках этой статьи мы их проигнорируем.

Всякий раз, когда ядру Linux требуется привязать сокет к локальному порту, сначала нужно поискать корзину привязки для этого порта. Нам несколько усложняет жизнь следующий аспект: поиск TCP-корзины привязки в ядре осуществляется в двух точках ядра. Поиск корзины привязки может осуществляться заранее, во время`bind()` , или поздно, во время `connect()`. Которая из этих функций будет вызвана — зависит от того, как именно был настроен подключённый сокет:

![](/images/f9cf8728bbccfe6ff05879aa99aad6b2.png)

Однако, оказываясь в [inet_csk_get_port](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L486) или [__inet_hash_connect](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_hashtables.c#L992), нам всегда приходится обходить цепочку корзин в bhash, подыскивая корзину с совпадающим номером порта. Такая корзина может уже существовать, либо нам предварительно придётся её создать. Но, когда она возникнет, её поле fastreuse окажется в одном из трёх возможных состояний. Это -1, 0 или +1. Создаётся впечатление, будто Linux-разработчики вдохновлялись [квантовой механикой](https://en.wikipedia.org/wiki/Triplet_state).

Состояние отражает два аспекта корзины привязки:

1\. Какие сокеты находятся в корзине?

2\. Когда возможно совместное использование локального порта?

Поэтому давайте попробуем расшифровать три возможных состояния fastreuse и посмотрим, что они означают в каждом из случаев.

Во-первых, что нам говорит свойство fastreuse о владельцах корзины, то есть о сокетах, использующих данный локальный порт?

Значение fastreuse | В списке владельцев содержатся
---|---
-1| Сокеты, подключённые (`connect()`) из эфемерного порта
0| Сокеты, привязанные без `SO_REUSEADDR`
+1| Сокеты, привязанные с `SO_REUSEADDR`

Это, конечно, не вся, но почти вся правда. Вскоре мы доберёмся до сути.

Когда же дело доходит до совместного использования портов, ситуация получается гораздо менее прямолинейной:

Можно ли, … когда …| fastreuse = -1| fastreuse = 0| fastreuse = +1
---|---|---|---
Связаться (bind()) с тем же самым портом (эфемерным или указанным)| **Да,** тогда и только тогда, когда локальный IP уникален ①| ← [idem](https://en.wiktionary.org/wiki/idem#Pronoun)| ← idem
Связаться (bind()) с конкретным портом при помощи SO_REUSEADDR| **Да,** тогда и только тогда, когда локальный IP уникален ИЛИ конфликтующий сокет использует SO_REUSEADDR ①| ← idem| **да** ②
Подсоединиться (connect()) с того же эфемерного порта к тому же удалённому (IP, порту)| **Да,** тогда и только тогда, когда локальный IP уникален ③| **нет** ③| **нет** ③
Подсоединиться (connect()) с того же эфемерного порта к уникальному удалённому (IP, порту)| **да** ③| **нет** ③| **нет** ③

① Определяется в зависимости от [inet_csk_bind_conflict()](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L214), вызываемой из `inet_csk_get_port()` (привязка к конкретному порту) или `inet_csk_get_port()` → `inet_csk_find_open_port()` (привязка к эфемерному порту).

② Поскольку `inet_csk_get_port()` [пропускает проверку конфликтов](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L531) для fastreuse == 1 buckets.

③ Поскольку `inet_hash_connect()` → `__inet_hash_connect()` [пропускает корзины](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_hashtables.c#L1062) с fastreuse != -1.

Притом, что на первый взгляд всё это выглядит довольно сложно, вышеприведённая таблица вполне сводима к двум утверждениям, которые должны быть верными — в таком виде она воспринимается немного проще:

  * `bind()` или раннее выделение локального адреса всегда проходит успешно при отсутствии каких-либо конфликтов между локальным IP-адресом и каким-либо из существующих сокетов,

  * `connect()` или позднее выделение локального адреса всегда оканчивается неудачей в случае, если корзина TCP-привязки для локального порта находится в любом состоянии, кроме fastreuse = -1,

  * `connect()` оканчивается успехом только при отсутствии каких-либо конфликтов между локальными и удалёнными адресами,

  * сокетная опция `SO_REUSEADDR` обеспечивает совместное использование локальных адресов, если эта опция также используется всеми конфликтующими сокетами (и ни один из них не находится в состоянии слушателя).

## Это безумие. Я вам не верю

К счастью, вы и не обязаны. При помощи программируемого отладчика [drgn](https://drgn.readthedocs.io/en/latest/index.html) можно проверить состояние корзины привязки прямо в действующем ядре:

```text
#!/usr/bin/env drgn

"""
dump_bhash.py - List all TCP bind buckets in the current netns.

Script is not aware of VRF.
"""
```

```python
import os
```

```text
from drgn.helpers.linux.list import hlist_for_each, hlist_for_each_entry
from drgn.helpers.linux.net import get_net_ns_by_fd
from drgn.helpers.linux.pid import find_task
```

```python
def dump_bind_bucket(head, net):
    for tb in hlist_for_each_entry("struct inet_bind_bucket", head, "node"):
        # Пропустить корзины не из этой сети
        if tb.ib_net.net != net:
            continue
```

```text
        port = tb.port.value_()
        fastreuse = tb.fastreuse.value_()
        owners_len = len(list(hlist_for_each(tb.owners)))
```

```python
        print(
            "{:8d}  {:{sign}9d}  {:7d}".format(
                port,
                fastreuse,
                owners_len,
                sign="+" if fastreuse != 0 else " ",
            )
        )
```

```python
def get_netns():
    pid = os.getpid()
    task = find_task(prog, pid)
    with open(f"/proc/{pid}/ns/net") as f:
        return get_net_ns_by_fd(task, f.fileno())
```

```python
def main():
    print("{:8}  {:9}  {:7}".format("TCP-PORT", "FASTREUSE", "#OWNERS"))
```

```text
    tcp_hashinfo = prog.object("tcp_hashinfo")
    net = get_netns()

    # Перебрать все слоты bhash
    for i in range(0, tcp_hashinfo.bhash_size):
        head = tcp_hashinfo.bhash[i].chain
        # Перебрать корзины привязки в слоте
        dump_bind_bucket(head, net)

main()
```

Давайте испробуем [этот скрипт](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/dump_bhash.py) и попробуем подтвердить вещи, подаваемые в _таблице 1_ как истинные. Учитывайте, что для получения приведённых ниже сеансовых сниппетов ipython --classic я пользовался той же конфигурацией, которая делалась для ответов на загадки.

Два подключённых сокета совместно используют эфемерный порт 60 000:

```text
>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.connect(('127.1.1.1', 1234))
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.connect(('127.2.2.2', 1234))
>>> !./dump_bhash.py
TCP-PORT  FASTREUSE  #OWNERS
    1234          0        3
   60000         -1        2
>>>
```

Два привязанных сокета повторно используют порт 60 000:

```text
>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s1.bind(('127.1.1.1', 60_000))
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s2.bind(('127.1.1.1', 60_000))
>>> !./dump_bhash.py
TCP-PORT  FASTREUSE  #OWNERS
    1234          0        1
   60000         +1        2
>>>
```

Смесь привязанных сокетов с активированной и активированной опцией REUSEADDR совместно использует порт 60 000:

```text
>>> s1 = socket(AF_INET, SOCK_STREAM)
>>> s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
>>> s1.bind(('127.1.1.1', 60_000))
>>> !./dump_bhash.py
TCP-PORT  FASTREUSE  #OWNERS
    1234          0        1
   60000         +1        1
>>> s2 = socket(AF_INET, SOCK_STREAM)
>>> s2.bind(('127.2.2.2', 60_000))
>>> !./dump_bhash.py
TCP-PORT  FASTREUSE  #OWNERS
    1234          0        1
   60000          0        2
>>>
```

Если работать с такими инструментами, то чтобы доказать истинность информации, содержащейся в _таблице 2_ , требуется всего лишь написать комплект [исследовательских тестов](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse.py).

Но что произошло в последнем сниппете? Корзина привязки явно перешла из одного состояния fastreuse в другое. Именно это упускается в _таблице 1_. И это означает, что полной картины происходящего мы себе по-прежнему не представляем.

Нам ещё предстоит выяснить, когда именно может измениться состояние fastreuse у корзины. Здесь явно требуется конечный автомат.

## Конечный автомат

Как мы только что могли убедиться, корзине привязки не требуется на протяжении всего жизненного цикла оставаться в исходном состоянии fastreuse. Добавление сокетов в корзину может спровоцировать изменение состояния. Оказывается, возможен переход только в состояние fastreuse = 0, если нам доведётся привязать (`bind()`) сокет, который:

1\. не конфликтует с уже имеющимися владельцами и

2\. у него не включена опция SO_REUSEADDR.

![](/images/e0a0c02c771428cbd4d64f8ab605fb9b.png)

Притом, что мы могли бы выяснить всё это, внимательно прочитав код в [inet_csk_get_port → inet_csk_update_fastreuse](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L431), нам определённо не повредило бы подкрепить то, что мы уже поняли, и для этого нужно провести [ещё несколько тестов](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse_states.py).

Теперь, когда мы смогли восстановить полную картину, напрашивается вопрос…

## Зачем вы мне всё это рассказываете?

Во-первых, на случай, когда в следующий раз системный вызов `bind()` отклонит ваш запрос с мотивацией `EADDRINUSE`, или `connect()` упрётся, выдав ошибку `EADDRNOTAVAIL` : чтобы вы знали, что происходит, или, как минимум, обладали инструментарием, позволяющим это выяснить.

Во-вторых, поскольку ранее мы [рекламировали, как можно](https://blog.cloudflare.com/how-to-stop-running-out-of-ephemeral-ports-and-start-to-love-long-lived-connections/) открывать соединения из конкретного набора портов. Такая практика сопряжена с привязкой сокетов, у которых выставлена опция `SO_REUSEADDR`. Тогда мы ещё не осознавали, что существует [пограничный случай](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse.py#L300), в котором порт не поддаётся совместному использованию обычными сокетами, подключёнными при помощи connect(). Притом, что это погоды не делает, важно понимать потенциальные последствия.

Чтобы поправить ситуацию, мы совместно с сообществом Linux надстроили в API ядра новую сокетную опцию, позволяющую пользователю [указать диапазон локальных портов](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=91d0b78c5177). Ожидается, что новая опция будет доступна в готовящейся к выходу новой версии Linux 6.3. Имея такую опцию, мы сможем больше не прибегать к уловкам с `bind()`. Опять же, так открывается возможность разделять локальный порт между сокетами, подключёнными при помощи обычного `connect()`.

## Заключительные мысли

В этой статье был сформулирован относительно прямолинейный вопрос — в каких случаях два TCP-сокета могут совместно использовать локальный адрес? — после чего был проработан путь к ответу. Этот ответ настолько сложен, что в одном предложении его не выразить. Более того, это даже не полный ответ. В конце концов, мы решили проигнорировать фичу `SO_REUSEPORT`, а также не рассматривали конфликтов, в которые вовлечены слушающие TCP-сокеты.

Если из этого исследования и есть простой вывод, то вот он: привязывая сокет при помощи bind(), можно нарваться на коварные последствия. При использовании `bind()` для выбора исходящего IP-адреса лучше всего сочетать этот выбор с сокетной опцией `IP_BIND_ADDRESS_NO_PORT`, а присваивание портов оставить ядру. В противном случае можно непреднамеренно перекрыть возможность переиспользования локальных TCP-портов.

Прискорбно, что этот совет неприменим к UDP, где `IP_BIND_ADDRESS_NO_PORT` на настоящий момент, в сущности, не работает. Но это уже другая история.

До новых встреч ?.

**********

[Linux](/tags/linux.md)
[sockets](/tags/sockets.md)
