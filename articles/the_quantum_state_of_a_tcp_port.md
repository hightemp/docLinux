# Квантовое состояние TCP-порта

Источник: [The quantum state of a TCP port](https://blog.cloudflare.com/the-quantum-state-of-a-tcp-port/)

Jakub Sitnicki · 20 марта 2023 · 11 мин

Вы замечали, как простые вопросы иногда приводят к сложным ответам? Сегодня мы разберём один из таких вопросов. Категория: наш любимая — сеть в Linux.

## Когда два TCP-сокета могут использовать один локальный адрес?

Если я перейду на [https://blog.cloudflare.com/](/), мой браузер подключится к удалённому TCP-адресу — в данном случае это может быть 104.16.132.229:443 — с локального IP-адреса, назначенного моей Linux-машине, и случайно выбранным локальным TCP-портом, скажем 192.0.2.42:54321. Что произойдёт, если я затем решу отправиться на другой сайт? Возможно ли установить ещё одно TCP-соединение с того же локального IP-адреса и порта?

Чтобы найти ответ, давайте займёмся [обучением через открытие](https://en.wikipedia.org/wiki/Discovery_learning). Мы подготовили восемь вопросов викторины. Каждый позволит вам открыть один аспект правил, управляющих совместным использованием локальных адресов TCP-сокетами в Linux. Сразу предупреждаю: может слегка взорвать мозг.

Вопросы разделены на две группы по тестовому сценарию:

![image](/images/ff606eb3168f7546ecc8d5dc824af1d2.png)

В первом тестовом сценарии два сокета подключаются с одного и того же локального порта к одному и тому же удалённому IP и порту. Однако локальный IP у каждого сокета свой.

Во втором же сценарии локальный IP и порт одинаковы для всех сокетов, но удалённый адрес — точнее, просто IP-адрес — различается.

В наших вопросах викторины мы либо:

  1. позволяем ОС автоматически выбирать локальный IP и/или порт для сокета, либо
  2. явно назначаем локальный адрес с помощью [`bind()`](https://man7.org/linux/man-pages/man2/bind.2.html) перед [`connect()`](https://man7.org/linux/man-pages/man2/connect.2.html)-ом сокета — метод, также известный как [bind-before-connect](https://idea.popcount.org/2014-04-03-bind-before-connect/).

Поскольку мы будем исследовать угловые случаи логики bind(), нам нужен способ исчерпать доступные локальные адреса, то есть пары (IP, порт). Мы могли бы просто создать кучу сокетов, но будет проще [подкрутить конфигурацию системы](https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html?#ip-variables) и притвориться, что есть всего один эфемерный локальный порт, который ОС может назначать сокетам:

```bash
sysctl -w net.ipv4.ip_local_port_range='60000 60000'
```

Каждый вопрос викторины — короткий фрагмент на Python. Ваша задача — предсказать результат выполнения кода. Удаётся? Падает? Если падает, то что именно? Спрашивать ChatGPT не разрешается ?

Всегда есть общая процедура настройки, которую нужно держать в уме. Мы опустим её во фрагментах викторины, чтобы сохранить их краткость:

```python
from os import system
from socket import *

# Missing constants
IP_BIND_ADDRESS_NO_PORT = 24

# Our network namespace has just *one* ephemeral port
system("sysctl -w net.ipv4.ip_local_port_range='60000 60000'")

# Open a listening socket at *:1234. We will connect to it.
ln = socket(AF_INET, SOCK_STREAM)
ln.bind(("", 1234))
ln.listen(SOMAXCONN)
```

С формальностями покончено, начнём. Внимание. Марш. Вперёд!

### Сценарий #1: когда локальный IP уникален, но локальный порт одинаков

В сценарии #1 мы подключаем два сокета к одному и тому же удалённому адресу — 127.9.9.9:1234. Сокеты будут использовать разные локальные IP-адреса, но достаточно ли этого для совместного использования локального порта?

локальный IP | локальный порт | удалённый IP | удалённый порт
---|---|---|---
уникален | одинаков | одинаков | одинаков
127.0.0.1
127.1.1.1
127.2.2.2 | 60_000 | 127.9.9.9 | 1234

### Викторина #1

На локальной стороне мы биндим два сокета на разные, явно указанные IP-адреса. Мы позволим ОС выбрать локальный порт. Помните: наш диапазон локальных эфемерных портов содержит всего один порт (60 000).

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.1.1.1', 0))
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.2.2.2', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #1](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_1.py)

### Викторина #2

Здесь настройка почти идентична предыдущей. Однако для первого сокета мы просим ОС выбрать и локальный IP-адрес, и порт. Думаете, результат будет отличаться от предыдущего вопроса?

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.2.2.2', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #2](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_2.py)

### Викторина #3

Этот вопрос — такой же, как предыдущий. Мы просто изменили порядок. Сначала мы подключаем сокет с явно указанного локального адреса. Затем просим систему выбрать локальный адрес за нас. Очевидно, такое изменение порядка ничего не меняет, верно?

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.1.1.1', 0))
s1.connect(('127.9.9.9', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #3](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_3.py)

### Сценарий #2: когда локальный IP и порт одинаковы, но удалённый IP различается

В сценарии #2 мы переворачиваем настройку. Вместо нескольких локальных IP и одного удалённого адреса, теперь у нас один локальный адрес `127.0.0.1:60000` и два разных удалённых адреса. Вопрос остаётся тем же — могут ли два сокета использовать один локальный порт? Напоминание: диапазон эфемерных портов всё ещё состоит из одного порта.

локальный IP | локальный порт | удалённый IP | удалённый порт
---|---|---|---
одинаков | одинаков | уникален | одинаков
127.0.0.1 | 60_000 | 127.8.8.8
127.9.9.9 | 1234

### Викторина #4

Начнём с основ. Мы `connect()`-имся к двум разным удалённым адресам. Это разминка ?

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #4](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_4.py)

### Викторина #5

А что если мы явно `bind()`-имся к локальному IP, но позволим ОС выбрать порт — что-нибудь меняется?

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.0.0.1', 0))
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.0.0.1', 0))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #5](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_5.py)

### Викторина #6

На этот раз мы явно указываем и локальный адрес, и локальный порт. Иногда есть необходимость указать локальный порт.

```python
s1 = socket(AF_INET, SOCK_STREAM)
s1.bind(('127.0.0.1', 60_000))
s1.connect(('127.8.8.8', 1234))
s1.getsockname(), s1.getpeername()

s2 = socket(AF_INET, SOCK_STREAM)
s2.bind(('127.0.0.1', 60_000))
s2.connect(('127.9.9.9', 1234))
s2.getsockname(), s2.getpeername()
```

ПЕРЕЙТИ к [ответу #6](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_6.py)

### Викторина #7

Казалось бы, страннее уже некуда, но мы добавляем [`SO_REUSEADDR`](https://manpages.debian.org/unstable/manpages/socket.7.en.html#SO_REUSEADDR) в смесь.

Сначала мы просим ОС выделить локальный адрес для нас. Затем мы явно биндимся на тот же локальный адрес, который, как мы знаем, ОС назначила первому сокету. Мы включаем переиспользование локального адреса для обоих сокетов. Разрешено ли это?

```python
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

ПЕРЕЙТИ к [ответу #7](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_7.py)

### Викторина #8

Наконец, вишенка на торте. Это викторина #7, но наоборот. Здравый смысл диктует, что результат должен быть тем же, но так ли это?

```python
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

ПЕРЕЙТИ к [ответу #8](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/quiz_8.py)

## Тайная трёхзначная жизнь локального TCP-порта

Всё ли теперь ясно? Ну, скорее всего нет. Ощущение, будто реверс-инжинирим чёрный ящик. Так что же происходит за кулисами? Давайте посмотрим.

Linux отслеживает все используемые TCP-**порты** в хеш-таблице с именем [bhash](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L166). Не путать с таблицей [ehash](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L156), которая отслеживает **сокеты**, у которых уже назначены и локальный, и удаленный адрес.

![image](/images/af798bb1802b1eea5378eeb5ce82678e.png)

Каждый элемент хеш-таблицы указывает на цепочку так называемых bind-бакетов (bind buckets), которые группируют сокеты, использующие один локальный порт. Точнее, сокеты группируются в бакеты по:

  * [сетевому пространству имён](https://man7.org/linux/man-pages/man7/network_namespaces.7.html), которому они принадлежат, и
  * устройству [VRF](https://docs.kernel.org/networking/vrf.html), к которому они привязаны, и
  * номеру локального порта, к которому они привязаны.

Но в простейшей возможной настройке — одно сетевое пространство имён, без VRF — можно сказать, что сокеты в bind-бакете группируются по номеру локального порта.

Набор сокетов в каждом bind-бакете, то есть использующих один локальный порт, поддерживается связным списком с именем owners.

Когда мы просим ядро назначить сокету локальный адрес, его задача — проверить конфликт с любым существующим сокетом. Это потому, что номер локального порта может использоваться совместно только [при определённых условиях](https://elixir.bootlin.com/linux/v6.2/source/include/net/inet_hashtables.h#L43):

```c
/* There are a few simple rules, which allow for local port reuse by
 * an application.  In essence:
 *
 *   1) Sockets bound to different interfaces may share a local port.
 *      Failing that, goto test 2.
 *   2) If all sockets have sk->sk_reuse set, and none of them are in
 *      TCP_LISTEN state, the port may be shared.
 *      Failing that, goto test 3.
 *   3) If all sockets are bound to a specific inet_sk(sk)->rcv_saddr local
 *      address, and none of them are the same, the port may be
 *      shared.
 *      Failing this, the port cannot be shared.
 *
 * The interesting point, is test #2.  This is what an FTP server does
 * all day.  To optimize this case we use a specific flag bit defined
 * below.  As we add sockets to a bind bucket list, we perform a
 * check of: (newsk->sk_reuse && (newsk->sk_state != TCP_LISTEN))
 * As long as all sockets added to a bind bucket pass this test,
 * the flag bit will be set.
 * ...
 */
```

Комментарий выше намекает, что ядро пытается оптимизировать счастливый случай отсутствия конфликта. Для этого bind-бакет держит дополнительное состояние, агрегирующее свойства находящихся в нём сокетов:

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

Сфокусируем внимание только на первом агрегированном свойстве — `fastreuse`. Оно существует с доисторических времён Linux 2.1.90pre1. Изначально в форме [битового флага](https://git.kernel.org/pub/scm/linux/kernel/git/history/history.git/tree/include/net/tcp.h?h=2.1.90pre1&id=9d11a5176cc5b9609542b1bd5a827b8618efe681#n76), как говорит комментарий, лишь со временем эволюционировав в поле размером с байт.

Остальные шесть полей пришли значительно позже — с появлением [`SO_REUSEPORT` в Linux 3.9](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=da5e36308d9f7151845018369148201a5d28b46d). Они играют роль, только когда есть сокеты с установленным флагом [`SO_REUSEPORT`](https://manpages.debian.org/unstable/manpages/socket.7.en.html#SO_REUSEPORT). Сегодня мы их игнорируем.

Всякий раз, когда ядру Linux нужно привязать сокет к локальному порту, оно сначала должно найти bind-бакет для этого порта. Жизнь немного усложняет тот факт, что поиск TCP bind-бакета существует в двух местах ядра. Поиск bind-бакета может произойти рано — `в момент bind()` — или поздно — `в момент connect()`. Какой из них вызывается, зависит от того, как настроен подключаемый сокет:

![image](/images/b474d081c648911dbde0bd23af5b0046.png)

Однако, попадаем ли мы в [`inet_csk_get_port`](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L486) или [`__inet_hash_connect`](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_hashtables.c#L992), мы всегда в итоге идём по цепочке бакетов в bhash, ища бакет с совпадающим номером порта. Бакет может уже существовать, или его придётся создать. Но когда он существует, его поле fastreuse находится в одном из трёх возможных состояний: `-1`, `0` или `+1`. Как будто разработчиков Linux вдохновляла [квантовая механика](https://en.wikipedia.org/wiki/Triplet_state).

Это состояние отражает два аспекта bind-бакета:

  1. Какие сокеты находятся в бакете?
  2. Когда локальный порт может использоваться совместно?

Итак, давайте попробуем расшифровать три возможных состояния fastreuse и то, что они означают в каждом случае.

Во-первых, что свойство fastreuse говорит о владельцах бакета, то есть о сокетах, использующих этот локальный порт?

fastreuse равен | список owners содержит
---|---
-1 | сокеты, connect()-нутые с эфемерного порта
0 | сокеты, забинденные без SO_REUSEADDR
+1 | сокеты, забинденные с SO_REUSEADDR

Хотя это не вся правда, пока этого достаточно. Скоро мы доберёмся до сути.

Что касается совместного использования порта, ситуация куда менее простая:

Могу ли я … когда … | fastreuse = -1 | fastreuse = 0 | fastreuse = +1
---|---|---|---
bind() на тот же порт (эфемерный или указанный) | да, ЕСЛИ локальный IP уникален ① | ← [то же](https://en.wiktionary.org/wiki/idem#Pronoun) | ← то же
bind() на конкретный порт с SO_REUSEADDR | да, ЕСЛИ локальный IP уникален ИЛИ конфликтующий сокет использует SO_REUSEADDR ① | ← то же | да ②
connect() с того же эфемерного порта к тому же удалённому (IP, порт) | да, ЕСЛИ локальный IP уникален ③ | нет ③ | нет ③
connect() с того же эфемерного порта к уникальному удалённому (IP, порт) | да ③ | нет ③ | нет ③

① Определяется [`inet_csk_bind_conflict()`](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L214), вызываемой из `inet_csk_get_port()` (бинд на конкретный порт) или `inet_csk_get_port()` → `inet_csk_find_open_port()` (бинд на эфемерный порт).

② Потому что `inet_csk_get_port()` [пропускает проверку конфликтов](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L531) для бакетов с `fastreuse == 1`.

③ Потому что `inet_hash_connect()` → `__inet_hash_connect()` [пропускает бакеты](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_hashtables.c#L1062) с `fastreuse != -1`.

Хотя на первый взгляд всё выглядит довольно сложно, мы можем выжать из таблицы выше несколько утверждений, которые верны и усваиваются легче:

  * `bind()`, то есть раннее выделение локального адреса, всегда успешен, если нет конфликта локального IP-адреса ни с одним существующим сокетом;
  * `connect()`, то есть позднее выделение локального адреса, всегда терпит неудачу, когда TCP bind-бакет локального порта находится в любом состоянии, кроме `fastreuse = -1`;
  * `connect()` успешен, только если нет конфликта ни локального, ни удалённого адреса;
  * опция сокета `SO_REUSEADDR` разрешает совместное использование локального адреса, если все конфликтующие сокеты тоже её используют (и ни один из них не находится в состоянии прослушивания).

### Это безумие. Я вам не верю.

К счастью, вам и не приходится. С помощью [drgn](https://drgn.readthedocs.io/en/latest/index.html), программируемого отладчика, мы можем исследовать состояние bind-бакетов на живом ядре:

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
        # Skip buckets not from this netns
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

    # Iterate over all bhash slots
    for i in range(0, tcp_hashinfo.bhash_size):
        head = tcp_hashinfo.bhash[i].chain
        # Iterate over bind buckets in the slot
        dump_bind_bucket(head, net)

main()
```

Давайте испытаем [этот скрипт](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/dump_bhash.py) и попробуем подтвердить, что утверждает _Таблица 1_. Имейте в виду, что для получения фрагментов сеансов `ipython --classic` ниже я использовал ту же настройку, что и для вопросов викторины.

Два подключённых сокета, использующих эфемерный порт 60 000:

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

Два забинденных сокета, переиспользующие порт 60 000:

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

Смесь забинденных сокетов с REUSEADDR и без него, использующих порт 60 000:

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

С таким инструментарием доказательство того, что _Таблица 2_ верна, — просто вопрос написания пачки [разведочных тестов](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse.py).

Но что же произошло в последнем фрагменте? Bind-бакет явно перешёл из одного состояния fastreuse в другое. Это то, чего _Таблица 1_ не отражает. И это значит, что у нас всё ещё нет полной картины.

Нам ещё предстоит выяснить, когда состояние fastreuse бакета может измениться. Это требует машины состояний.

### Das State Machine

Как мы только что видели, bind-бакету не обязательно оставаться в начальном состоянии fastreuse на протяжении всей своей жизни. Добавление сокетов в бакет может вызвать смену состояния. Как выясняется, он может перейти только в `fastreuse = 0`, если нам случится забиндить сокет, который:

  1. не конфликтует с существующими владельцами, и
  2. не имеет включённой опции `SO_REUSEADDR`.

![image](/images/3f93c4aeacd9d5f7e74fdab6d0105e3a.png)

И хотя мы могли бы разобраться во всём этом, внимательно читая код в [`inet_csk_get_port → inet_csk_update_fastreuse`](https://elixir.bootlin.com/linux/v6.2/source/net/ipv4/inet_connection_sock.c#L431), подтверждение понимания [ещё несколькими тестами](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse_states.py) точно не помешает.

Теперь, когда у нас есть полная картина, напрашивается вопрос...

### Почему вы мне всё это рассказываете?

Во-первых, чтобы в следующий раз, когда системный вызов `bind()` отвергнет ваш запрос с `EADDRINUSE`, или `connect()` откажется сотрудничать, выбросив ошибку `EADDRNOTAVAIL`, вы знали, что происходит, или хотя бы имели инструменты, чтобы выяснить.

Во-вторых, потому что мы ранее [рекламировали технику](/how-to-stop-running-out-of-ephemeral-ports-and-start-to-love-long-lived-connections/) открытия соединений из определённого диапазона портов, включающую bind() сокетов с опцией SO_REUSEADDR. Чего мы тогда не осознавали, так это того, что существует [угловой случай](https://github.com/cloudflare/cloudflare-blog/blob/master/2023-03-quantum-state-of-tcp-port/test_fastreuse.py#L300), когда тот же порт не может использоваться совместно с обычными, `connect()`-нутыми сокетами. Хотя это не критично, хорошо понимать последствия.

Чтобы стало лучше, мы поработали с сообществом Linux над расширением API ядра новой опцией сокета, позволяющей пользователю [указать диапазон локальных портов](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=91d0b78c5177). Новая опция будет доступна в грядущем Linux 6.3. С ней нам больше не придётся прибегать к bind()-трюкам. Это вновь делает возможным совместное использование локального порта с обычными `connect()`-нутыми сокетами.

## Заключительные мысли

Сегодня мы задали относительно простой вопрос — когда два TCP-сокета могут использовать один локальный адрес? — и проделали путь к ответу. Ответ, который слишком сложен, чтобы сжать его в одно предложение. Более того, это даже не полный ответ. В конце концов, мы решили проигнорировать существование возможности SO_REUSEPORT и не рассматривали конфликты с TCP-сокетами в состоянии прослушивания.

Если и есть простой вывод, то он в том, что bind() сокета может иметь коварные последствия. Используя bind() для выбора исходящего IP-адреса, лучше всего комбинировать его с опцией сокета IP_BIND_ADDRESS_NO_PORT и оставлять назначение порта ядру. Иначе мы можем непреднамеренно заблокировать переиспользование локальных TCP-портов.

Жаль, что тот же совет не применим к UDP, где IP_BIND_ADDRESS_NO_PORT сегодня на самом деле не работает. Но это уже другая история.

До следующего раза ?.

Если вам нравится ломать голову, читая исходный код ядра Linux, — [мы нанимаем](https://www.cloudflare.com/careers/).

**********

[linux](/tags/linux.md)
[tcp](/tags/tcp.md)
[sockets](/tags/sockets.md)