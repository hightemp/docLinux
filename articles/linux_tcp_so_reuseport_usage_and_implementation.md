# Linux TCP SO_REUSEPORT: использование и реализация

Источник: [Linux TCP SO_REUSEPORT: Usage and Implementation](https://linuxjournal.rubdos.be/ljarchive/LJ/298/12538.html)

Улучшаем производительность сервера с помощью относительно новой возможности сетевой подсистемы Linux — опции сокета `SO_REUSEPORT`. Автор: Кришна Кумар (Krishna Kumar)

HAProxy и NGINX — одни из немногих приложений, использующих TCP `SO_REUSEPORT` — [опцию сокета сетевой подсистемы Linux](https://lwn.net/Articles/542629). Эта опция, изначально представленная в 4.4 BSD, используется для реализации высокопроизводительных серверов, помогающих эффективнее задействовать современные большие многоядерные системы. Первые несколько разделов этой статьи объясняют ключевые концепции сокетов TCP/IP, а оставшиеся разделы используют эти знания для описания обоснования, использования и реализации опции сокета `SO_REUSEPORT`.

### Основы TCP-соединения

TCP-соединение определяется [уникальной пятёркой (5-tuple)](https://en.wikipedia.org/wiki/Network_socket):

> _[ Протокол, IP-адрес источника, Порт источника, IP-адрес назначения, Порт назначения ]_

Отдельные элементы пятёрки задаются клиентами и серверами по-разному. Давайте посмотрим, как инициализируется каждый элемент пятёрки.

### Клиентское приложение

**Протокол:** это поле инициализируется при создании сокета на основе параметров, предоставленных приложением. Для целей этой статьи протоколом всегда является TCP. Например:

```c
socket(AF_INET, SOCK_STREAM, 0);  /* create a TCP socket */
```

**IP-адрес и порт источника:** обычно задаются ядром, когда приложение вызывает `connect()` без предварительного вызова `bind()`. Ядро выбирает подходящий IP-адрес для связи с сервером назначения и порт источника из диапазона эфемерных портов (`sysctl net.ipv4.ip_local_port_range`).

**IP-адрес и порт назначения:** задаются приложением при вызове `connect()`. Например:

```c
server.sin_family  = AF_INET;
server.sin_port    = htons(SERVER_PORT);
bcopy(server_ent->h_addr, &server.sin_addr.s_addr,
      server_ent->h_length);
/* Connect to server, and set the socket's destination IP
 * address and port# based on above parameters. Also, request
 * the kernel to automatically set the Source IP and port# if
 * the application did not call bind() prior to connect().
 */
connect(fd, (struct sockaddr *)&server, sizeof server);
```

### Серверное приложение

**Протокол:** инициализируется так же, как описано для клиентского приложения.

**IP-адрес и порт источника:** задаются приложением при вызове `bind()`, например:

```c
srv_addr.sin_family        = AF_INET;
srv_addr.sin_addr.s_addr   = INADDR_ANY;
srv_addr.sin_port          = htons(SERVER_PORT);
bind(fd, &srv_addr, sizeof srv_addr);
```

**IP-адрес и порт назначения:** клиент подключается к серверу, завершая [трёхэтапное рукопожатие TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol). Стек TCP/IP сервера создаёт новый сокет для отслеживания соединения с клиентом и устанавливает его IP:порт источника и IP:порт назначения из параметров входящего клиентского соединения. Новый сокет переводится в состояние `ESTABLISHED`, тогда как сокет `LISTEN` сервера остаётся неизменным. В этот момент вызов `accept()` серверным приложением на сокете `LISTEN` возвращает ссылку на новый сокет в состоянии `ESTABLISHED`. Пример реализации клиентского и серверного приложений смотрите в листинге в конце этой статьи.

### Сокеты TIME-WAIT

[Сокет TIME-WAIT](https://en.wikipedia.org/wiki/File:Tcp_state_diagram.png) создаётся, когда приложение закрывает свою сторону TCP-соединения первым. Это приводит к запуску четырёхэтапного рукопожатия TCP, в ходе которого состояние сокета меняется с `ESTABLISHED` на `FIN-WAIT1`, затем на `FIN-WAIT2` и на `TIME-WAIT`, прежде чем сокет закрывается. Состояние `TIME-WAIT` — это отложенное состояние, существующее по причинам протокола. Приложение может указать стеку TCP/IP не задерживать соединение, отправив TCP-пакет RST. При этом соединение завершается мгновенно, без прохождения четырёхэтапного рукопожатия TCP. Следующий фрагмент кода реализует сброс соединения, задавая время задержки сокета (linger) в ноль секунд:

```c
const struct linger opt = { .l_onoff = 1, .l_linger = 0 };

setsockopt(fd, SOL_SOCKET, SO_LINGER, &opt, sizeof opt);
close(fd);
```

### Понимание различных состояний серверного сокета

Сервер при запуске обычно выполняет следующие системные вызовы:

1) Создание сокета:

```c
server_fd = socket(...);
```

2) Привязка к общеизвестному IP-адресу и номеру порта:

```c
ret = bind(server_fd, ...);
```

3) Перевод сокета в пассивное состояние путём изменения его состояния на `LISTEN`:

```c
ret = listen(server_fd, ...);
```

4) Ожидание подключения клиента и получение ссылающегося файлового дескриптора:

