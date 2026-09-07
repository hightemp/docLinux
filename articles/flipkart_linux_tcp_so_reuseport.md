# Linux TCP SO_REUSEPORT: использование и реализация

Источник: [flipkart_linux_tcp_so_reuseport](https://blog.flipkart.tech/linux-tcp-so-reuseport-usage-and-implementation-6bbed5310178)

Кришна Кумар (Krishna Kumar) · Flipkart Tech Blog · 19 августа 2019 · 11 мин чтения

Улучшите производительность вашего сервера, используя относительно новую возможность сетевого стека Linux — опцию сокета SO_REUSEPORT.

![](/images/02fe44e7eca93029eb03f2272764d336.png)

Рисунок 1: Сервер вверху использует параллельные слушающие сокеты (listeners) для избежания узких мест, тогда как сервер внизу использует единственный слушающий сокет для приёма входящих соединений.

## Резюме

HAProxy и NGINX — одни из немногих приложений, которые используют опцию сокета TCP SO_REUSEPORT [1] сетевого стека Linux. Эта опция, изначально представленная в 4.4 BSD, используется для реализации высокопроизводительных серверов, которые помогают лучше задействовать современные многоядерные системы. Первые несколько разделов этой статьи объясняют ключевые концепции сокетов TCP/IP, а оставшиеся разделы используют эти знания для описания обоснования, использования и реализации опции сокета SO_REUSEPORT.

## Постановка задачи

Традиционный метод, который использует высокопроизводительный сервер на многопроцессорной системе, состоит в том, чтобы иметь один процесс-слушатель, который принимает входящие соединения и передаёт эти соединения рабочим процессам для обработки. Однако при высокой нагрузке соединениями слушающий процесс становится узким местом. Другой часто используемый серверами метод — открыть один слушающий сокет и породить (fork) несколько процессов, каждый из которых вызывает accept() для обработки входящих соединений на этом сокете, выполняя работу самостоятельно. Проблема этого подхода в том, что процесс, который начинает забирать соединения, как правило, получает перекос в их распределении. В этой статье мы обсуждаем альтернативный третий подход — открытие нескольких слушающих сокетов для обработки входящих соединений с использованием SO_REUSEPORT, который решает как проблему узкого места единственного процесса, так и перекос соединений между процессами.

## Основы TCP-соединения

TCP-соединение определяется уникальной пятёркой (5-tuple) [2]:

```text
[ Protocol, Source IP address, Source Port, Destination IP address, Destination Port ]
```

Отдельные элементы пятёрки задаются клиентами и серверами по-разному. Давайте поймём, как каждый элемент пятёрки инициализируется приложениями.

### Клиентское приложение

**Protocol (протокол)**: это поле инициализируется при создании сокета на основе параметров, предоставленных приложением. Протокол для целей этой статьи всегда TCP. Например:

```c
socket(AF_INET, SOCK_STREAM, 0); /* создать TCP-сокет */
```

**Source IP address and Port (IP-адрес и порт источника)**: они обычно устанавливаются ядром, когда приложение вызывает connect() без предварительного вызова bind(). Ядро выбирает подходящий IP-адрес для связи с сервером назначения и порт источника из диапазона эфемерных портов (sysctl net.ipv4.ip_local_port_range).

**Destination IP address and Port (IP-адрес и порт назначения)**: они устанавливаются приложением при вызове connect(). Например:

```c
connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr));
```

### Серверное приложение

**Protocol**: инициализируется так же, как описано для клиентского приложения.

**Source IP address and Port**: устанавливаются приложением при вызове bind(), например:

```c
bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr));
```

**Destination IP address and Port**: клиент подключается к серверу, завершая TCP-тройное рукопожатие (TCP 3-way handshake) [3]. Стек TCP/IP сервера создаёт новый сокет для отслеживания соединения с клиентом и устанавливает его Source IP:Port и Destination IP:Port из параметров входящего клиентского соединения. Новый сокет переводится в состояние ESTABLISHED, тогда как LISTEN-сокет сервера остаётся неизменным. В этот момент вызов accept() серверного приложения на LISTEN-сокете возвращается со ссылкой на новый сокет в состоянии ESTABLISHED. См. листинг исходного кода в конце этой статьи для примера реализации клиентского и серверного приложений.

### Сокеты TIME-WAIT

Сокет TIME-WAIT [4] создаётся, когда приложение закрывает свой конец TCP-соединения первым. Это приводит к инициированию TCP-четверного рукопожатия (TCP 4-way handshake), во время которого состояние сокета меняется с ESTABLISHED на FIN-WAIT1, затем на FIN-WAIT2, затем на TIME-WAIT, прежде чем сокет закрывается. Состояние TIME-WAIT — это задерживающееся состояние по причинам протокола. Приложение может указать стеку TCP/IP не задерживать соединение, отправив TCP-пакет RST. При этом соединение мгновенно разрывается без прохождения TCP-четверного рукопожатия. Следующий фрагмент кода реализует сброс соединения, задавая время задержки (linger time) сокета в ноль секунд:

```c
struct linger lg;
lg.l_onoff = 1;
lg.l_linger = 0;
setsockopt(fd, SOL_SOCKET, SO_LINGER, &lg, sizeof(lg));
close(fd); /* отправляет RST и мгновенно разрывает соединение */
```

## Понимание различных состояний серверного сокета

Сервер обычно выполняет следующие системные вызовы при запуске:

```c
server_fd = socket(AF_INET, SOCK_STREAM, 0);   /* #1: создать сокет */
bind(server_fd, ...);                         /* #2: назначить известный адрес */
listen(server_fd);                            /* #3: перейти в состояние LISTEN */
client_fd = accept(server_fd, ...);           /* #4: ждать клиентское соединение */
```

Любой новый сокет, созданный системными вызовами socket() или accept(), отслеживается в ядре с помощью структуры «struct sock» [5]. В приведённом выше фрагменте кода сокет создаётся на шаге #1 и получает известный адрес на шаге #2. Этот сокет переводится в состояние LISTEN на шаге #3. Шаг #4 вызывает accept(), который блокируется, пока клиент не подключится к этому IP:port. После того как клиент завершит TCP-тройное рукопожатие, ядро создаёт второй сокет и возвращает ссылку на этот сокет. Состояние нового сокета устанавливается в ESTABLISHED, тогда как сокет server_fd остаётся в состоянии LISTEN.

## Опция сокета SO_REUSEADDR

Опцию SO_REUSEADDR для TCP-сокетов можно лучше понять из следующих двух сценариев использования.

**Сценарий #1.** Серверное приложение перезапускается в два шага — выход, за которым следует запуск. При выходе LISTEN-сокет сервера закрывается немедленно. Давайте рассмотрим две ситуации, которые могут возникнуть из-за наличия существующих соединений с сервером.

* Все установленные соединения, которые обслуживались этим умирающим серверным процессом, закрываются, и эти сокеты переходят в состояние TIME-WAIT.

* Все установленные соединения, которые были переданы дочернему процессу, продолжают оставаться в состоянии ESTABLISHED.

Когда сервер впоследствии запускается, его попытка выполнить bind() на свой LISTEN-порт завершается с ошибкой EADDRINUSE, потому что некоторые сокеты в системе уже привязаны к этой комбинации IP:port (например, сокет в состоянии TIME-WAIT или ESTABLISHED). Демонстрация этой проблемы показана ниже:

```text
$ sudo ss --tcp -tina sport = :45000
State  Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  ...
LISTEN 0       511     10.20.1.1:45000     0.0.0.0:*           ...
$ ./my_server 45000
bind() failed: Address already in use
```

Этот листинг показывает, что сокет, который раньше был в состоянии ESTABLISHED, — это тот же сокет, который теперь виден в состоянии TIME-WAIT. Наличие этого сокета, привязанного к локальному адресу — 10.20.1.1:45000 — помешало серверу впоследствии выполнить bind() на ту же комбинацию IP:port для своего LISTEN-сокета.

**Сценарий #2.** Если два процесса пытаются выполнить bind() на одну и ту же комбинацию IP:port, процесс, который выполняет bind() первым, преуспевает, тогда как второй завершается с ошибкой EADDRINUSE. Другой вариант этого сценария использования включает приложение, привязывающееся к конкретному IP:port (например, 192.168.100.1:80), и другое приложение, пытающееся привязаться к wildcard-IP-адресу с тем же номером порта (например, 0.0.0.0:80); или наоборот. Последний вызов bind() завершается неудачей, так как он пытается привязаться ко всем адресам с тем же номером порта, который был использован первым процессом. Если оба процесса устанавливают опцию SO_REUSEADDR на своих сокетах, оба сокета могут быть успешно привязаны. Однако заметьте эту оговорку — если первый процесс вызовет bind() и listen(), второй процесс всё равно не сможет успешно выполнить bind(), поскольку первый сокет находится в состоянии LISTEN. Следовательно, этот сценарий использования обычно предназначен для клиентов, которые хотят привязаться к конкретному IP:port перед подключением к различным сервисам.

Как SO_REUSEADDR помогает решить эту проблему? Когда сервер перезапускается и вызывает bind() на сокете с установленным SO_REUSEADDR, ядро игнорирует все не-LISTEN-сокеты, привязанные к той же комбинации IP:port. Ричард Стивенс в своей книге Unix Network Programming [6] описывает эту возможность так: «SO_REUSEADDR позволяет слушающему серверу запуститься и привязать свой известный порт, даже если существуют ранее установленные соединения, использующие этот порт в качестве своего локального порта».

Однако нам нужна опция SO_REUSEPORT, чтобы позволить двум или более процессам успешно вызвать listen() на одном и том же порту. Эта опция описывается подробнее в оставшихся разделах.

## Опция сокета SO_REUSEPORT

В то время как SO_REUSEADDR позволяет сокетам выполнять bind() на одну и ту же комбинацию IP:port, когда могут присутствовать существующие сокеты ESTABLISHED или TIME-WAIT, SO_REUSEPORT позволяет привязку к одному и тому же IP:port, когда могут также присутствовать существующие LISTEN-сокеты. Ядро игнорирует все сокеты, включая сокеты в состоянии LISTEN, когда приложение вызывает bind() или listen() на сокете с включённым SO_REUSEPORT. Это позволяет запускать серверный процесс несколько раз, позволяя многим процессам слушать соединения. Следующий раздел исследует реализацию SO_REUSEPORT в ядре.

## Как соединения распределяются между несколькими слушающими сокетами?

Когда несколько сокетов находятся в состоянии LISTEN, как ядро решает, какой сокет — и, следовательно, какой процесс приложения — получает входящее соединение? Определяется ли это методом round-robin, least-connection, случайным или каким-либо другим методом? Давайте взглянем глубже в код TCP/IP, чтобы понять, как выполняется выбор сокета.

Примечания:

* Структуры данных и фрагменты кода в этом разделе сильно упрощены ради ясности — удалены некоторые элементы структур, аргументы функций, переменные и ненужный код — но без потери корректности. Часть листинга также представлена в псевдокоде для лучшего понимания.

* sk представляет структуру данных сокета ядра типа «struct sock».

* skb, или буфер сокета, представляет сетевой пакет типа «struct sk_buff».

* src_addr, src_port и dst_addr, dst_port относятся к IP:port источника и IP:port назначения соответственно.

* Читатели могут сопоставить фрагменты кода с реальным исходным кодом [5], если пожелают.

Когда входящий пакет skb движется вверх по стеку TCP/IP, подсистема IP вызывает обработчик приёма TCP-пакетов tcp_v4_rcv(), передавая skb в качестве аргумента. tcp_v4_rcv() пытается найти сокет, связанный с этим skb:

```c
sk = __inet_lookup_skb(&tcp_hashinfo, skb, src_port, dst_port);
```

tcp_hashinfo — это глобальная переменная типа «struct inet_hashinfo», содержащая, среди прочего, две хеш-таблицы сокетов ESTABLISHED и LISTEN соответственно. Хеш-таблица LISTEN имеет размер 32 бакета, как показано ниже:

```c
struct inet_hashinfo {
    ...
    struct inet_listen_hashbucket  listening_hash[INET_LHTABLE_SIZE]
                                         ____cacheline_aligned_smp;
    ...
};
```

__inet_lookup_skb() извлекает IP-адреса источника и назначения из входящего skb и передаёт их вместе с портами источника и назначения в __inet_lookup(), чтобы найти соответствующий сокет ESTABLISHED или LISTEN, как показано ниже:

```c
struct sock *__inet_lookup(struct net *net, struct inet_hashinfo *hashinfo,
                           struct sk_buff *skb, int doff,
                           const __be32 saddr, const __be16 sport,
                           const __be32 daddr, const __be16 dport,
                           bool exact_dif)
{
    ...
    sk = __inet_lookup_established(net, hashinfo, saddr, sport,
                                   daddr, hnum, dif);
    if (sk)
        return sk;
    ...
    return __inet_lookup_listener(net, hashinfo, skb, doff,
                                  saddr, sport, daddr, hnum, dif);
}
```

__inet_lookup() ищет в хеш-таблице tcp_hashinfo->ehash уже установленный сокет, соответствующий параметрам четвёрки (4-tuple) клиента. В отсутствие установленного сокета он ищет в хеш-таблице tcp_hashinfo->listening_hash LISTEN-сокет.

Функция __inet_lookup_listener() реализует выбор LISTEN-сокета:

```c
struct sock *__inet_lookup_listener(struct net *net,
                                    struct inet_hashinfo *hashinfo,
                                    struct sk_buff *skb, int doff,
                                    const __be32 saddr, __be16 sport,
                                    const __be32 daddr, const unsigned short hnum,
                                    const int dif)
{
    ...
    phash = inet_ehashfn(daddr, hnum, saddr, sport);
    ...
    sk_for_each_rcu(sk, &ilb->head) {
        if (sk->sk_reuseport) {
            ...
            result = reuseport_select_sock(sk, ahash, skb, doff);
            if (result)
                return result;
        }
        ...
    }
    ...
}
```

Выбор сокета из группы SO_REUSEPORT выполняется в reuseport_select_sock():

```c
struct sock *reuseport_select_sock(struct sock *sk,
                                   u32 hash,
                                   struct sk_buff *skb,
                                   int hdr_len)
{
    struct sock_reuseport *reuseport = sk->sk_reuseport_cb;
    ...
    if (reuseport->num_socks) {
        sync_rcu();
        index = reciprocal_scale(hash, reuseport->num_socks);
        sk2 = reuseport->socks[index];
        ...
        return sk2;
    }
    ...
}
```

Нам нужно немного отступить, чтобы понять, как это работает. Когда первый процесс вызвал listen() на сокете с включённым SO_REUSEPORT, указатель в его структуре «struct sock» — sk_reuseport_cb — выделяется. Эта структура определена как:

```c
struct sock_reuseport {
    unsigned int    max_socks;
    unsigned int    num_socks;
    struct bpf_prog *prog;
    struct rcu_head rcu;
    struct sock     *socks[0];
};
```

Последний элемент этой структуры — это «flexible array member» [7]. Вся структура выделяется так, что массив socks[] имеет 128 элементов типа «struct sock *». Заметьте, что когда количество слушающих сокетов возрастает свыше 128, эта структура перераспределяется так, что размер массива socks[] удваивается.

Первый сокет sk1, который вызвал listen(), кэшируется в первом слоте собственного массива socks[], например: sk1->sk_reuseport_cb->socks[0] = sk1;

Когда listen() впоследствии вызывается на других сокетах (sk2, …), привязанных к тому же IP:port, выполняются две операции:

* Адрес нового сокета (sk2, …) добавляется в sk_reuseport_cb->socks[] первого сокета (sk1).

* Указатель sk_reuseport_cb нового сокета устанавливается так, чтобы указывать на указатель sk_reuseport_cb первого сокета. Это гарантирует, что все LISTEN-сокеты одной группы ссылаются на один и тот же указатель sk_reuseport_cb.

Результат этих двух шагов показан на Рисунке 2.

![](/images/22d0f4b50b879da9af4ef8b04e074922.png)

Рисунок 2: Представление группы LISTEN-сокетов SO_REUSEPORT.

На этом рисунке sk1 — первый LISTEN-сокет, тогда как sk2 и sk3 — сокеты, которые вызвали listen() позже. Два описанных выше шага выполняются в следующем фрагменте кода и исполняются по цепочке вызова listen():

```c
int reuseport_add_sock(struct sock *sk, struct sock *sk2)
{
    struct sock_reuseport *reuseport = sk2->sk_reuseport_cb;

    if (reuseport->num_socks == reuseport->max_socks) {
        reuseport = more_reuseport_entries(reuseport);
        if (!reuseport)
            return -ENOMEM;
    }
    reuseport->socks[reuseport->num_socks] = sk;
    sk->sk_reuseport_cb = reuseport;  /* указывает на общий sk_reuseport_cb */
    reuseport->num_socks++;
    return 0;
}
```

Теперь давайте поймём, как reuseport_select_sock() выбирает LISTEN-сокет. reuseport_select_sock() просто индексирует массив socks[] через вызов reciprocal_scale() следующим образом:

```c
index = reciprocal_scale(phash, reuseport->num_socks);
```

reciprocal_scale() [8] — это оптимизированная функция, реализующая псевдооперацию взятия остатка по модулю с использованием операций умножения и сдвига.

Как мы видели ранее, phash вычисляется в __inet_lookup_listener():

```c
phash = inet_ehashfn(dst_addr, dst_port, src_addr, src_port);
```

а num_socks — это количество сокетов в массиве socks[]. Функция reciprocal_scale(phash, num_socks) вычисляет индекс, 0 <= index < num_socks. Этот индекс используется для получения сокета из группы сокетов SO_REUSEPORT. Отсюда мы видим, что ядро выбирает сокет, хешируя значения IP:port клиента и IP:port сервера. Этот метод обеспечивает хорошее распределение соединений между различными LISTEN-сокетами.

## SO_REUSEPORT в действии

Давайте посмотрим на эффект SO_REUSEPORT в командной строке с помощью двух тестов.

1. Приложение открывает сокет для прослушивания и создаёт два процесса. Путь кода приложения: socket(); bind(); listen(); fork();

2. Приложение создаёт два процесса, и каждый создаёт LISTEN-сокет после установки SO_REUSEPORT. Путь кода приложения: fork(); socket(); setsockopt(SO_REUSEPORT); bind(); listen()

Давайте посмотрим на состояние сокета без SO_REUSEPORT:

```text
$ sudo ss --tcp -tina 'sport = :45000'
State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN  0       5       0.0.0.0:45000        0.0.0.0:*           users:(("my_server",ino:3854904087,sk:37d5a0))
```

Строка «ino:3854904087 sk:37d5a0» описывает один сокет ядра.

Давайте посмотрим на состояние сокета с SO_REUSEPORT:

```text
$ sudo ss --tcp -tina 'sport = :45000'
State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN  0       5       0.0.0.0:45000        0.0.0.0:*           users:(("my_server",ino:3854912345,sk:37d6c0))
LISTEN  0       5       0.0.0.0:45000        0.0.0.0:*           users:(("my_server",ino:3854912789,sk:37d8a0))
```

Теперь мы видим два разных сокета ядра — обратите внимание на разные номера inode.

Приложения, использующие несколько процессов для приёма соединений на одном LISTEN-сокете, могут столкнуться с существенными проблемами производительности, поскольку каждый процесс конкурирует за одну и ту же блокировку сокета в accept(), как показано в следующем упрощённом псевдокоде:

```text
accept() {
    lock_sock(sk);                    /* конкуренция за одну блокировку */
    newsk = dequeue_from_accept_queue(sk);
    release_sock(sk);
    return newsk;
}
```

Обе функции lock_sock() и release_sock() внутри себя захватывают и освобождают спинлок, встроенный в sk. См. Рисунок 4 далее в статье, чтобы наблюдать накладные расходы из-за конкуренции за спинлок.

## Бенчмаркинг SO_REUSEPORT

Следующая конфигурация используется для измерения производительности SO_REUSEPORT:

* Версия ядра: 4.17.13.

* Клиентская и серверная системы обе имеют 48 ядер с гиперпоточностью и соединены друг с другом через 40g NIC через коммутатор.

* Сервер запускается одним из двух способов:

1. Создать один LISTEN-сокет и сделать fork 48 раз; или

2. Сделать fork 48 раз, и каждый дочерний процесс создаёт LISTEN-сокет после включения SO_REUSEPORT.

* Клиент создаёт 48 процессов. Каждый процесс подключается и отключается от сервера миллион раз последовательно.

* Исходный код клиентского и серверного приложений приведён в конце этой статьи.

```text
With fork of the LISTEN socket
server-system-$ ./my_server 45000 48 0   # 0 означает fork() LISTEN-сокета
client-system-$ time ./my_client <server-ip> 45000 48 1000000
real 4m45.471s

With SO_REUSEPORT
server-system-$ ./my_server 45000 48 1   # 1 означает SO_REUSEPORT
client-system-$ time ./my_client <server-ip> 45000 48 1000000
real 1m36.766s
```

## Анализ производительности SO_REUSEPORT

Давайте взглянем на профиль производительности для этих двух тестов с помощью инструмента perf [9]. Рисунки 3 и 4 показывают статистику аппаратных счётчиков производительности и профиль ядра для вышеуказанного теста без использования SO_REUSEPORT.

![](/images/eb28061f04b43f27a6d8f04671552347.png)

Рисунок 3. Статистика счётчиков производительности без SO_REUSEPORT.

![](/images/8713a5af12cad8bd1a2f33d0e0278344.png)

Рисунок 4. Профиль производительности топ-25 функций без SO_REUSEPORT.

Рисунки 5 и 6 показывают статистику аппаратных счётчиков производительности и профиль ядра для вышеуказанного теста с использованием SO_REUSEPORT.

![](/images/d65dece4bc5753ecdd8e05d5359efd8e.png)

Рисунок 5. Статистика счётчиков производительности с SO_REUSEPORT.

![](/images/98b2b02ea3c041c256c0e65dc848e257.png)

Рисунок 6. Профиль производительности топ-25 функций с SO_REUSEPORT.

## Исходный код клиентского и серверного приложений

Листинг ниже реализует серверное и клиентское приложения, которые использовались для тестирования производительности SO_REUSEPORT.

Серверная программа:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int server_port;
int num_procs;
int enable_reuseport;

int main(int argc, char **argv)
{
    int server_fd, client_fd;
    struct sockaddr_in server_addr;
    int sock_opt = 1;
    int i;

    if (argc != 4) {
        printf("Usage: %s <port> <num_procs> <reuseport: 0|1>\n", argv[0]);
        return 1;
    }
    server_port = atoi(argv[1]);
    num_procs = atoi(argv[2]);
    enable_reuseport = atoi(argv[3]);

    if (enable_reuseport) {
        /* создать сокет и слушать в каждом дочернем процессе */
        for (i = 0; i < num_procs; i++)
            if (fork() == 0)
                break;
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT,
                       &sock_opt, sizeof(sock_opt)) < 0)
            error("setsockopt(SO_REUSEPORT) failed");
    } else {
        /* единственный сокет, который слушают все дочерние процессы */
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        listen(server_fd);
        for (i = 0; i < num_procs; i++)
            if (fork() == 0)
                break;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(server_port);

    bind(server_fd, (struct sockaddr *)&server_addr,
         sizeof(server_addr));
    listen(server_fd, 5);

    while (1) {
        client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0)
            continue;
        close(client_fd); /* соединения закрываются сразу же */
    }
    return 0;
}
```

Клиентская программа:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc, char **argv)
{
    int client_fd, i, j;
    struct sockaddr_in server_addr;

    if (argc != 5) {
        printf("Usage: %s <ip> <port> <num_procs> <num_conns>\n", argv[0]);
        return 1;
    }
    for (i = 0; i < atoi(argv[3]); i++)
        if (fork() == 0)
            break;

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);
    server_addr.sin_port = htons(atoi(argv[2]));

    for (j = 0; j < atoi(argv[4]); j++) {
        client_fd = socket(AF_INET, SOCK_STREAM, 0);
        connect(client_fd, (struct sockaddr *)&server_addr,
                sizeof(server_addr));
        close(client_fd);
    }
    return 0;
}
```

## Ссылки

[1] https://lwn.net/Articles/542629/
[2] https://en.wikipedia.org/wiki/Network_socket
[3] https://en.wikipedia.org/wiki/Transmission_Control_Protocol
[4] TCP State Transition diagram: https://en.wikipedia.org/wiki/File:Tcp_state_diagram.png
[5] Kernel source code: https://elixir.bootlin.com/linux/v4.17.13/source
[6] https://www.amazon.com/Unix-Network-Programming-Sockets-Networking/dp/0131411551/
[7] https://gcc.gnu.org/onlinedocs/gcc/Zero-Length.html
[8] http://homepage.cs.uiowa.edu/~jones/bcd/divide.html
[9] https://perf.wiki.kernel.org/index.php/Tutorial

**********

[tcp](/tags/tcp.md)
[sockets](/tags/sockets.md)
[linux](/tags/linux.md)