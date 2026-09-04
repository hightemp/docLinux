# Unix domain sockets: локальный IPC через AF_UNIX

Источник: [Unix Domain Sockets — разбор локального IPC через `AF_UNIX`: `SOCK_STREAM`/`SOCK_DGRAM`/`SOCK_SEQPACKET`, filesystem/abstract namespace, `socketpair()`, `SCM_RIGHTS`/`SCM_CREDENTIALS` и реализация в `net/unix/af_unix.c`.](https://kernel-internals.org/ipc/unix-sockets/)

kernel-internals.org

# Unix Domain Sockets

> Локальный IPC с передачей файловых дескрипторов, abstract namespace и SOCK_SEQPACKET

Сокеты Unix domain (`AF_UNIX`) обеспечивают полнодуплексный, ориентированный на соединение или дейтаграммный IPC целиком внутри ядра — сетевой стек не задействуется. Они — основа D-Bus, socket activation в systemd, управляющего сокета Docker и бесчисленного множества других локальных демонов.

## Типы сокетов

| Тип | Семантика | Границы сообщений сохраняются | Сценарий использования
|---|---|---|---
| `SOCK_STREAM` | Надёжный поток байтов | Нет | Высокоскоростные каналы, базы данных
| `SOCK_DGRAM` | Ненадёжные дейтаграммы | Да | Короткие сообщения «отправил и забыл»
| `SOCK_SEQPACKET` | Надёжные, упорядоченные сообщения | **Да** | RPC, разделение привилегий

`SOCK_SEQPACKET` — золотая середина для структурированного IPC: он сочетает надёжность `SOCK_STREAM` с сохранением границ сообщений `SOCK_DGRAM`. Каждый `send()` соответствует ровно одному `recv()` на другой стороне.

```c
#include <sys/socket.h>
#include <sys/un.h>

/* Server side */
int srv = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
```

## struct sockaddr_un

```c
#include <sys/un.h>

struct sockaddr_un {
    sa_family_t sun_family;   /* AF_UNIX */
    char        sun_path[108]; /* socket path or abstract name */
};
```

`sun_path` — 108 байт всего (`UNIX_PATH_MAX`). Для сокетов abstract-namespace первый байт — `\0`, а остальные 107 байт образуют имя.

## Файловая система как пространство имён (filesystem namespace)

Привязка к пути в файловой системе создаёт inode сокета в VFS:

```c
struct sockaddr_un addr = {
    .sun_family = AF_UNIX,
    /* null-terminated path */
};
strncpy(addr.sun_path, "/run/myservice.sock", sizeof(addr.sun_path) - 1);

bind(srv, (struct sockaddr *)&addr, sizeof(addr));
listen(srv, SOMAXCONN);
```

Свойства: \- Разрешения контролируются битами режима файла (`chmod 0660 /run/myservice.sock`) \- Файл сокета сохраняется после выхода сервера — его нужно удалить с помощью `unlink()` перед повторной привязкой \- Контролируется пространством имён файловой системы: контейнеры с раздельными mount-namespace не видят файлы сокетов друг друга

## Abstract namespace

Абстрактное имя сокета начинается с нулевого байта (`\0`). Ядро отслеживает привязку в памяти — записи в файловой системе нет:

```c
struct sockaddr_un addr = { .sun_family = AF_UNIX };
/* First byte \0, then the name */
memcpy(addr.sun_path, "\0myservice", 10);

/* sun_path length includes the leading \0 */
socklen_t addrlen = offsetof(struct sockaddr_un, sun_path) + 10;
bind(srv, (struct sockaddr *)&addr, addrlen);
```

Свойства: \- Автоматически очищается при закрытии последнего файлового дескриптора, ссылающегося на него, — `unlink()` не нужен \- Имя — произвольные байты, а не C-строка; может содержать нулевые байты после первого \- Видно только внутри одного сетевого пространства имён (`ip netns` или namespace контейнера дают изоляцию) \- `ss -xlp` показывает abstract-сокеты с префиксом `@` в колонке адреса

## socketpair()

`socketpair()` создаёт связанную пару сокетов без bind и listen — простейший способ создать двунаправленный канал между родительским и дочерним процессами:

```c
int sv[2];
socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv);
/* sv[0] and sv[1] are connected */

if (fork() == 0) {
    close(sv[0]);
    /* child uses sv[1] */
} else {
    close(sv[1]);
    /* parent uses sv[0] */
}
```

Это предпочтительнее пайпа для двунаправленного IPC и анонимной пары сокетов для структурированной (с сохранением границ сообщений) связи.

## Передача файловых дескрипторов через SCM_RIGHTS

Управляющее сообщение `SCM_RIGHTS` позволяет процессу отправлять открытые файловые дескрипторы через Unix-сокет. Ядро дублирует описание файла в таблицу файловых дескрипторов получателя — получатель получает новый номер fd, указывающий на тот же открытый файл, включая его смещение, флаги и режим доступа.

```c
#include <sys/socket.h>
#include <sys/un.h>

/* --- Sender --- */
int fd_to_pass = open("/etc/passwd", O_RDONLY);

struct msghdr msg = {};
char buf[CMSG_SPACE(sizeof(int))];  /* control message buffer */
struct iovec iov = { .iov_base = "x", .iov_len = 1 }; /* must send ≥1 data byte */

msg.msg_iov        = &iov;
msg.msg_iovlen     = 1;
msg.msg_control    = buf;
msg.msg_controllen = sizeof(buf);

struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type  = SCM_RIGHTS;
cmsg->cmsg_len   = CMSG_LEN(sizeof(int));
memcpy(CMSG_DATA(cmsg), &fd_to_pass, sizeof(int));

sendmsg(sock, &msg, 0);
close(fd_to_pass);  /* sender no longer needs it */
```

```c
/* --- Receiver --- */
char data[1];
char cbuf[CMSG_SPACE(sizeof(int))];
struct iovec riov = { .iov_base = data, .iov_len = sizeof(data) };
struct msghdr rmsg = {
    .msg_iov        = &riov,
    .msg_iovlen     = 1,
    .msg_control    = cbuf,
    .msg_controllen = sizeof(cbuf),
};

recvmsg(sock, &rmsg, 0);

struct cmsghdr *rcmsg = CMSG_FIRSTHDR(&rmsg);
if (rcmsg && rcmsg->cmsg_type == SCM_RIGHTS) {
    int received_fd;
    memcpy(&received_fd, CMSG_DATA(rcmsg), sizeof(int));
    /* received_fd is usable immediately */
}
```

Путь `unix_stream_sendmsg()` / `unix_scm_to_skb()` в ядре (в `net/unix/af_unix.c`) прикрепляет ссылки на файлы к socket buffer. На стороне приёма `unix_detach_fds()` извлекает их из skb, затем `scm_detach_fds()` (в `net/core/scm.c`) устанавливает их в `files_struct` получателя через `receive_fd()`.

### Риск утечки

Каждый полученный fd должен быть закрыт, включая на аварийных путях. Если получатель не закрывает fd, они незаметно накапливаются в таблице файловых дескрипторов процесса. `lsof -p <pid>` их покажет, но ущерб уже нанесён, когда сработает `EMFILE`.

Используйте `SOCK_CLOEXEC` на _сокете_, чтобы сами сокетные fd не утекали через `exec()`. Для полученных fd устанавливайте `O_CLOEXEC` через `fcntl(received_fd, F_SETFD, FD_CLOEXEC)` сразу после получения.

## Передача учётных данных пира через SCM_CREDENTIALS

`SCM_CREDENTIALS` позволяет отправителю прикрепить к сообщению свой `pid`, `uid` и `gid`. Ядро проверяет учётные данные по фактическим значениям отправителя — процесс не может подделать чужой uid (если только он не root).

```c
/* Enable credential reception on the socket */
int enable = 1;
setsockopt(sock, SOL_SOCKET, SO_PASSCRED, &enable, sizeof(enable));

/* Sender: attach credentials */
struct ucred cred = {
    .pid = getpid(),
    .uid = getuid(),
    .gid = getgid(),
};
char cbuf[CMSG_SPACE(sizeof(struct ucred))];
struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type  = SCM_CREDENTIALS;
cmsg->cmsg_len   = CMSG_LEN(sizeof(struct ucred));
memcpy(CMSG_DATA(cmsg), &cred, sizeof(cred));
```

Для соединённого сокета более простая альтернатива — `SO_PEERCRED`, возвращающая учётные данные _соединённого_ пира без per-message управляющего сообщения:

```c
struct ucred peer;
socklen_t len = sizeof(peer);
getsockopt(sock, SOL_SOCKET, SO_PEERCRED, &peer, &len);
printf("peer pid=%d uid=%d gid=%d\n", peer.pid, peer.uid, peer.gid);
```

`SO_PEERCRED` используется systemd, D-Bus и polkit для аутентификации вызывающего процесса перед предоставлением привилегированных операций.

## Производительность

Сокеты Unix domain обходят весь стек TCP/IP. Данные копируются напрямую между буферами отправки и приёма сокета в ядре, а в некоторых конфигурациях используются zero-copy приёмы через `sk_buff`. Типичная пропускная способность на современном оборудовании:

| Механизм | Пропускная способность
|---|---
| `AF_INET` loopback (`127.0.0.1`) | ~5 ГБ/с
| `AF_UNIX SOCK_STREAM` | ~10–15 ГБ/с
| Разделяемая память | ~30–50 ГБ/с

`AF_UNIX` с `SOCK_DGRAM` полностью избегает накладных расходов установки соединения, что полезно для коротких управляющих сообщений «отправил и забыл» между процессами на одной машине.

## Реализация в ядре

Реализация находится в `net/unix/af_unix.c`. Ключевые структуры:

```c
/* include/net/af_unix.h */
struct unix_sock {
    /* WARNING: sk has to be the first member */
    struct sock     sk;
    struct unix_address *addr;      /* bound address */
    struct path     path;           /* socket file path (filesystem sockets) */
    struct mutex    iolock, bindlock;
    struct sock    *peer;           /* connected peer (SOCK_STREAM/SEQPACKET) */
    struct sock    *listener;
    struct unix_vertex *vertex;     /* this socket's node in the GC graph */
    spinlock_t      lock;
    struct socket_wq peer_wq;
    wait_queue_entry_t peer_wake;
    struct scm_stat scm_stat;       /* SCM stats for this socket */
    int             inq_len;
    bool            recvmsg_inq;
    /* struct sk_buff *oob_skb; -- only under CONFIG_AF_UNIX_OOB */
};
```

Сообщения для `SOCK_DGRAM` и `SOCK_SEQPACKET` хранятся как элементы `sk_buff` в `sk->sk_receive_queue`. Для `SOCK_STREAM` `unix_stream_sendmsg()` копирует данные напрямую в очередь приёма пира.

На `struct unix_sock` нет счётчика fd в полёте (в раннем дизайне ядра он отслеживался парой `struct list_head link`/`atomic_long_t inflight`; обе теперь ушли). Учёт находящихся в полёте `SCM_RIGHTS` теперь ведётся на уровне `user_struct` (`user->unix_inflight`). Сборщик мусора (`net/unix/garbage.c`) строит явный граф сокетов и их fd-ссылок — каждый сокет является `struct unix_vertex` (связанным через `unix_sock.vertex` выше), каждая ссылка в полёте — ребром (`struct unix_edge`) — и запускает по этому графу поиск сильно связных компонент в стиле Тарьяна, чтобы находить и освобождать циклы ссылок, вместо простой проверки счётчика inflight.

## Дополнительное чтение

### Исходники ядра

* [net/unix/af_unix.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/unix/af_unix.c) — основная реализация `AF_UNIX`: `unix_stream_sendmsg()`, `unix_dgram_sendmsg()`, `unix_attach_fds()` / `unix_detach_fds()`, `unix_scm_to_skb()`
* [net/unix/garbage.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/unix/garbage.c) — собирающий циклы сборщик мусора для циклов ссылок `SCM_RIGHTS` (`struct unix_vertex`, `struct unix_edge`)
* [net/core/scm.c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/core/scm.c) — общая обработка вспомогательных данных: `scm_detach_fds()`, `scm_check_creds()` (проверка uid/gid для `SCM_CREDENTIALS`)
* [include/net/af_unix.h](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/net/af_unix.h) — определение `struct unix_sock`
* [include/uapi/linux/un.h](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/un.h) — `struct sockaddr_un` и `UNIX_PATH_MAX`

### Man-страницы

* [`unix(7)`](https://man7.org/linux/man-pages/man7/unix.7.html) — канонический справочник: типы сокетов, `sockaddr_un`, abstract namespace, `SCM_RIGHTS`, `SCM_CREDENTIALS`, `SO_PEERCRED`
* [`socket(2)`](https://man7.org/linux/man-pages/man2/socket.2.html) — системный вызов `socket()` и типы `SOCK_STREAM` / `SOCK_DGRAM` / `SOCK_SEQPACKET`
* [`sendmsg(2)`](https://man7.org/linux/man-pages/man2/sendmsg.2.html) — `sendmsg()`/`recvmsg()`, `struct msghdr` и вспомогательные данные
* [`cmsg(3)`](https://man7.org/linux/man-pages/man3/cmsg.3.html) — макросы `CMSG_FIRSTHDR`/`CMSG_DATA`/`CMSG_LEN`/`CMSG_SPACE`

### Связанные страницы

* [Pipes and FIFOs](../pipes/) — однонаправленный потоковый IPC
* [Shared Memory](../shared-memory/) — обмен данными без копирования
* [eventfd and signalfd](../eventfd-signalfd/) — опрашиваемые fd уведомлений
* [IPC War Stories](../war-stories/) — реальный инцидент утечки fd через `SCM_RIGHTS` в демоне с разделением привилегий
* [Socket Layer Overview](../../net/socket-layer/) — универсальный стек `struct socket`/`struct sock`/`proto_ops`, в который подключается `AF_UNIX`

### Статьи LWN

* [io_uring, SCM_RIGHTS, and reference-count cycles](https://lwn.net/Articles/779472/) (Jonathan Corbet, февраль 2019) — как регистрация файлов в `io_uring` создала новый вариант цикла ссылок fd, для разрыва которого и существует сборщик мусора `AF_UNIX`

**********

[sockets](/tags/sockets.md)
[linux](/tags/linux.md)
[kernel](/tags/kernel.md)