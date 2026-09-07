# Сокеты в ядре Linux — Часть 3: поиск TCP-сокета на приёме

Источник: [Sockets in the Linux Kernel - Part 3: TCP Socket Lookup on Rx — разбор поиска сокета для входящих TCP-пакетов в Linux v6.12: IPv4/IPv6 Rx path, `struct socket`, `struct sock`, `tcp_hashinfo`, `ehash`/`lhash2`, `__inet_lookup()` и пример TCP server socket.](https://thermalcircle.de/doku.php?id=blog%3Alinux%3Asockets_in_the_linux_kernel_3_tcp_socket_lookup_on_rx)

Andrej Stender · опубликовано 6 января 2026 · последнее изменение 6 января 2026

В этой серии статей я исследую реализацию сокетов в ядре Linux и окружающий их исходный код. В то время как большинство моих предыдущих статей фокусировались в первую очередь на уровне 3 OSI, эта серия попытается нырнуть на уровень 4 OSI. Читателям исходного кода ядра из-за sheer сложности очень легко не видеть леса за деревьями. Моё намерение — бросить здесь спасательный круг, чтобы помочь ориентироваться в коде и удержаться за существенное.

## Статьи серии

* [Sockets in the Linux Kernel - Part 1: L4 Protocol Demux on Rx](https://thermalcircle.de/doku.php?id=blog:linux:sockets_in_the_linux_kernel_1_l4prot_demux_on_rx "blog:linux:sockets_in_the_linux_kernel_1_l4prot_demux_on_rx")

* [Sockets in the Linux Kernel - Part 2: UDP Socket Lookup on Rx](https://thermalcircle.de/doku.php?id=blog:linux:sockets_in_the_linux_kernel_2_udp_socket_lookup_on_rx "blog:linux:sockets_in_the_linux_kernel_2_udp_socket_lookup_on_rx")

* [Sockets in the Linux Kernel - Part 3: TCP Socket Lookup on Rx](https://thermalcircle.de/doku.php?id=blog:linux:sockets_in_the_linux_kernel_3_tcp_socket_lookup_on_rx "blog:linux:sockets_in_the_linux_kernel_3_tcp_socket_lookup_on_rx")

## Обзор

В этой 3-й статье серии я хочу углубиться в поиск сокета (socket lookup) для TCP-пакетов, который определяет, на каком сокете входящий TCP-пакет будет фактически принят и обработан. Хотя пути приёма для пакетов IPv4 и IPv6 существуют раздельно, поиск сокета и реализация протокола TCP в основном состоят из общих компонентов, используемых на обоих путях приёма. Общий принцип работы поиска в обоих случаях практически идентичен. Я пройдусь по общему потоку пакетов, по вовлечённым компонентам вроде структур сокетов и хеш-таблиц, и, наконец, по самому поиску сокета.

## Поток пакетов на приёме (Rx)

Рисунок 1 визуализирует путь приёма _unicast_-TCP-пакетов в ядре Linux, инкапсулированных в IPv4 или IPv6, от первоначального приёма пакета в драйвере NIC до обработки машиной состояний TCP, с особым фокусом на поиск сокета (1).

[![](/images/b354a56d029a8f6e9c85bc0abc063710.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:packet-flow-tcp-sock-lookup-rx-l3-l4.png "linux:packet-flow-tcp-sock-lookup-rx-l3-l4.png") Рисунок 1: Поток пакетов на пути приёма L2 → L3 → L4 для локально принимаемых TCP-пакетов с фокусом на поиск сокета.

В потоке пакетов, изображённом на рисунке 1, решение маршрутизации определяет, что IPv4/IPv6-пакет должен быть принят локально. На основании этого решения выполняется непрямой вызов обработчика локального приёма, который вызывает [`ip_local_deliver()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/ip_input.c#L242 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/ip_input.c#L242") в случае IPv4 и [`ip6_input()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/ip6_input.c#L488 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/ip6_input.c#L488") в случае IPv6. В обоих случаях пакет проходит через _Netfilter Input hook_ (2) и затем демультиплексируется (3) по протоколу L4, который он несёт. В данном случае пакет несёт TCP-сегмент, и поэтому в случае IPv4 вызывается функция [`tcp_v4_rcv()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L2176 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L2176"), а в случае IPv6 — [`tcp_v6_rcv()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/tcp_ipv6.c#L1742 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/tcp_ipv6.c#L1742"). Обе функции выполняют начальные проверки TCP-заголовка и контрольной суммы, а затем вызывают [`__inet_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L408 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L408") (IPv4) или [`__inet6_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L85 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L85") (IPv6) соответственно (4) — это и есть собственно поиск сокета. Обе реализации используют в качестве бэкенда две центральные хеш-таблицы, которые я подробно опишу в следующих разделах. Если найден подходящий сокет, пакет передаётся машине состояний TCP, которая обрабатывает его дальше и, в зависимости от деталей пакета и состояния соединения, добавляет его полезную нагрузку, если она есть, в буфер приёма этого сокета.

## Структуры сокетов

Прежде чем перейти к самому поиску сокета, я хочу провести вас по строительным блокам, которые здесь задействованы, — прежде всего по самим сокетам. В ядре они представлены сложной объектно-ориентированной иерархией структур. Реализация — глубокая кроличья нора, и я опущусь здесь лишь настолько глубоко, насколько необходимо.

[![](/images/4ca3bb663c3bf935d1ca42fa0a2b11f4.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcpsocket_structs_ipv4_1.png "linux:tcpsocket_structs_ipv4_1.png") Рисунок 2: Упрощённый пример экземпляра IPv4 TCP _listening socket_ (слушающего сокета) или _child socket_ (дочернего сокета).

Рисунок 2 показывает экземпляры структур, которые выделяются и инициализируются в ядре, когда вы используете системный вызов _[socket(2)](https://manpages.debian.org/bookworm/manpages-dev/socket.2.en.html "https://manpages.debian.org/bookworm/manpages-dev/socket.2.en.html")_ для создания TCP-сокета в домене IPv4, затем системный вызов _[bind(2)](https://manpages.debian.org/bookworm/manpages-dev/bind.2.en.html "https://manpages.debian.org/bookworm/manpages-dev/bind.2.en.html")_ для привязки сокета к локальному IPv4-адресу и порту, и затем системный вызов _[listen(2)](https://manpages.debian.org/bookworm/manpages-dev/listen.2.en.html "https://manpages.debian.org/bookworm/manpages-dev/listen.2.en.html")_ для перевода сокета в режим прослушивания привязанного адреса и порта. Все задействованные структуры сокетов ядра имеют куда больше переменных-членов, чем показано на рисунке 2 и других рисунках этого раздела. Я показываю здесь только те, которые считаю релевантными для текущей темы. Итак, пройдём по этому примеру: системный вызов _socket(2)_, представленный в ядре в первую очередь функцией [`__sys_socket()`](https://elixir.bootlin.com/linux/v6.12/source/net/socket.c#L1711 "https://elixir.bootlin.com/linux/v6.12/source/net/socket.c#L1711"), выделяет экземпляр [`struct socket`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/net.h#L107 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/net.h#L107") и экземпляр [`struct tcp_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L192 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L192") (5), которые содержат указатели друг на друга. Последний включает иерархию под-структур [`struct inet_connection_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_connection_sock.h#L82 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_connection_sock.h#L82"), [`struct inet_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L210 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L210"), [`struct sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L237 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L237") и [`struct sock_common`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105"), как показано на рисунке 2. Системный вызов _bind(2)_, представленный в ядре в первую очередь функцией [`inet_bind()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L467 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L467") (в случае IPv4), привязывает здесь сокет к `127.0.0.1:8080` и сохраняет этот IP-адрес в переменной-члене [`skc_rcv_saddr`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L155 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L155"), а порт `8080` — в переменной-члене [`skc_num`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167"). Системный вызов _listen(2)_, представленный в ядре в первую очередь функцией [`inet_listen()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L230 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L230") (в случае TCP), переводит здесь сокет в состояние прослушивания, изменяя его состояние и добавляя его в хеш-таблицу (подробнее об этом в разделе ниже).

Имейте в виду: к этим переменным-членам в разных частях кода часто обращаются под несколькими разными именами-псевдонимами вместо их настоящего имени. У большинства структур этой иерархии есть набор define-ов препроцессора, служащих псевдонимами или «сокращениями» для доступа к переменным-членам структур, находящихся ниже в иерархии. См., например, [этот список define-ов](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L348 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L348"), являющийся частью _struct sock_. В этой статье я всегда буду использовать настоящее имя, а не один из псевдонимов, когда ссылаюсь на переменную-член.

[![](/images/cee44fca76b06d6c1d622e9dc67d0e8b.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcpsocket_structs_ipv6_1.png "linux:tcpsocket_structs_ipv6_1.png") Рисунок 3: Упрощённый пример экземпляра IPv6 TCP _listening socket_ или _child socket_.

Рисунок 3 показывает тот же самый пример, что и рисунок 2, но на этот раз для TCP-сокета в домене IPv6. На нём показаны экземпляры структур, выделяемые и инициализируемые в ядре при использовании системных вызовов _socket(2)_, _bind(2)_ и _listen(2)_ так же, как описано выше, только с IPv6-адресами. Пройдём по этому IPv6-варианту примера: системный вызов _socket(2)_ выделяет экземпляр [`struct socket`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/net.h#L107 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/net.h#L107") и экземпляр [`struct tcp6_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L305 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L305"), которые содержат указатели друг на друга. Последний включает почти ту же иерархию под-структур, что и в примере IPv4 TCP. [`struct tcp6_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L305 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L305") просто действует как обёртка вокруг исходной иерархии из [`struct tcp_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L192 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L192"), [`struct inet_connection_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_connection_sock.h#L82 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_connection_sock.h#L82"), [`struct inet_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L190 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L190"), [`struct sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L237 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L237") и [`struct sock_common`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105") и добавляет дополнительный [`struct ip6_pinfo`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L213 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L213"). Системный вызов _bind(2)_, представленный в ядре функцией [`inet6_bind()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/af_inet6.c#L470 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/af_inet6.c#L470") (в случае IPv6), привязывает здесь сокет к `[2001:db8::1]:8080` и сохраняет этот IP-адрес в переменной-члене [`skc_v6_rcv_saddr`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L187 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L187"). Порт `8080` он сохраняет в члене [`skc_num`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167"). Системный вызов _listen(2)_, как и в случае IPv4, добавляет сокет в хеш-таблицу и изменяет его состояние (я к этому ещё вернусь).

[![](/images/ba6411c183820ababf38ee956c6410a8.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcpreq_structs_ipv4_1.png "linux:tcpreq_structs_ipv4_1.png") Рисунок 4: Упрощённый пример экземпляра IPv4 TCP _request socket_ (сокета запроса).  [![](/images/fbe377f98d937444c9df72e47dfc8456.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcpreq_structs_ipv6_1.png "linux:tcpreq_structs_ipv6_1.png") Рисунок 5: Упрощённый пример экземпляра IPv6 TCP _request socket_.

Так что же это за «сокеты запросов» (request sockets), показанные на рисунках 4 и 5? Это «облегчённые» (lightweight) TCP-сокеты, которые используются для представления новых запросов на соединение во время TCP-квитирования (3-way handshake). Полноценные TCP-сокеты, показанные на рисунках 2 и 3, используются только как _слушающие сокеты_ (listening sockets) или как сокеты, представляющие _установленные соединения_ (established connections). Во время TCP-квитирования, а также во время TCP FIN-квитирования вместо них используются «облегчённые» сокеты. Те, что применяются в FIN-квитировании, я здесь объяснять не буду. TCP _сокет запроса_ создаётся, когда от клиента-пира получен первый TCP SYN-пакет. В случае IPv4 он состоит из иерархии структур [`tcp_request_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L149 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L149"), [`inet_request_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L68 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_sock.h#L68"), [`struct request_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/net/request_sock.h#L55 "https://elixir.bootlin.com/linux/v6.12/source/include/net/request_sock.h#L55") и [`struct sock_common`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L105"), см. снова рисунок 4. В случае IPv6 он состоит из точно такой же иерархии структур, только всё это обёрнуто сверху в экземпляр [`struct tcp6_request_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L198 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/ipv6.h#L198"), см. рисунок 5.

**TCP Syncookies**

Это функция, которая делает обработку новых запросов на соединение, получаемых на слушающем TCP-сокете, ещё более «облегчённой», вообще не используя «сокеты запросов» или другие виды экземпляров сокетов во время 3-way handshake. _Syncookies_ обычно применяются, когда очередь accept-ов TCP уже заполнена. Подробнее я их в этой статье рассматривать не буду.

## Хеш-таблицы TCP

[![](/images/fc06726d096e8bc5d8d8d6a1b0a030ab.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_hashinfo1.png "linux:tcp_hashinfo1.png") Рисунок 6: Глобальный экземпляр _struct inet_hashinfo_ с именем _tcp_hashinfo_, содержащий хеш-таблицы TCP; таблицы _*ehash_ и _*lhash2_ используются в поиске сокета.

Хеш-таблицы, которые используются для хранения TCP-сокетов, размещены в глобальном экземпляре [`struct inet_hashinfo`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L144 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L144") с именем [`tcp_hashinfo`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L94 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L94"), члены которого выделяются и инициализируются в функции [`tcp_init()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5054 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5054") и расположенных ниже функциях на ранней загрузке ядра; см. рисунок 6. Эта структура фактически содержит 4 различные хеш-таблицы: [`ehash`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L151 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L151"), [`bhash`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L161 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L161"), [`bhash2`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L167 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L167") и [`lhash2`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L172 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L172"). Таблицы `bhash` и `bhash2` используются для управления сокетами, связанного с системным вызовом _bind()_, и на самом деле не содержат экземпляры сокетов. Они не важны для рамок этой статьи. Таблицы `ehash` и `lhash2` действительно содержат экземпляры сокетов и используются в поиске TCP-сокета, поэтому именно они — наш главный фокус здесь. В то время как `lhash2` содержит сокеты в состоянии `TCP_LISTEN` (слушающие сокеты), `ehash` содержит сокеты во всех остальных состояниях (сокеты, представляющие реальные TCP-соединения). Элементы («бакеты» — buckets, или иногда их также называют «слоты» — slots) таблицы `ehash` имеют тип [`struct inet_ehash_bucket`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L39 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L39"), который занимает 8 байт памяти и содержит указатель _head_ на связный список. Элементы `lhash2` имеют тип [`struct inet_listen_hashbucket`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L136 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L136"), который занимает 16 байт памяти и дополнительно содержит спинлок. По умолчанию число элементов обеих таблиц определяется динамически при выделении на основе объёма памяти в системе. Для `ehash` создаётся один элемент на каждые [128 КБ](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5096 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5096") памяти в системе, с жёстким лимитом в [2^19](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5101 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5101") элементов. Для `lhash2` создаётся один элемент на каждые [2 МБ](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5072 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5072") памяти в системе, с жёстким лимитом в [2^16](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5073 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp.c#L5073") элементов. На одной из моих систем с 32 ГБ оперативной памяти я наблюдал, что `ehash` обладает 2^18 = 262144 элементами (6), а `lhash2` — 2^14 = 16384 элементами (7). Размер выделенной памяти и число элементов обеих таблиц легко наблюдать с помощью [сообщения в журнале](https://elixir.bootlin.com/linux/v6.12/source/mm/mm_init.c#L2430 "https://elixir.bootlin.com/linux/v6.12/source/mm/mm_init.c#L2430") на ранней загрузке, которое появляется в ваших журналах _dmesg_ и _journald_ (8):

```bash
$ journalctl -b 0 -k -g 'TCP established'
TCP established hash table entries: 262144 (order: 9, 2097152 bytes, linear)
# meaning:
# 262144 buckets in *ehash  a 8 byte = 2097152 byte

$ journalctl -b 0 -k -g 'tcp_listen_portaddr_hash'
tcp_listen_portaddr_hash hash table entries: 16384 (order: 6, 262144 bytes, linear)
# meaning:
# 16384 buckets in *lhash2  a 16 byte = 262144 byte
```

Кроме того, (только для чтения) _sysctl_ `tcp_ehash_entries` также может показать вам то же самое число элементов для `ehash`. Похоже, эквивалента для `lhash2` не существует:

```bash
$ sudo sysctl net.ipv4.tcp_ehash_entries
net.ipv4.tcp_ehash_entries = 262144
```

Я опишу более подробно в следующем разделе, как эти таблицы фактически используются. Пока лишь констатируем, что обе таблицы вместе содержат все сокеты, которые могут быть сопоставлены во время поиска TCP-сокета с локально принятым пакетом. Это включает TCP/IPv4-сокеты, а также TCP/IPv6-сокеты и по умолчанию также сокеты всех _[сетевых пространств имён](https://manpages.debian.org/bookworm/manpages/network_namespaces.7.en.html "https://manpages.debian.org/bookworm/manpages/network_namespaces.7.en.html")_ (network namespaces).

**Опция: сетевое пространство имён с индивидуальным экземпляром таблицы _ehash_**

Как упомянуто выше, по умолчанию существует только один глобальный экземпляр _struct inet_hashinfo_ с именем _[tcp_hashinfo](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L94 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L94")_, который содержит и таблицу _ehash_, и таблицу _lhash2_ и используется во всех сетевых пространствах имён. Каждое сетевое пространство имён хранит индивидуальный указатель на этот глобальный экземпляр в _[net->ipv4.tcp_death_row.hashinfo](https://elixir.bootlin.com/linux/v6.12/source/include/net/netns/ipv4.h#L83 "https://elixir.bootlin.com/linux/v6.12/source/include/net/netns/ipv4.h#L83")_. Этот указатель инициализируется в функции _[tcp_set_hashinfo()](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L3427 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L3427")_, которая вызывается в момент создания каждого сетевого пространства имён. Поиск сокета фактически использует именно этот указатель для доступа к _ehash_ и _lhash2_. Однако существует _sysctl_, который опционально позволяет сетевым пространствам имён выделять собственный индивидуальный экземпляр _ehash_ (но не _lhash2_!). Если эта функция активирована, то функция _tcp_set_hashinfo()_ создаёт новый экземпляр _struct inet_hashinfo_ индивидуально для каждого нового дочернего сетевого пространства имён и выделяет индивидуальный экземпляр таблицы _ehash_. Указатель _*lhash2_ в этой структуре, однако, продолжит указывать на глобальный экземпляр _lhash2_. Чтобы активировать это, вам нужно установить _sysctl_ _[net.ipv4.tcp_child_ehash_entries](https://elixir.bootlin.com/linux/v6.12/source/Documentation/networking/ip-sysctl.rst#L1103 "https://elixir.bootlin.com/linux/v6.12/source/Documentation/networking/ip-sysctl.rst#L1103")_ в число элементов, которое вы хотите выделить для _ehash_, а затем создать дочернее сетевое пространство имён. Это дочернее сетевое пространство имён затем выделит собственный экземпляр _ehash_ с настроенным числом элементов; см. снова функцию _[tcp_set_hashinfo()](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L3412 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L3412")_. Вы можете подтвердить это, прочитав _sysctl_ _[net.ipv4.tcp_ehash_entries](https://elixir.bootlin.com/linux/v6.12/source/Documentation/networking/ip-sysctl.rst#L1096 "https://elixir.bootlin.com/linux/v6.12/source/Documentation/networking/ip-sysctl.rst#L1096")_ внутри дочернего сетевого пространства имён. По умолчанию эта функция выключена, и задействованные _sysctls_ выглядят так (9):

```text
net.ipv4.tcp_child_ehash_entries = 0
net.ipv4.tcp_ehash_entries =  262144  # in main network namespace
net.ipv4.tcp_ehash_entries = -262144  # in other network namespaces
```

Если включить её и установить 1048576 (2^20) элементов, задействованные _sysctls_ будут выглядеть так:

```text
net.ipv4.tcp_child_ehash_entries = 1048576
net.ipv4.tcp_ehash_entries = 262144   # in main network namespace
net.ipv4.tcp_ehash_entries = 1048576  # in child network namespace
```

## Поиск сокета IPv4

Теперь мы наконец добрались до самого главного. Фактический поиск сокета для локально принимаемых IPv4 TCP-пакетов реализован в функции [`__inet_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L408 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L408") и визуализирован на рисунке 7. Он в первую очередь состоит из поиска в таблице `ehash`, реализованного в [`__inet_lookup_established()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L371 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L371"), за которым следуют два последовательных поиска в `lhash2`, реализованных в [`__inet_lookup_listener()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L426 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L426"). Хотя имена этих функций наводят на мысль, что поиск в `ehash` — это поиск установленных сокетов, а поиски в `lhash2` — поиски слушающих сокетов, реальность немного сложнее.

[![](/images/1160739952fb93d43d7cde7234940345.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_sock_lookup_v4_1.png "linux:tcp_sock_lookup_v4_1.png") Рисунок 7: Поиск сокета для IPv4 TCP-пакетов в деталях.

Как я уже упоминал в предыдущем разделе, `ehash` содержит сокеты, которые могут находиться во всех возможных состояниях машины состояний TCP, кроме `TCP_LISTEN`, в то время как `lhash2` содержит исключительно сокеты в состоянии `TCP_LISTEN`. Поиск в `ehash` выполняется на основе _кортежа из 4 элементов (4-tuple)_ принятого TCP-пакета, то есть его _srcIP + srcPort + dstIP + dstPort_. На основе этого вычисляется хеш (10). Другими словами, поиск в `ehash` может найти подходящий сокет, представляющий _TCP-соединение_, которое либо _установлено_, либо в данный момент находится в середине TCP-квитирования (3-way handshake) либо TCP-завершающего квитирования (FIN handshake). Поиск работает типичным для хеш-таблиц образом (11): вычисленный хеш служит индексом массива в `ehash` и тем самым определяет правильный бакет/слот в таблице. Затем код в цикле проходит по связному списку всех экземпляров сокетов, находящихся в этом бакете/слоте, сравнивая _4-tuple_ и _netns_ пакета с каждым сокетом, чтобы найти совпадающий. Это делается функцией [`inet_match()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L354 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L354"). Здесь для сравнения используются переменные-члены сокета `sk_net`, `skc_rcv_saddr`, `skc_num`, `skc_daddr` и `skc_dport`, см. снова рисунок 2. Если подходящий сокет найден, весь поиск на этом завершается. Иначе код переходит к поискам в `lhash2`. Как показано на рисунке 7, между ними происходит опциональный eBPF-поиск, см. [`inet_lookup_run_sk_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L404 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L404"). По умолчанию это no-op, и вы можете его игнорировать. Подробнее об этом опциональном поиске см. в инфобоксе ниже. Теперь выполняется поиск в `lhash2` на основе _кортежа из 2 элементов (2-tuple)_, состоящего из _dstIP_ и _dstPort_ принятого пакета. Вычисляется хеш на основе _2-tuple_ и _netns_ для определения бакета/слота, и затем код использует функцию [`inet_lhash2_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L377 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L377") для прохода по сокетам связного списка этого бакета/слота. Этот поиск способен найти подходящий слушающий сокет, привязанный к конкретному локальному IP-адресу и порту. Если совпадение не найдено, выполняется ещё один поиск в `lhash2`, на этот раз на основе _2-tuple_, состоящего из _IP-адреса «любой» (0.0.0.0)_ и _dstPort_ принятого пакета. Очевидно, что этот поиск способен найти подходящий слушающий сокет, привязанный к «любому» IP-адресу и конкретному порту. Из последовательности выполняемых здесь поисков ясно видно, что совпадения с сокетами, представляющими реальные TCP-соединения на основе _4-tuple_, имеют приоритет над совпадениями со слушающими сокетами, привязанными к конкретным адресам, которые, в свою очередь, имеют приоритет над совпадениями со слушающими сокетами, привязанными к «любому» адресу.

**eBPF sk_lookup**

Как показано на рисунке 7, eBPF-программа может быть загружена в ядро для выполнения на этом хуке _sk_lookup_. Это можно использовать, чтобы переопределить обычный поиск сокета и выбрать целевой сокет для приёма сетевого пакета на основе иных критериев, чем критерии по умолчанию, покрываемые обычным поиском. Первоначальный поиск на основе _4-tuple_ в таблицу _ehash_ всё равно выполняется до этого eBPF-хука и тем самым имеет приоритет. Другими словами, eBPF-поиск не может переопределить обычный поиск для сокетов, представляющих существующие (установленные) TCP-соединения. Он может использоваться только для переопределения поисков _слушающих_ сокетов. EBPF-программа, загруженная в этот хук, загружается в указанное сетевое пространство имён. Другими словами, каждое сетевое пространство имён имеет здесь собственный индивидуальный eBPF-хук. Я собрал несколько полезных ссылок для тех, кто хочет углубиться в эту тему:

* [kernel.org: BPF sk_lookup program](https://www.kernel.org/doc/html/v6.12/bpf/prog_sk_lookup.html "https://www.kernel.org/doc/html/v6.12/bpf/prog_sk_lookup.html")

* [docs.ebpf.io: Program type BPF_PROG_TYPE_SK_LOOKUP](https://docs.ebpf.io/linux/program-type/BPF_PROG_TYPE_SK_LOOKUP/ "https://docs.ebpf.io/linux/program-type/BPF_PROG_TYPE_SK_LOOKUP/")

* [blog.cloudflare.com: It's crowded in here!](https://blog.cloudflare.com/its-crowded-in-here/ "https://blog.cloudflare.com/its-crowded-in-here/")

* [youtu.be: Steering connections to sockets with BPF socket lookup hook](https://youtu.be/vCJ8kDYI8ZE "https://youtu.be/vCJ8kDYI8ZE")

## Поиск сокета IPv6

Поиск сокета для локально принимаемых IPv6 TCP-пакетов, изображённый на рисунке 8, на самом деле работает точно так же, как его IPv4-аналог, описанный в предыдущем разделе. Он просто реализован в отдельном наборе функций. Весь поиск выполняется в [`__inet6_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L85 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L85"). Эта функция вызывает [`__inet6_lookup_established()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L49 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L49") для поиска в `ehash`, а затем [`__inet6_lookup_listener()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L202 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L202") для поисков в `lhash2`, включая опциональный eBPF-поиск, который здесь реализован в [`inet6_lookup_run_sk_lookup()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L177 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv6/inet6_hashtables.c#L177").

[![](/images/e8a99f2218d5800d1989fc7302c00709.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_sock_lookup_v6_1.png "linux:tcp_sock_lookup_v6_1.png") Рисунок 8: Поиск сокета для IPv6 TCP-пакетов в деталях.

Есть лишь крошечное отличие от IPv4: поскольку эти поиски основаны на IPv6-, а не IPv4-адресах, а IPv6-адреса хранятся в других переменных-членах экземпляров сокетов, здесь вместо их IPv4-аналогов используются эти другие члены: [`skc_v6_rcv_saddr`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L187 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L187") и [`skc_v6_daddr`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L186 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L186"), см. снова рисунок 3.

## Пример: TCP-сокет сервера

Давайте пройдём по начальным шагам «пассивного открытия» (passive open) IPv4 TCP-сокета: мы создаём новый TCP-сокет, который хотим использовать как _слушающий сокет_ в TCP-серверном приложении. После создания мы привязываем его к локальному _адресу_ и _порту_ и переводим его в режим прослушивания этого _адреса_ и _порта_. Как только мы получаем _TCP SYN_-пакет от клиента, совпадающий с нашим слушающим сокетом, создаётся _сокет запроса_ (request socket), и при успешном завершении TCP-квитирования этот _сокет запроса_ замещается новым полноценным TCP-сокетом, представляющим теперь установленное TCP-соединение. Его обычно называют «дочерним сокетом» (child socket). Проходя по этим шагам, давайте сосредоточимся на задействованных экземплярах сокетов, их состояниях, о том, в каких хеш-таблицах они находятся и что это означает для поиска сокета, который выполняется для каждого пакета, получаемого от клиента-пира.

### (1) Системный вызов socket()

```text
# socket() syscall, shown here in strace style
socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
```

Мы используем системный вызов [`socket()`](https://manpages.debian.org/trixie/manpages-dev/socket.2.en.html "https://manpages.debian.org/trixie/manpages-dev/socket.2.en.html") для создания нового TCP-сокета. Основные шаги этого системного вызова выполняются в функциях [`__sock_create()`](https://elixir.bootlin.com/linux/v6.12/source/net/socket.c#L1490 "https://elixir.bootlin.com/linux/v6.12/source/net/socket.c#L1490"), [`inet_create()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L252 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L252") (12) и [`tcp_v4_init_sock()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L2489 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_ipv4.c#L2489") (13): создаётся экземпляр всей иерархии структур, показанной на рисунке 2 выше; см. рисунок 9. Состояние этого нового сокета пока устанавливается в [`TCP_CLOSE`](https://elixir.bootlin.com/linux/v6.12/source/include/net/tcp_states.h#L19 "https://elixir.bootlin.com/linux/v6.12/source/include/net/tcp_states.h#L19"). Он ещё не добавлен ни в какую хеш-таблицу. Вместо этого системный вызов возвращает вызывающей стороне в пользовательском пространстве _файловый дескриптор_ (здесь: `3`), который служит ссылкой.

![](/images/42698a3bdbddb7ec57d3fbc1359b8af7.png) Рисунок 9: Новый экземпляр `struct tcp_sock`, созданный системным вызовом `socket()`. Начальное состояние — `TCP_CLOSE`.

### (2) Системный вызов bind()

```text
bind(3, {sa_family=AF_INET, sin_port=htons(8080),
     sin_addr=inet_addr("127.0.0.1")}, 16) = 0
```

Мы используем системный вызов [`bind()`](https://manpages.debian.org/trixie/manpages-dev/bind.2.en.html "https://manpages.debian.org/trixie/manpages-dev/bind.2.en.html") для привязки нашего нового сокета к указанному локальному _адресу_ и _порту_ `127.0.0.1:8080`. Основные шаги этого системного вызова выполняются в [`__inet_bind()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L473 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L473") (14) и [`inet_csk_get_port()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L515 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L515") (15): в хеш-таблицы `bhash` и `bhash2` добавляются новые записи (16). Указанный локальный _адрес_ и _порт_ сохраняются в переменных-членах [`skc_rcv_saddr`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L155 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L155") и [`skc_num`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L167") сокета; см. рисунок 10.

![](/images/1ec8a34d1c37005dd9ecc5cbcf984fad.png) Рисунок 10: Системный вызов `bind()` привязывает сокет к `127.0.0.1:8080`.

### (3) Системный вызов listen()

```text
listen(3, 128) = 0
```

Затем мы вызываем системный вызов [`listen()`](https://manpages.debian.org/trixie/manpages-dev/listen.2.en.html "https://manpages.debian.org/trixie/manpages-dev/listen.2.en.html"). Основные шаги этого системного вызова выполняются в [`__inet_listen_sk()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L191 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/af_inet.c#L191"), [`inet_csk_listen_start()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1340 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1340") и [`__inet_hash()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L728 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L728") (17). Это помечает наш сокет как «пассивный» = переводит сокет в режим прослушивания привязанного локального _адреса_ и _порта_ для входящих TCP-соединений от других «активных» сокетов (клиентов). Он делает это, добавляя сокет в таблицу [`lhash2`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L754 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L754") и устанавливая его состояние в [`TCP_LISTEN`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1360 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1360"). Хеш, используемый как индекс в `lhash2`, вычисляется функцией [`ipv4_portaddr_hash()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L307 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L307") (18) на основе _сетевого пространства имён_ и _2-tuple_ из _адреса_ и _порта_ привязки. Указатели-коннекторы [`skc_node`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L211 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L211") (19) используются для добавления его в связный список правильного бакета таблицы; см. рисунок 11.

[![](/images/c546150870a29992d11d6c1de3026ed3.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_sock_listen2.png "linux:tcp_sock_listen2.png") Рисунок 11: Системный вызов `listen()` добавляет сокет в таблицу `lhash2` и устанавливает состояние в `TCP_LISTEN`.

### (4) Получен TCP SYN

Допустим, от клиента получен _TCP SYN_-пакет, и он совпадает со слушающим TCP-сокетом, который мы только что создали. Поиск TCP-сокета не находит совпадения среди сокетов в таблице `ehash`, но находит наш подходящий сокет в таблице `lhash2`; см. рисунок 12.

[![](/images/57efab1f2878123e85eb81ebbc3c859b.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_syn_rcv1.png "linux:tcp_syn_rcv1.png") Рисунок 12: Поиск TCP-сокета, выполненный в `__inet_lookup()` для полученного _TCP SYN_, находит наш подходящий слушающий сокет в `lhash2` на основе 2-tuple из _dstIP_ и _dstPort_ пакета.

Тем самым мы обнаружили новый запрос на соединение, и создаётся новый «сокет запроса». Для IPv4 это сокет типа [`struct tcp_request_sock`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L149 "https://elixir.bootlin.com/linux/v6.12/source/include/linux/tcp.h#L149"). См. рисунок 13. Рисунок 4 выше показывает его внутреннюю структуру в деталях. Его цель — служить «облегчённым» сокетом, который представляет обнаруженный (и теперь идущий) запрос на соединение. _Кортеж из 4 элементов_, состоящий из _srcIP:srcPort + dstIP:dstPort_ полученного _TCP SYN_-пакета, сохраняется в его переменных-членах. Его состояние устанавливается в `TCP_NEW_SYN_RECV`. Член [`skc_listener`](https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L199 "https://elixir.bootlin.com/linux/v6.12/source/include/net/sock.h#L199") делается указывающим на наш слушающий сокет, с которым совпал поиск сокета для пакета.

[![](/images/6bf2808d150c7a306d0b6999bced0dfd.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_syn_rcv2.png "linux:tcp_syn_rcv2.png") Рисунок 13: Создаётся экземпляр `struct tcp_request_sock`, содержащий _4-tuple_ полученного _TCP SYN_.

После инициализации новый _сокет запроса_ добавляется в таблицу `ehash` функцией [`inet_ehash_insert()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L656 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L656"); см. рисунок 14. Хеш, используемый как индекс в `ehash`, вычисляется функцией [`inet_ehashfn()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L55 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L55") на основе _сетевого пространства имён_ и _4-tuple_, сохранённого в _сокете запроса_. Указатели-коннекторы `skc_node` _сокета запроса_ используются для добавления его в связный список правильного бакета таблицы. Наконец, обратно клиенту отправляется ответный TCP-пакет _SYN+ACK_.

[![](/images/0010dc1ac25b08673546a49a5efbfa4a.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_syn_rcv3.png "linux:tcp_syn_rcv3.png") Рисунок 14: TCP-сокет запроса добавляется в таблицу `ehash`.

### (5) Получен TCP SYN (второй)

Допустим, теперь от того же клиента получен ещё один _TCP SYN_-пакет. Это, возможно, не самый частый случай, так как в данный момент мы ждём, что клиент отправит нам _TCP ACK_ для завершения 3-way handshake. Однако такое может случиться, так как этот 2-й _TCP SYN_ может быть, например, ретрансмиссией, если наш _SYN ACK_-ответ потерялся по пути к клиенту. Интересно рассмотреть этот случай, чтобы увидеть, как здесь используется _сокет запроса_: в этот момент и _сокет запроса_, и наш исходный _слушающий сокет_ присутствуют в хеш-таблицах, как показано на рисунке 15. Поиск TCP-сокета находит наш _сокет запроса_ в таблице `ehash` на основе _4-tuple_ + _netns_ пакета и тем самым обнаруживает, что полученный пакет является частью идущего запроса на соединение. Большая часть обработки пакета после этого происходит в [`tcp_check_req()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L680 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L680") и [`tcp_rtx_synack()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_output.c#L4401 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_output.c#L4401"). В самом частом случае ядро здесь ещё раз ответит другим _TCP SYN ACK_ (20).

[![](/images/9d96f5ce33cf0b8c3cbd18ea7cfbb275.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_syn_rcv4.png "linux:tcp_syn_rcv4.png") Рисунок 15: Поиск TCP-сокета для 2-го _TCP SYN_, полученного во время квитирования, находит наш подходящий _сокет запроса_ в `ehash` на основе _4-tuple_ пакета.

### (6) Получен TCP ACK

Допустим теперь, что от того же клиента получен _TCP ACK_, завершающий TCP 3-way handshake. И _сокет запроса_, и наш исходный _слушающий сокет_ присутствуют в хеш-таблицах, как показано на рисунке 16. Поиск TCP-сокета находит наш _сокет запроса_ в таблице `ehash` на основе _4-tuple_ пакета (21) и тем самым обнаруживает, что полученный _TCP ACK_-пакет является частью идущего запроса на соединение.

[![](/images/de6c42d293e175739d1752db3fadfe1d.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_ack_rcv1.png "linux:tcp_ack_rcv1.png") Рисунок 16: Поиск TCP-сокета для полученного _TCP ACK_ находит наш подходящий _сокет запроса_ в `ehash` на основе _4-tuple_ пакета.

Большая часть обработки пакета, которая следует сейчас, выполняется в функции [`tcp_check_req()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L651 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L651") и расположенных ниже функциях. Выполняются дальнейшие проверки, и если пакет оказывается валидным, создаётся новый полноценный экземпляр TCP-сокета, который должен представлять установленное TCP-соединение. Этот новый экземпляр `struct tcp_sock` клонируется из нашего слушающего сокета. Клонирование здесь означает, что большинство внутренних переменных-членов копируются в новый экземпляр. Соответственно, этот новый сокет обычно называют _дочерним сокетом_ (child socket — ребёнок _слушающего сокета_). Однако определённые переменные, такие как _4-tuple_, копируются из нашего _сокета запроса_. См. рисунок 17. Состояние этого нового сокета изначально устанавливается в [`TCP_SYN_RECV`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1254 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_connection_sock.c#L1254").

[![](/images/de0ffb31dadc1d4561c2da490148c5a4.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_ack_rcv2.png "linux:tcp_ack_rcv2.png") Рисунок 17: Новый `struct tcp_sock`, клонированный из _слушающего сокета_, _4-tuple_ взят из _сокета запроса_.

Затем _сокет запроса_ удаляется из таблицы `ehash` и замещается новосозданным _дочерним сокетом_. См. рисунок 18. Оставшаяся обработка теперь происходит ниже [`tcp_child_process()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L918 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_minisocks.c#L918"). Среди прочего состояние нового _дочернего сокета_ теперь меняется на [`TCP_ESTABLISHED`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_input.c#L6841 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/tcp_input.c#L6841").

[![](/images/725b4079e7984376a5b4201f0afc7576.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_ack_rcv3.png "linux:tcp_ack_rcv3.png") Рисунок 18: _Сокет запроса_ замещается новым _дочерним сокетом_ в таблице `ehash`.

### (7) Получен TCP PSH ACK

Если теперь мы получаем дальнейшие TCP-пакеты от клиента, например _TCP PSH ACK_ с данными, то поиск TCP-сокета теперь находит наш новый установленный _дочерний сокет_ в таблице `ehash` как совпадение на основе _4-tuple_; см. рисунок 19. Если все проверки проходят, машина состояний TCP затем доставляет полезную нагрузку пакета в буфер приёма _дочернего сокета_.

[![](/images/d9ff3cfb5e7c0241f28c5bf75c3cda97.png)](https://thermalcircle.de/lib/exe/fetch.php?media=linux:tcp_psh_ack_rcv1.png "linux:tcp_psh_ack_rcv1.png") Рисунок 19: Поиск TCP-сокета для полученного _TCP PSH ACK_ находит наш подходящий установленный _дочерний сокет_ в `ehash` на основе _4-tuple_ пакета.

### (8) Системный вызов accept()

Скорее всего, я немного расширю эту статью в ближайшем будущем, добавив детали о том, как работает _очередь accept-ов_ (accept queue) _слушающего_ TCP-сокета.

## Контекст

Эта статья описывает исходный код и поведение ядра Linux v6.12.

## Обратная связь

[Обратная связь](https://thermalcircle.de/doku.php?id=feedback "feedback") по этой статье очень приветствуется! Имейте в виду, что я не разрабатывал и не участвовал в создании ни одного из описанных здесь программных компонентов. Я лишь разработчик, который взглянул на исходный код и провёл некоторые практические эксперименты. Если вы найдёте что-то, что я, возможно, понял неправильно или описал здесь некорректно, я буду очень признателен, если вы обратите на это моё внимание, и, конечно же, я тогда как можно скорее исправлю свой контент соответствующим образом.

_опубликовано 6 января 2026_, _последнее изменение 6 января 2026_

1) Пожалуйста, сравните этот рисунок с его аналогами из моих предыдущих статей:
[Routing Decisions in the Linux Kernel - Part 1: Lookup and packet flow](https://thermalcircle.de/doku.php?id=blog:linux:routing_decisions_in_the_linux_kernel_1_lookup_packet_flow#packet_flow "blog:linux:routing_decisions_in_the_linux_kernel_1_lookup_packet_flow")
[Sockets in the Linux Kernel - Part 2: UDP Socket Lookup on Rx](https://thermalcircle.de/doku.php?id=blog:linux:sockets_in_the_linux_kernel_2_udp_socket_lookup_on_rx#rx_packet_flow "blog:linux:sockets_in_the_linux_kernel_2_udp_socket_lookup_on_rx")

2) Если быть точным: вариант _Input_-хука для IPv4 или IPv6, так как оба реализованы независимо.
См. мою статью [Nftables - Packet flow and Netfilter hooks in detail](https://thermalcircle.de/doku.php?id=blog:linux:nftables_packet_flow_netfilter_hooks_detail "blog:linux:nftables_packet_flow_netfilter_hooks_detail").

3) Подробнее см. мою статью [Sockets in the Linux Kernel - Part 1: L4 Protocol Demultiplexing on Rx](https://thermalcircle.de/doku.php?id=blog:linux:sockets_in_the_linux_kernel_1_l4prot_demux_on_rx#rx_packet_flow "blog:linux:sockets_in_the_linux_kernel_1_l4prot_demux_on_rx").

4) Согласен, здесь есть промежуточный слой функций [`__inet_lookup_skb()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L487 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L487") или [`__inet6_lookup_skb()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L146 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L146"), которые сначала вызывают [`inet_steal_sock()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L448 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet_hashtables.h#L448") или [`inet6_steal_sock()`](https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L107 "https://elixir.bootlin.com/linux/v6.12/source/include/net/inet6_hashtables.h#L107") соответственно. Однако это релевантно только в отношении функции _[early-demux](https://thermalcircle.de/doku.php?id=blog:linux:routing_decisions_in_the_linux_kernel_2_caching#socket_caching_rx "blog:linux:routing_decisions_in_the_linux_kernel_2_caching")_. Я не фокусируюсь на этом здесь.

5) Если быть точным, для этого обычно используется _slab cache_.

6) что логично для одного элемента на каждые 128 КБ: 32 ГБ = 32768 МБ * 8 = 262144

7) что логично для одного элемента на каждые 2 МБ: 32 ГБ = 32768 МБ / 2 = 16384

8) Да, конечно, размеры двух других хеш-таблиц `bhash` и `bhash2` вы тоже можете наблюдать таким образом:

```bash
$ journalctl -b 0 -k -g 'TCP bind'
TCP bind hash table entries: 65536 (order: 9, 2097152 bytes, linear)
# meaning:
# 65536 buckets in *bhash  a 16 byte
# 65536 buckets in *bhash2 a 16 byte
# 65536 * 32byte = 2097152 byte
```

9) взяв в качестве примера 262144 элемента, выделение которых я наблюдал здесь на своей системе

10) _Сетевое пространство имён_, в котором пакет был получен, также включается в вычисление хеша, так как таблица `ehash` — глобальная таблица, которая содержит сокеты из более чем одного (или всех) _сетевых пространств имён_. Поэтому различие между ними необходимо.

11) Если вам нужно освежить знания о том, как работают хеш-таблицы… Я более подробно описал внутреннее устройство хеш-таблицы системы _connection tracking_ ядра в своей статье [Connection tracking (conntrack) - Part 2: Core Implementation](https://thermalcircle.de/doku.php?id=blog:linux:connection_tracking_2_core_implementation#the_ct_table "blog:linux:connection_tracking_2_core_implementation").

12) , 14) в случае IPv4 (`AF_INET`)

13) , 15) , 17) в случае TCP (`SOCK_STREAM`)

16) Это просто замечание на полях, так как они нас в рамках этой статьи не касаются. Эти записи, кстати, не указатели на наш сокет, а связанные с ним данные управления.

18) В случае IPv6 использовалась бы эквивалентная функция [`ipv6_portaddr_hash()`](https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L302 "https://elixir.bootlin.com/linux/v6.12/source/net/ipv4/inet_hashtables.c#L302").

19) если быть точным, `skc_nulls_node`, так как это _union_

20) Есть функция безопасности, которая предотвращает отправку TCP SYN ACK-ответов, если TCP SYN-пакеты приходят с высокой частотой, так как это, скорее всего, была бы DOS-атака.

21) и _netns_ … я не буду больше упоминать это явно каждый раз

**********

[linux](/tags/linux.md)
[kernel](/tags/kernel.md)
[sockets](/tags/sockets.md)
[tcp](/tags/tcp.md)