```c
client_fd = accept(server_fd, ...);
```

Любой новый сокет, созданный системными вызовами `socket()` или `accept()`, отслеживается в ядре с помощью [структуры "struct sock"](https://elixir.bootlin.com/linux/v4.17.13/source). В приведённом выше фрагменте кода сокет создаётся на шаге №1 и получает общеизвестный адрес на шаге №2. Этот сокет переводится в состояние `LISTEN` на шаге №3. Шаг №4 вызывает `accept()`, который блокируется, пока клиент не подключится к этому IP:порту. После того как клиент завершит трёхэтапное рукопожатие TCP, ядро создаёт второй сокет и возвращает ссылку на него. Состояние нового сокета устанавливается в `ESTABLISHED`, тогда как сокет `server_fd` остаётся в состоянии `LISTEN`.

### Опция сокета SO_REUSEADDR

Рассмотрим два сценария использования, чтобы лучше понять опцию `SO_REUSEADDR` для TCP-сокетов.

**Сценарий №1:** серверное приложение перезапускается в два этапа — выход, за которым следует запуск. При выходе сокет `LISTEN` сервера закрывается немедленно. Из-за наличия существующих соединений с сервером могут возникнуть две ситуации:

  1. Все установленные соединения, которые обслуживались этим умирающим серверным процессом, закрываются, и эти сокеты переходят в состояние `TIME-WAIT`.
  2. Все установленные соединения, которые были переданы дочернему процессу, остаются в состоянии `ESTABLISHED`.

Когда сервер впоследствии запускается, его попытка привязаться к своему порту `LISTEN` завершается ошибкой `EADDRINUSE`, поскольку некоторые сокеты в системе уже привязаны к этой комбинации IP:порт (например, сокет в состоянии `TIME-WAIT` или `ESTABLISHED`). Вот демонстрация этой проблемы:

```bash
# Server is listening on port #45000.
$ ss -tan | grep :45000
LISTEN   0     1      10.20.1.1:45000      *:*

# A client connects to the server using its source
# port 54762. A new socket is created and is seen
# in the ESTABLISHED state, along with the
# earlier LISTEN socket.
$ ss -tan | grep :45000
LISTEN     0     1    10.20.1.1:45000      *:*
ESTAB      0     0    10.20.1.1:45000      10.20.1.100:54762

# Kill the server application.
$ pkill -9 my_server

# Restart the server application.
$ ./my_server 45000
bind: Address already in use

# Find out why
$ ss -tan | grep :45000
TIME-WAIT  0     0    10.20.1.1:45000      10.20.1.100:54762
```

Этот листинг показывает, что ранний сокет `ESTABLISHED` — это тот же сокет, который теперь виден в состоянии `TIME-WAIT`. Наличие этого сокета, привязанного к локальному адресу 10.20.1.1:45000, помешало серверу впоследствии выполнить `bind()` к той же комбинации IP:порт для своего сокета `LISTEN`.

**Сценарий №2:** если два процесса пытаются выполнить `bind()` к одной и той же комбинации IP:порт, процесс, который выполнит `bind()` первым, преуспеет, а второй завершится ошибкой `EADDRINUSE`. Другой вариант этого сценария: одно приложение привязывается к конкретному IP:порту (например, 192.168.100.1:80), а другое приложение пытается привязаться к wildcard-IP-адресу с тем же номером порта (например, 0.0.0.0:80), или наоборот. Последний вызов `bind()` завершается ошибкой, поскольку он пытается привязаться ко всем адресам с тем же номером порта, который использовался первым процессом. Если оба процесса установят опцию `SO_REUSEADDR` на своих сокетах, оба сокета смогут быть успешно привязаны. Однако заметьте эту оговорку: если первый процесс вызывает `bind()` и `listen()`, второй процесс всё равно не сможет успешно выполнить `bind()`, поскольку первый сокет находится в состоянии `LISTEN`. Следовательно, этот сценарий обычно предназначен для клиентов, которые хотят привязаться к конкретному IP:порту перед подключением к разным службам.

Как `SO_REUSEADDR` помогает решить эту проблему? Когда сервер перезапускается и вызывает `bind()` на сокете с установленной опцией `SO_REUSEADDR`, ядро игнорирует все сокеты не в состоянии `LISTEN`, привязанные к той же комбинации IP:порт. Книга _UNIX Network Programming_ [описывает эту возможность так](https://www.amazon.com/Unix-Network-Programming-Sockets-Networking/dp/0131411551): «`SO_REUSEADDR` позволяет слушающему серверу запуститься и привязаться к своему общеизвестному порту, даже если существуют ранее установленные соединения, использующие этот порт в качестве своего локального порта».

Однако, чтобы позволить двум или более процессам успешно вызвать `listen()` на одном и том же порту, нам нужна опция `SO_REUSEPORT`. Я описываю эту опцию более подробно в остальных разделах.

### Опция сокета SO_REUSEPORT

В то время как `SO_REUSEADDR` позволяет сокетам выполнять `bind()` к одной и той же комбинации IP:порт, когда могут присутствовать существующие сокеты `ESTABLISHED` или `TIME-WAIT`, `SO_REUSEPORT` позволяет привязываться к тому же IP:порту, даже когда могут присутствовать существующие сокеты `LISTEN`. Ядро игнорирует все сокеты, включая сокеты в состоянии `LISTEN`, когда приложение вызывает `bind()` или `listen()` на сокете с включённой опцией `SO_REUSEPORT`. Это позволяет запускать серверный процесс многократно, давая множеству процессов возможность слушать соединения. В следующем разделе рассматривается реализация `SO_REUSEPORT` в ядре.

### Как соединения распределяются между несколькими слушателями?

Когда несколько сокетов находятся в состоянии `LISTEN`, как ядро решает, какой сокет — и, соответственно, какой процесс приложения — получает входящее соединение? Определяется ли это методом round-robin, least-connection, случайным или каким-либо иным методом? Давайте глубже заглянем в код TCP/IP, чтобы понять, как выполняется выбор сокета.

Примечания:

  * Структуры данных и фрагменты кода в этом разделе сильно упрощены для ясности — удалены некоторые элементы структур, аргументы функций, переменные и ненужный код — но без потери корректности. Некоторые части листинга также представлены в виде псевдокода для лучшего понимания.
  * `sk` представляет структуру данных сокета ядра типа "struct sock".
  * `skb`, или буфер сокета (socket buffer), представляет сетевой пакет типа "struct sk_buff".
  * `src_addr`, `src_port` и `dst_addr`, `dst_port` означают соответственно IP:порт источника и IP:порт назначения.
  * При желании читатели могут сопоставить фрагменты кода с [реальным исходным кодом](https://elixir.bootlin.com/linux/v4.17.13/source).

Когда входящий пакет (`skb`) движется вверх по стеку TCP/IP, IP-подсистема вызывает обработчик приёма TCP-пакетов `tcp_v4_rcv()`, передавая `skb` в качестве аргумента. `tcp_v4_rcv()` пытается найти сокет, связанный с этим `skb`:

```c
sk = __inet_lookup_skb(&tcp_hashinfo, skb, src_port, dst_port);
```

`tcp_hashinfo` — это глобальная переменная типа `struct inet_hashinfo`, содержащая, среди прочего, две хеш-таблицы сокетов `ESTABLISHED` и `LISTEN` соответственно. Размер хеш-таблицы `LISTEN` составляет 32 корзины, как показано ниже:

```c
#define LHTABLE_SIZE 32 /* Yes, this really is all you need */
struct inet_hashinfo {
   /* Hash table for fully established sockets */
   struct inet_ehash_bucket *ehash;
   /* Hash table for LISTEN sockets */
   struct inet_listen_hashbucket listening_hash[LHTABLE_SIZE];
};

struct inet_hashinfo tcp_hashinfo;
```

`__inet_lookup_skb()` извлекает IP-адреса источника и назначения из входящего `skb` и передаёт их вместе с портами источника и назначения в `__inet_lookup()`, чтобы найти связанный сокет `ESTABLISHED` или `LISTEN`, как показано здесь:

```c
struct sock *__inet_lookup_skb(tcp_hashinfo, skb,
 ↪src_port, dst_port)
{
   /* Get the IPv4 header to know
    * the source and destination IPs */
   const struct iphdr *iph = ip_hdr(skb);

   /*
    * Look up the incoming skb in tcp_hashinfo using the
    * [ Source-IP:Port, Destination-IP:Port ] tuple.
    */
   return __inet_lookup(tcp_hashinfo, skb, iph->saddr,
            ↪src_port, iph->daddr, dst_port);
}
```

`__inet_lookup()` ищет в `tcp_hashinfo->ehash` уже установленное соединение, соответствующее параметрам четвёрки клиента. При отсутствии установленного сокета она ищет в `tcp_hashinfo->listening_hash` сокет `LISTEN`:

```c
struct sock *__inet_lookup(tcp_hashinfo, skb, src_addr,
                ↪src_port, dst_addr, dst_port)
{
   /* Convert dest_port# from network to host byte order */
   u16 hnum = ntohs(dst_port);

   /* First look for an established socket ... */
   sk = __inet_lookup_established(tcp_hashinfo, src_addr,
            ↪src_port, dst_addr, hnum);
   if (sk)
      return sk;

   /* failing which, look for a LISTEN socket */
   return __inet_lookup_listener(tcp_hashinfo, skb, src_addr,
                                 src_port, dst_addr, hnum);
}
```

Функция `__inet_lookup_listener()` реализует выбор сокета `LISTEN`:

```c
struct sock *__inet_lookup_listener(tcp_hashinfo, skb,
                  ↪src_addr, src_port, dst_addr, dst_port)
{
   /*
    * Use the destination port# to calculate a hash table
    * slot# of the listen socket. inet_lhashfn() returns
    * a number between 0
    * and LHTABLE_SIZE-1 (both inclusive).
    */
   unsigned int hash = inet_lhashfn(dst_port);

   /* Use this slot# to index the global LISTEN hash table */
   struct inet_listen_hashbucket *ilb =
                       ↪tcp_hashinfo->listening_hash[hash];

   /* Track best matching LISTEN socket
    * so far and its "score" */
   struct sock *result = NULL, *sk;
   int hi_score = 0;

   for each socket, 'sk', in the selected hash bucket, 'ilb' {
      /*
       * Calculate the "score" of this LISTEN socket (sk)
       * against the incoming skb. Score is computed on
       * some parameters, such as exact destination port#,
       * destination IP address exact match (as against
       * matching INADDR_ANY, for example),
       * with each criteria getting a different weight.
       */
      score = compute_score(sk, dst_port, dst_addr);
      if (score > hi_score) {
         /* Highest score - best matched socket till now */
         if (sk->sk_reuseport) {
            /*
             * sk has SO_REUSEPORT feature enabled. Call
             * inet_ehashfn() with dest_addr, dest_port,
             * src_addr and src_port to compute a
             * 2nd hash, phash.
             */
            phash = inet_ehashfn(dst_addr, dst_port,
                                 src_addr, src_port);

            /* Select a socket from sk's SO_REUSEPORT group
             * using 'phash'.
             */
            result = reuseport_select_sock(sk, phash);
            if (result)
               return result;
         }

         /* Update new best socket and its score */
         result = sk;
         hi_score = score;
      }
   }

   return result;
}
```

Выбор сокета из группы `SO_REUSEPORT` выполняется с помощью `reuseport_select_sock()`:

```c
struct sock *reuseport_select_sock(struct sock *sk,
                                   unsigned int phash)
{
   /* Get control block of sockets
    * in this SO_REUSEPORT group */
   struct sock_reuseport *reuse = sk->sk_reuseport_cb;

   /* Get count of sockets in the group */
   int num_socks = reuse->num_socks;

   /* Calculate value between 0 and 'num_socks-1'
    * (both inclusive) */
   unsigned int index = reciprocal_scale(phash, num_socks);

   /* Index into the SO_REUSEPORT group using this index */
   return reuse->socks[index];
}
```

Давайте немного вернёмся, чтобы понять, как это работает. Когда первый процесс вызвал `listen()` на сокете с включённой опцией `SO_REUSEPORT`, указатель в его структуре "struct sock" — `sk_reuseport_cb` — выделяется. Эта структура определена так:

```c
struct sock_reuseport {
  u16      max_socks; /* Allocated size of socks[] array */
  u16      num_socks; /* #Elements in socks[] */
  struct sock *socks[0]; /* All sockets added to this group */
};
```

Последний элемент этой структуры — это [«гибкий элемент массива» (flexible array member)](https://gcc.gnu.org/onlinedocs/gcc/Zero-Length.html). Вся структура выделяется так, чтобы массив `socks[]` имел 128 элементов типа `struct sock *`. Обратите внимание, что когда количество слушателей превышает 128, эта структура перевыделяется так, чтобы размер массива `socks[]` удвоился.

Первый сокет, `sk1`, который вызвал `listen()`, сохраняется в первом слоте собственного массива `socks[]`, например:

```c
sk1->sk_reuseport_cb->socks[0] = sk1;
```

Когда `listen()` впоследствии вызывается на других сокетах (`sk2`, ...), привязанных к тому же IP:порту, выполняются две операции:

  1. Адрес нового сокета (`sk2`, ...) добавляется в `sk_reuseport_cb->socks[]` первого сокета (`sk1`).
  2. Указатель `sk_reuseport_cb` нового сокета начинает указывать на указатель `sk_reuseport_cb` первого сокета. Это гарантирует, что все сокеты `LISTEN` одной группы ссылаются на один и тот же указатель `sk_reuseport_cb`.

Рисунок 1 показывает результат этих двух шагов.

Рисунок 1. Представление группы сокетов `LISTEN` с `SO_REUSEPORT`

На рисунке 1 `sk1` — первый сокет `LISTEN`, а `sk2` и `sk3` — сокеты, вызвавшие `listen()` позднее. Два описанных выше шага выполняются в следующем фрагменте кода, исполняемом по цепочке вызовов `listen()`:

```c
static int inet_reuseport_add_sock(struct sock *new_sk)
{
   /*
    * First check if another identical LISTEN socket, prev_sk,
    * exists. ... Then do the following:
    */
   if (prev_sk) {
      /*
       * Not the first listener - do the following:
       * - Grow prev_sk->sk_reuseport_cb structure if required.
       * - Save new_sk socket pointer in prev_sk's socks[].
       *   prev_sk->sk_reuseport_cb->socks[num_socks] = new_sk;
       * - prev_sk->sk_reuseport_cb->num_socks++;
       * - Pointer assignment of the control block:
       *   new_sk->sk_reuseport_cb = prev_sk->sk_reuseport_cb;
       */
      return reuseport_add_sock(new_sk, prev_sk);
   }

   /*
    * First listener - do the following:
    * - allocate new_sk->sk_reuseport_cb to contain 128 socks[]
    * - new_sk->sk_reuseport_cb->max_socks = 128;
    * - new_sk->sk_reuseport_cb->socks[0] = new_sk;
    * - new_sk->sk_reuseport_cb->numsocks = 1;
    */
   return reuseport_alloc(new_sk);
}
```

Теперь вернёмся к `reuseport_select_sock()`, чтобы посмотреть, как выбирается сокет `LISTEN`. Индексирование массива `socks[]` выполняется через вызов `reciprocal_scale()` следующим образом:

```c
unsigned int index = reciprocal_scale(phash, num_socks);
return reuse->socks[index];
```

[reciprocal_scale()](http://homepage.cs.uiowa.edu/~jones/bcd/divide.html) — это оптимизированная функция, реализующая псевдооперацию взятия остатка с помощью операций умножения и сдвига.

Как показано ранее, `phash` вычисляется в `__inet_lookup_listener()`:

```c
phash = inet_ehashfn(dst_addr, dst_port, src_addr, src_port);
```

А `num_socks` — это количество сокетов в массиве `socks[]`. Функция `reciprocal_scale(phash, num_socks)` вычисляет индекс, `0 <= index < num_socks`. Этот индекс используется для извлечения сокета из группы сокетов `SO_REUSEPORT`.

Следовательно, видно, что ядро выбирает сокет, хешируя значения IP:порта клиента и IP:порта сервера. Этот метод обеспечивает хорошее распределение соединений между различными сокетами `LISTEN`.

### SO_REUSEPORT в действии

Рассмотрим эффект `SO_REUSEPORT` в командной строке с помощью двух тестов.

1) Приложение открывает сокет для прослушивания и создаёт два процесса.

Путь кода приложения: `socket(); bind(); listen(); fork();`

```bash
$ ss -tlnpe | grep :45000
LISTEN     0     128    *:45000      *:* users:(("my_server",
↪pid=3020,fd=3),("my_server",pid=3019,fd=3))
 ↪ino:3854904087 sk:37d5a0
```

Строка `ino:3854904087 sk:37d5a0` описывает единственный сокет ядра.

2) Приложение создаёт два процесса, и каждый создаёт сокет `LISTEN` после установки `SO_REUSEPORT`.

Путь кода приложения: `fork(); socket(); setsockopt(SO_REUSEPORT); bind(); listen();`

```bash
$ ss -tlnpe | grep :45000
LISTEN     0     128    *:45000     *:*  users:(("my_server",
↪pid=1975,fd=3)) ino:3854935788 sk:37d59c
LISTEN     0     128    *:45000     *:*  users:(("my_server",
↪pid=1974,fd=3)) ino:3854935786 sk:37d59d
```

Теперь вы видите два разных сокета ядра — обратите внимание на разные номера inode.

Приложения, использующие несколько процессов для приёма соединений на одном сокете `LISTEN`, могут столкнуться с серьёзными проблемами производительности, поскольку каждый процесс конкурирует за одну и ту же блокировку сокета в `accept()`, как показано в следующем упрощённом псевдокоде:

```c
struct sock *inet_csk_accept(struct sock *sk)
{
   struct sock *newsk = NULL;   /* client socket */

   /* We need to make sure that this socket is listening, and
    * that it has something pending.
    */
   lock_sock(sk);
   if (sk->sk_state == TCP_LISTEN)
      if ("there are completed connections waiting
            ↪to be accepted")
         newsk = get_first_connection(sk);
   release_sock(sk);

   return newsk;
}
```

И `lock_sock()`, и `release_sock()` внутри себя захватывают и освобождают спинлок, встроенный в `sk`. (Смотрите рисунок 3 далее в этой статье, чтобы увидеть накладные расходы из-за конкуренции за спинлок.)

### Тестирование производительности SO_REUSEPORT

Для измерения производительности `SO_REUSEPORT` используется следующая конфигурация:

  1. Версия ядра: 4.17.13.
  2. Клиентская и серверная системы обе имеют 48 гиперпоточных ядер и соединены между собой через коммутатор сетевыми картами 40g.
  3. Сервер запускается одним из двух способов: создаётся единственный сокет `LISTEN` и выполняется fork 48 раз, либо выполняется fork 48 раз, и каждый дочерний процесс создаёт сокет `LISTEN` после включения `SO_REUSEPORT`.
  4. Клиент создаёт 48 процессов. Каждый процесс последовательно подключается к серверу и отключается от него миллион раз.

С форком сокета `LISTEN`:

```text
server-system-$  ./my_server 45000  48  0   (0 indicates fork)
client-system-$  time ./my_client <server-ip> 45000 48 1000000
real   4m45.471s
```

С `SO_REUSEPORT`:

```text
server-system-$ ./my_server 45000 48  1  (1 indicates
 ↪SO_REUSEPORT)
client-system-$ time ./my_client <server-ip> 45000 48 1000000
real   1m36.766s
```

### Анализ производительности SO_REUSEPORT

Рисунки 2–5 показывают профиль производительности для двух описанных выше тестов с помощью инструмента `perf`.

Рисунок 2. Статистика счётчиков производительности без `SO_REUSEPORT`

Рисунок 3. Профиль производительности 25 верхних функций без `SO_REUSEPORT`

Рисунок 4. Статистика счётчиков производительности с `SO_REUSEPORT`

Рисунок 5. Профиль производительности 25 верхних функций с `SO_REUSEPORT`

### Исходный код клиентского и серверного приложений

Приведённый ниже листинг реализует серверное и клиентское приложения, которые использовались для тестирования производительности `SO_REUSEPORT`:

```c
$ cat my_server.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <netdb.h>

void create_children(int nprocs, int parent_pid)
{
   while (nprocs-- > 0) {
      if (getpid() == parent_pid && fork() < 0)
         exit(1);
   }
}

int main(int argc, char *argv[])
{
   int reuse_port, fd, cfd, nprocs, opt = 1, parent_pid =
    ↪getpid();
   struct sockaddr_in server;

   if (argc != 4) {
      fprintf(stderr, "Port# #Procs {0->fork, or
       ↪1->SO_REUSEPORT}\n");
      return 1;
   }

   nprocs = atoi(argv[2]);
   reuse_port = atoi(argv[3]);
   if (reuse_port)   /* proper SO_REUSEPORT */
      create_children(nprocs, parent_pid);

   if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
      perror("socket");
      return 1;
   }

   if (reuse_port)
      setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, (char *)&opt,
                 sizeof opt);

   server.sin_family      = AF_INET;
   server.sin_addr.s_addr = INADDR_ANY;
   server.sin_port        = htons(atoi(argv[1]));

   if (bind(fd, (struct sockaddr *)&server, sizeof server)
    ↪< 0) {
      perror("bind");
      return 1;
   }

   if (!reuse_port)   /* simple fork instead of SO_REUSEPORT */
      create_children(nprocs, parent_pid);

   if (parent_pid == getpid()) {
      while (wait(NULL) != -1);   /* wait for all children */
   } else {
      listen(fd, SOMAXCONN);
      while (1) {
         if ((cfd = accept(fd, NULL, NULL)) < 0) {
            perror("accept");
            return 1;
         }
         close(cfd);
      }
   }

   return 0;
}

$ cat my_client.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <strings.h>
#include <sys/wait.h>
#include <netdb.h>

void create_children(int nprocs, int parent_pid)
{
void create_children(int nprocs, int parent_pid)
{
   while (nprocs-- > 0) {
      if (getpid() == parent_pid && fork() < 0)
         exit(1);
   }
}

int main(int argc, char *argv[])
{
   int fd, count, nprocs, parent_pid = getpid();
   struct sockaddr_in server;
   struct hostent *server_ent;
   const struct linger nolinger = { .l_onoff = 1,
    ↪.l_linger = 0 };

   if (argc != 5) {
      fprintf(stderr, "Server-IP Port# #Processes
       ↪#Conns_per_Proc\n");
      return 1;
   }

   nprocs = atoi(argv[3]);
   count = atoi(argv[4]);

   if ((server_ent = gethostbyname(argv[1])) == NULL) {
      perror("gethostbyname");
      return 1;
   }

   bzero((char *)&server, sizeof server);
   server.sin_family = AF_INET;
   server.sin_port   = htons(atoi(argv[2]));
   bcopy((char *)server_ent->h_addr, (char *)
↪&server.sin_addr.s_addr,
         server_ent->h_length);

   create_children(nprocs, parent_pid);

   if (getpid() == parent_pid) {
      while (wait(NULL) != -1);   /* wait for all children */
   } else {
      while (count-- > 0) {
         if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            perror("socket");
            return 1;
         }

         if (connect(fd, (struct sockaddr *)&server,
                     sizeof server) < 0) {
            perror("connect");
            return 1;
         }

         /* Reset connection to avoid TIME-WAIT state */
         setsockopt(fd, SOL_SOCKET, SO_LINGER, &nolinger,
                    sizeof nolinger);
         close(fd);
      }
   }

   return 0;
}
```

### Ресурсы

  * ["The SO_REUSEPORT socket option" by Michael Kerrisk](https://lwn.net/Articles/542629) на LWN.net
  * [Network Socket](https://en.wikipedia.org/wiki/Network_socket) (Wikipedia)
  * [Transmission Control Protocol](https://en.wikipedia.org/wiki/Transmission_Control_Protocol) (Wikipedia)
  * [TCP State Transition Diagram](https://en.wikipedia.org/wiki/File:Tcp_state_diagram.png)
  * [Kernel Source Code](https://elixir.bootlin.com/linux/v4.17.13/source)
  * [UNIX Network Programming](https://www.amazon.com/Unix-Network-Programming-Sockets-Networking/dp/0131411551) by W. Richard Stevens, Bill Fenner and Andrew M. Rudoff
  * [Arrays of Length Zero](https://gcc.gnu.org/onlinedocs/gcc/Zero-Length.html)
  * [Reciprocal Multiplication](http://homepage.cs.uiowa.edu/~jones/bcd/divide.html)

### Об авторе

Кришна Кумар работает в Flipkart Internet Pvt Ltd — крупнейшей e-commerce компании Индии. Он особенно заинтересован в сегодняшней теме, поскольку Flipkart использует эту технологию, чтобы обслуживать миллионы соединений от посетителей со всего мира. Среди его других интересов — игра в шахматы, тяжёлая борьба с освоением приложений и периодическое принесение домой бродячих щенков, к великому смятению его жены. Присылайте свои комментарии и отзывы на krishna.ku@flipkart.com.

**********

[linux](/tags/linux.md)
[sockets](/tags/sockets.md)
[kernel](/tags/kernel.md)