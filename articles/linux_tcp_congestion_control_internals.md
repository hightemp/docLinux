# Внутреннее устройство управления перегрузкой TCP в Linux

Источник: [Linux TCP congestion control internals](https://www.yonch.com/tech/linux-tcp-congestion-control-internals)

Опубликовано 5 июля 2016 года, автор: yonch

В Linux применяется подключаемая архитектура управления перегрузкой TCP (congestion control): реализации IPv4 и IPv6 обе вызывают набор функций, реализующих управление перегрузкой. Алгоритм управления перегрузкой можно изменить системно для новых соединений или задать для отдельных сокетов с помощью setsockopt (подробнее [здесь](http://sgros.blogspot.com/2012/12/controlling-which-congestion-control.html)). Здесь мы рассмотрим, как реализация TCP взаимодействует с алгоритмами управления перегрузкой и …

Исследование основано на ядре v4.4.3

### Интерфейс управления перегрузкой

Интерфейс алгоритмов управления перегрузкой Linux определён в _struct tcp_congestion_ops._

```c
struct tcp_congestion_ops {
	struct list_head	list;
	u32 key;
	u32 flags;
	/* initialize private data (optional) */
	void (*init)(struct sock *sk);
	/* cleanup private data  (optional) */
	void (*release)(struct sock *sk);
	/* return slow start threshold (required) */
	u32 (*ssthresh)(struct sock *sk);
	/* do new cwnd calculation (required) */
	void (*cong_avoid)(struct sock *sk, u32 ack, u32 acked);
	/* call before changing ca_state (optional) */
	void (*set_state)(struct sock *sk, u8 new_state);
	/* call when cwnd event occurs (optional) */
	void (*cwnd_event)(struct sock *sk, enum tcp_ca_event ev);
	/* call when ack arrives (optional) */
	void (*in_ack_event)(struct sock *sk, u32 flags);
	/* new value of cwnd after loss (optional) */
	u32  (*undo_cwnd)(struct sock *sk);
	/* hook for packet ack accounting (optional) */
	void (*pkts_acked)(struct sock *sk, u32 num_acked, s32 rtt_us);
	/* get info for inet_diag (optional) */
	size_t (*get_info)(struct sock *sk, u32 ext, int *attr,
			   union tcp_cc_info *info);
	char 		name[TCP_CA_NAME_MAX];
	struct module 	*owner;
};
```

### Где хранится состояние управления перегрузкой

Ориентированные на соединения сокеты (struct inet_connection_sock) содержат фиксированный объём пространства для состояния управления перегрузкой в _icsk_ca_priv_:

```c
struct inet_connection_sock {
/* I removed some lines - JP */
	u64			  icsk_ca_priv[64 / sizeof(u64)];
#define ICSK_CA_PRIV_SIZE      (8 * sizeof(u64))
};
```

_inet_csk_ca(sk)_ получает указатель на это пространство по сокету:

```c
static inline void *inet_csk_ca(const struct sock *sk)
{
	return (void *)inet_csk(sk)->icsk_ca_priv;
}
```

### init и release

Инициализация запускается как часть трёхэтапного рукопожатия (SYN -> SYN+ACK -> ACK), когда:

  * На слушающем сокете, когда приходит пакет TCP fastopen «SYN» (_tcp_rcv_state_process -> icsk->icsk_af_ops->conn_request -> tcp_{v4,v6}_conn_request -> tcp_conn_request -> tcp_try_fastopen -> tcp_fastopen_create_child_).
  * В TCP-клиенте при получении «SYN+ACK» (вызывается через _tcp_rcv_state_process -> tcp_rcv_synsent_state_process -> tcp_finish_connect_).
  * В TCP-сервере при получении «ACK» (шаг 5 в _tcp_rcv_state_process_).

Или при смене алгоритма управления перегрузкой (_do_tcp_setsockopt -> tcp_set_congestion_control -> tcp_reinit_congestion_control_).

Release вызывается, когда setsockopt меняет алгоритмы, а также когда сокет закрывается (_tcp_v4_destroy_sock_, также вызывается для сокетов IPv6 из _tcp_v6_destroy_sock_).

### set_state и различные состояния TCP

Вызовы алгоритмов управления перегрузкой зависят от текущего состояния TCP-соединения и переходов между состояниями. Состояние TCP описано в _enum tcp_ca_state_:

```c
enum tcp_ca_state {
	TCP_CA_Open = 0,
#define TCPF_CA_Open	(1<<TCP_CA_Open)
	TCP_CA_Disorder = 1,
#define TCPF_CA_Disorder (1<<TCP_CA_Disorder)
	TCP_CA_CWR = 2,
#define TCPF_CA_CWR	(1<<TCP_CA_CWR)
	TCP_CA_Recovery = 3,
#define TCPF_CA_Recovery (1<<TCP_CA_Recovery)
	TCP_CA_Loss = 4
#define TCPF_CA_Loss	(1<<TCP_CA_Loss)
};
```

Функция _tcp_set_ca_state_ переключает состояния, сначала вызывая _set_state_ алгоритма управления перегрузкой, а затем устанавливая icsk->icsk_ca_state:

```c
static inline void tcp_set_ca_state(struct sock *sk, const u8 ca_state)
{
	struct inet_connection_sock *icsk = inet_csk(sk);
	if (icsk->icsk_ca_ops->set_state)
		icsk->icsk_ca_ops->set_state(sk, ca_state);
	icsk->icsk_ca_state = ca_state;
}
```

Такое расположение состояний и в enum, и в масках (TCPF_*) выше позволяет проверять побитовыми операциями, находится ли состояние сокета в некотором наборе состояний. Например:

```c
static inline bool tcp_in_cwnd_reduction(const struct sock *sk)
{
	return (TCPF_CA_CWR | TCPF_CA_Recovery) &
	       (1 << inet_csk(sk)->icsk_ca_state);
}
```

А чтобы охватить все состояния по степени серьёзности нарушения, можно сравнивать по числовому значению:

```c
		if (icsk->icsk_ca_state <= TCP_CA_Disorder)
			tcp_try_undo_dsack(sk);
```

### Состояние TCP-сокета

Состояние соответствует определениям из [RFC793](https://tools.ietf.org/html/rfc793):

```text
    Send Sequence Variables
      SND.UNA - send unacknowledged
      SND.NXT - send next
      SND.WND - send window
      SND.UP  - send urgent pointer
      SND.WL1 - segment sequence number used for last window update
      SND.WL2 - segment acknowledgment number used for last window
                update
      ISS     - initial send sequence number
    Receive Sequence Variables
      RCV.NXT - receive next
      RCV.WND - receive window
      RCV.UP  - receive urgent pointer
      IRS     - initial receive sequence number
```

Ниже перечислены некоторые важные переменные состояния. _tp->_ обозначает _struct tcp_sock_ (в include/linux/tcp.h). Переменные из RFC названы в нижнем регистре:

  * _tp->snd_nxt_: наибольший seq, отправленный «в провод»
  * tp->snd_wnd: окно пирингового узла
  * tp->snd_wl1: номер seq в момент, когда пир в последний раз обновил окно
  * _tp->rcv_nxt_: следующий ожидаемый к приёму порядковый номер. Используется в поле ACK исходящих пакетов.
  * _tp->rcv_wnd: размер окна, объявленный пиринговому узлу_

Другие важные переменные:

  * _tp->write_seq_: наибольший seq, записанный из пользовательского процесса
  * _tp->copied_seq_: порядковый номер, который следующим будет скопирован пользователю.
  * tp->rcv_wup: порядковый номер в момент, когда окно было объявлено пиру (подробнее ниже)
  * _tp->tlp_high_seq_: ноль, если проба [TLP](https://lwn.net/Articles/542642/) не отправлялась; устанавливается в _tp->snd_nxt_ при отправке пробы TLP.
  * _tp->prior_ssthresh_: сохраняет предыдущее значение ssthresh при входе в сокращение окна — для отмены сокращения cwnd, если отмена разрешена.
  * _tp->window_clamp_: максимальное окно приёма (rcv), которое будет объявлено.

### Окно управления потоком — что такое tp->rcv_wup (т.е. RCV.WUP)?

В исходящих пакетах TCP-отправитель включает ACK и th->window — количество байтов после ACK, которое получателю разрешено отправить. Особая осторожность проявляется в том, чтобы не сжимать окно при его изменении: если другая сторона уже отправила некоторые байты, они должны поместиться в новое окно.

Ядро хранит информацию о последнем обновлении окна в двух переменных. tp->rcv_wnd хранит объявленное окно, а tp->rcv_wup хранит последний ACK, который нёс обновление. Это означает, что другая сторона может отправлять данные вплоть до порядкового номера tp->rcv_wup + tp->rcv_wnd. Поэтому в последующих объявлениях окна код следит, чтобы последний разрешённый seq был не меньше этого порядкового номера.

  * _tcp_receive_window()_ возвращает количество байтов после tp->rcv_next, которое позволило предыдущее объявление окна
  * __tcp_select_window()_ выбирает размер окна с учётом свободного места, стараясь менять окно как можно меньше (для предсказания заголовков) и избегая [SWS](https://en.wikipedia.org/wiki/Silly_window_syndrome).
  * _tcp_select_window()_ гарантирует, что выбранное окно не сжимается.

### Обработка входящих пакетов — tcp_rcv_established

Пакеты обычно проходят от сетевой карты к _tcp_v{4,6}_do_rcv()_, а когда TCP-соединение находится в состоянии ESTABLISHED — к _tcp_rcv_established()_. Здесь код следует [вдохновлённой Ваном Джекобсоном схеме быстрой обработки пакетов «быстрого пути» (fast-path)](http://www.pdl.cmu.edu/mailinglists/ips/mail/msg00133.html), то есть TCP-пакетов без особых обстоятельств: они имеют следующий ожидаемый SEQ, несут ACK в правильном диапазоне и содержат ожидаемые флаги. Код быстрого пути оптимизирует два случая: пакеты только с ACK и пакеты с данными.

Теперь рассмотрим функции, вызываемые в каждом пути обработки.

Обработка пакета только с ACK вызовет _tcp_ack()_, освободит skb, затем вызовет _tcp_data_snd_check()_. Для пакетов с данными, если пользовательский процесс ждёт в приложении, _tcp_copy_to_iovec()_ пытается скопировать данные прямо в пользовательские буферы, иначе вызывается _tcp_queue_rcv()_ для постановки в очередь буферов сокета. Быстрый путь для данных завершается следующей обработкой:

```c
			tcp_event_data_recv(sk, skb);
			if (TCP_SKB_CB(skb)->ack_seq != tp->snd_una) {
				/* Well, only one small jumplet in fast path... */
				tcp_ack(sk, skb, FLAG_DATA);
				tcp_data_snd_check(sk);
				if (!inet_csk_ack_scheduled(sk))
					goto no_ack;
			}
			__tcp_ack_snd_check(sk, 0);
no_ack:
			if (eaten)
				kfree_skb_partial(skb, fragstolen);
			sk->sk_data_ready(sk);
			return;
```

Медленный путь в случае успеха вызывает _tcp_ack()_, _tcp_urg()_, _tcp_data_queue()_, _tcp_data_snd_check()_ и _tcp_ack_snd_check()_.

Итак, в этих трёх путях кода (быстрый-ACK, быстрый-данные, медленный):

  * все обрабатывают входные данные ACK в _tcp_ack()_
  * медленный путь вызывает _tcp_urg()_
  * если есть данные, их нужно поставить в очередь: вызываются _tcp_copy_to_iovec()_, _tcp_queue_rcv()_ или _tcp_data_queue()_
  * все вызывают _tcp_data_snd_check()_
  * если есть данные, вызывается __tcp_ack_snd_check()_ на быстром пути или _tcp_ack_snd_check()_ на медленном.

Обсудим некоторые из этих функций.

### tcp_data_snd_check() и запуск отправки данных

Вызов _tcp_data_snd_check()_ запускает следующее:

  * Вызов _tcp_push_pending_frames()_, который прерывается, если _tcp_send_head()_ равен NULL, то есть в write_queue нет пакета, ожидающего передачи.
  * Вызовы __tcp_push_pending_frames()_, который прерывается, если сокет находится в состоянии TCP_CLOSE
  * Вызов _tcp_write_xmit()_. Мы знаем, что _tcp_send_head()_ != NULL, поэтому функция проходит несколько проверок:

```text
* tcp_cwnd_test: how many packets does the congestion window allow. To first approximation, returns max(0,_tp- >snd_cwnd - tcp_packets_in_flight(tp)_)
* tcp_snd_wnd_test: the first segment in the skb must fit into the send window (i.e., its last seq should be < _tcp_wnd_end()_).
* if only one segment, perform Nagle check in _tcp_nagle_test()_
* if more than one segment, try to defer to minimize TSO splitting, _tcp_tso_should_defer()_ calls this "a kind of TSO Nagle test".
* Do some TSO accounting, and make sure there is no buffer-bloat in the kernel's qdiscs (a.k.a. TCP Small Queues or TSQ)
```

  * _tcp_trasmit_skb()_ фактически передаёт пакет.
  * после отправки всех разрешённых пакетов:

```text
* if socket is in CWR or Recovery state, adjust [PRR ](https://tools.ietf.org/html/rfc6937)state.
* schedule a loss probe (for [TLP](https://lwn.net/Articles/542642/))
```

  * Если _tcp_write_xmit()_ решил не отправлять, вызывается _tcp_check_probe_timer()_

### Обработка подтверждений в tcp_ack()

_tcp_ack()_ сначала выполняет несколько проверок ACK относительно состояния сокета. Подтверждает ли он ранее подтверждённые данные («old ack»)? Подтверждает ли он неотправленные данные («invalid_ack»)? Если ACK валиден, код далее перевзводит RTO, если тот установлен для EARLY_RETRANS или LOSS_PROBE.

Флаги в начале _tcp_ack()_ могут содержать:

  * FLAG_DATA: пакет содержит данные (не чистый ack) на быстром пути
  * FLAG_SLOWPATH: предсказание заголовков не сработало на пакете
  * FLAG_UPDATE_TS_RECENT: после проверки валидности _ack_tcp()_ должен вызвать _tcp_replace_ts_recent()_, чтобы обновить временную метку (_tp->rx_opt.ts_recent_ и _tp->rx_opt.ts_recent_stamp_).

Переменная флагов обновляется по ходу выполнения:

  * FLAG_SND_UNA_ADVANCED: если этот ACK увеличивает _tp->snd_una_, то есть подтверждает ранее неподтверждённые пакеты.
  * FLAG_DATA: добавляется в _tcp_ack()_, если на медленном пути пакет содержит данные.
  * FLAG_WIN_UPDATE: если правая граница объявленного пиром окна могла сдвинуться (заметьте, на медленном пути возможны ложные срабатывания).
  * FLAG_ECE: на пакете был отмечен бит ECN Echo.

_tcp_clean_rtx_queue()_ устанавливает следующие флаги:

  * FLAG_RETRANS_DATA_ACKED: «This ACK acknowledged new data some of which was retransmitted»
  * FLAG_ORIG_SACK_ACKED: «Never retransmitted data are (s)acked»
  * FLAG_DATA_ACKED: ранее неподтверждённые данные подтверждены этим пакетом
  * FLAG_SYN_ACKED: ACK подтверждает SYN.
  * FLAG_SACK_RENEGING: ACK подтверждает пакеты до некоторого пакета, но последующий SEQ был SACKed; это означает, что пир должен был отбросить пакет, который он SACKed (иначе ACK включил бы и этот пакет).

Если предсказание заголовков срабатывает, пакет входит на быстрый путь, и предсказание гарантирует, что объявленное пиром окно не изменилось. Поэтому на быстром пути нужно обновить только _tp->snd_wl1_ и _tp->snd_una_. На медленном пути _tcp_ack_update_window()_ проверяет, что пакет содержит более свежую информацию, и если да — обновляет эти переменные, а также _tp->snd_wnd_, и перевычисляет предсказание быстрого пути для следующего пакета. Пакеты медленного пути могут содержать [SACK](https://www.ietf.org/rfc/rfc2018.txt), поэтому далее они обрабатываются, затем проверяется бит ECN Echo. _tcp_clean_rtx_queue()_ освобождает из очереди записи пакеты, которые подтверждены, а значит достигли адресата.

Подозрительный ACK (dubious ack, см. _tcp_ack_is_dubious()_) — это ACK, у которого пакеты:

  * несут флаг _FLAG_CA_ALERT_, или
  * не несут ни одного из флагов, заданных _FLAG_NOT_DUP_, то есть не содержат ни одного из _FLAG_DATA, FLAG_WIN_UPDATE, FLAG_DATA_ACKED_ или _FLAG_SYN_ACKED_, или
  * находятся в любом соединении не в состоянии TCP_CA_Open

Когда ACK считается «подозрительным», _tcp_ack()_ вызывает _tcp__fastretrans_alert()_, который мы разберём в последующем разделе.

После обработки подозрительных ACK _tcp_ack()_ может вызвать _cong_avoid()_, обсуждаемый далее.

### cong_avoid

Вызывается из _tcp_ack()_, если _tcp_may_raise_cwnd()_ возвращает true. Это требует:

  * Сокет не должен находиться в состояниях CWR или Recovery
  * Должен быть достигнут некоторый прогресс. Обычно это значит, что некоторые пакеты были подтверждены, поэтому установлен _FLAG_DATA_ACKED_: _tcp_clean_rtx_queue()_ считает, сколько пакетов были полностью подтверждены ACK, и удаляет их из очереди ретрансляции; если пакеты удалены, устанавливается _FLAG_DATA_ACKED_. Когда переупорядочивание в сети превышает порог, используется более широкое определение прогресса (см. FLAG_FORWARD_PROGRESS — по сути, оно также учитывает новые SACK-нутые пакеты).

### tcp_fastretrans_alert()

  * На входящих пакетах с маркировкой ECE отключает отмену сокращения cwnd.
  * Если обнаружен SACK reneging (_FLAG_SACK_RENEGING_ был установлен в _tcp_clean_rtx_queue()_), устанавливает короткий таймаут ретрансляции, чтобы дать ACK время дойти для этих пакетов, иначе таймаут сбросит состояние SACK. Если есть подозрение на reneging, дальнейшая обработка в _tcp_fastretrans_alert()_ не выполняется.
  * Если сокет в состоянии CWR и ACK выше _tp->high_seq_, будет вызван _tcp_end_cwnd_reduction()_, который сбрасывает _tp->snd_cwnd_ в _tp->snd_ssthresh_, затем происходит переход в состояние _TCP_CA_Open_.
  * Если сокет в состоянии Recovery и ACK равен или выше _tp->high_seq_, будет вызван _tcp_try_undo_recovery()_

### cwnd_event и события TCP

Стек TCP сообщает о некоторых событиях через _tcp_ca_event()_, которые затем передаются в _cwnd_event_ управления перегрузкой:

```c
static inline void tcp_ca_event(struct sock *sk, const enum tcp_ca_event event)
{
	const struct inet_connection_sock *icsk = inet_csk(sk);
	if (icsk->icsk_ca_ops->cwnd_event)
		icsk->icsk_ca_ops->cwnd_event(sk, event);
}
```

Определения событий также содержат краткие описания:

```c
/* Events passed to congestion control interface */
enum tcp_ca_event {
	CA_EVENT_TX_START,	/* first transmit when no packets in flight */
	CA_EVENT_CWND_RESTART,	/* congestion window restart */
	CA_EVENT_COMPLETE_CWR,	/* end of congestion recovery */
	CA_EVENT_LOSS,		/* loss timeout */
	CA_EVENT_ECN_NO_CE,	/* ECT set, but not CE marked */
	CA_EVENT_ECN_IS_CE,	/* received CE marked IP packet */
	CA_EVENT_DELAYED_ACK,	/* Delayed ack is sent */
	CA_EVENT_NON_DELAYED_ACK,
};
```

В v4.4.3 вызовы _tcp_ca_event()_ присутствуют в 8 строках исходного кода — по одной для каждого типа событий.

  * CA_EVENT_TX_START из _tcp_event_data_sent()_
  * CA_EVENT_CWND_RESTART из _tcp_cwnd_restart()_
  * CA_EVENT_COMPLETE_CWR из _tcp_end_cwnd_reduction()_
  * CA_EVENT_LOSS из _tcp_enter_loss()_
  * CA_EVENT_ECN_NO_CE, CA_EVENT_ECN_IS_CE из __tcp_ecn_check_ce()_
  * CA_EVENT_DELAYED_ACK из _tcp__send_delayed_ack()_
  * CA_EVENT_NON_DELAYED_ACK из _tcp_send_ack()_

### ssthresh

ssthresh вызывается из двух функций: _tcp_init_cwnd_reduction_ и _tcp_enter_loss_. Возвращаемое значение устанавливает _tp->snd_ssthresh_, где tp указывает на _struct tcp_sock_.

### in_ack_event

Вызывается из _tcp_in_ack_event_. В ядре v4.4.3 только DCTCP и Westwood реализуют этот обратный вызов. Именно здесь DCTCP поддерживает счётчики для всех подтверждённых байтов и всех байтов с ECN-маркировкой и обновляет свою оценку альфа каждый RTT (см. _dctcp_update_alpha()_).

В то время как _cong_avoid()_ вызывается только когда _tcp_may_raise_cwnd()_ истинно, _in_ack_event()_ вызывается для каждого ACK, причём вызов происходит до _cong_avoid()_ в обработке ACK. Поэтому алгоритмы управления перегрузкой, реализующие оба обратных вызова, могут ожидать вызова _in_ack_event()_ перед каждым _cong_avoid()_.

Аргумент-флаг может содержать следующие флаги:

```c
/* Information about inbound ACK, passed to cong_ops->in_ack_event() */
enum tcp_ca_ack_event_flags {
	CA_ACK_SLOWPATH		= (1 << 0),	/* In slow path processing */
	CA_ACK_WIN_UPDATE	= (1 << 1),	/* ACK updated window */
	CA_ACK_ECE		= (1 << 2),	/* ECE bit is set on ack */
};
```

На быстром пути, где ACK подтверждает новый сегмент, обратный вызов получит только _CA_ACK_WIN_UPDATE_. Любой другой случай будет иметь как минимум _CA_ACK_SLOWPATH_.

### undo_cwnd

Путь вызова — _tcp_undo_cwnd_reduction_, вызываемый из:

  * tcp_try_undo_recovery
  * tcp_try_undo_dsack: «Try to undo cwnd reduction, because D-SACKs acked all retransmitted data»
  * tcp_try_undo_loss: «Undo during loss recovery after partial ACK or using F-RTO.»
  * tcp_try_undo_partial из _tcp_fastretrans_alert()_: «Undo during fast recovery after partial ACK.»

Используется в алгоритмах bic, cdg, cubic и htcp.

### pkts_acked

Вызывается из _tcp_ack_ -> _tcp_clean_rtx_queue_. Похоже, вызывается для каждого пакета только с ACK и каждого валидного пакета медленного пути с корректным значением ack, даже если новые пакеты не подтверждены. Для пакетов быстрого пути с данными tcp_ack вызывается только если ACK_SEQ != SND_UNA, то есть это либо старый ack, либо ack подтверждает больше байтов.

### get_info

Используется при выгрузке диагностики, то есть в _dump()_ и _dump_one()_ в _tcp_diag_handler_.

### Ресурсы

  * Работа Арианфара «[TCP’s Congestion Control Implementation in Linux Kernel](https://wiki.aalto.fi/download/attachments/69901948/TCP-CongestionControlFinal.pdf)» сосредоточена на описании механизмов TCP и важных функций, а затем рассматривает реализацию Cubic.

**********

[linux](/tags/linux.md)
[tcp](/tags/tcp.md)
[kernel](/tags/kernel.md)