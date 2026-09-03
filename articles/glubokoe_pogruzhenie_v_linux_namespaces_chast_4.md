# Глубокое погружение в Linux namespaces, часть 4

Источник: [Глубокое погружение в Linux namespaces, часть 4](https://habr.com/ru/articles/549414/)

В завершающем посте этой серии мы рассмотрим [Network namespaces](http://man7.org/linux/man-pages/man8/ip-netns.8.html). Как мы упоминали в [вводном посте](https://habr.com/ru/post/458462/), network namespace изолирует ресурсы, связанные с сетью: процесс, работающий в отдельном network namespace, имеет собственные сетевые устройства, таблицы маршрутизации, правила фаервола и т.д. Мы можем непосредственно увидеть это на практике, рассмотрев наше текущее сетевое окружение.

## Команда ip

> _Поскольку в этом посте мы будем взаимодействовать с сетевыми устройствами, мы вернем жесткое требование наличия прав суперпользователя, которое мы смягчили в предыдущих постах. С этого момента мы будем предполагать, что как`ip`, так и `isolate` будут запускаться с `sudo`._

```bash
$ ip link list
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether 00:0c:29:96:2e:3b brd ff:ff:ff:ff:ff:ff
```

Звездой шоу здесь является команда `ip` — [швейцарский армейский нож](https://access.redhat.com/sites/default/files/attachments/rh_ip_command_cheatsheet_1214_jcs_print.pdf) для работы с сетью в Linux — и мы будем активно использовать её в этом посте. Прямо сейчас мы только что выполнили подкоманду `link list`, чтобы увидеть, какие сетевые устройства в настоящее время доступны в системе (здесь есть `lo` — loopback-интерфес и `ens33, ethernet-интерфейс LAN.

Как и со всеми другими пространствами имён, система стартует с начальным network namespace, которому принадлежат все процесс процессы, если не задано иное. Выполнение команды `ip link list` как есть показывает нам сетевые устройства, принадлежащие изначальному пространству имён (поскольку и наш шелл, и команда `ip` принадлежат этому пространству имён).

## Именованные пространства имён Network

Давайте создадим новый network namespace:

```bash
$ ip netns add coke
$ ip netns list
coke
```

И снова мы использовали команду `ip`. Подкоманда `netns` позволяет нам играться с пространствами имён network: например, мы можем создавать новые сетевые пространства network с помощью подкоманды `add` команды `netns` и использовать `list` для их вывода.
Вы могли заметить, что `list` возвращал только наш вновь созданный namespace. Разве он не должен возвращать по крайней мере два, одним из которых был бы исходным namespace, о котором мы упоминали ранее? Причина этого в том, что `ip` создаёт то, что называется _named network namespace_ , который является просто network namespace, идентифицируемый уникальным именем (в нашем случае `coke`). Только именованные пространства имён network отображаются подкомандой `list`, а изначальный network namespace не именованный.

Проще всего получить именованные пространства имён network. Например, в каждом именованном network namespace создаётся файл в каталоге `/var/run/netns` и им сможет воспользоваться процесс, который хочет переключиться на свой namespace. Другое свойство именованных пространств имён network заключается в том, что они могут существовать без наличия какого-либо процесса — в отличие от неименованных, которые будут удалены как только завершатся все принадлежащие им процессы.

Теперь, когда у нас есть дочерний network namespace, мы можем взглянуть на сеть с его точки зрения.

> _Мы будем использовать приглашение командной строки`C$` для обозначения шелла, работающего в дочернем network namespace._

```bash
$ ip netns exec coke bash
C$ ip link list
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
```

Запуск субкоманды `exec $namespace $command` выполняет `$command` в именованном network namespace `$namespace`. Здесь мы запустили шелл внутри пространства имён `coke` и посмотрели доступные сетевые устройства. Мы видим, что, по крайней мере, наше устройство `ens33` исчезло. Единственное устройство, которое видно, это лупбек и даже этот интерфейс погашен.

```text
C$ ping 127.0.0.1
connect: Network is unreachable
```

Мы должны теперь свыкнуться с тем, что настройки по умолчанию для пространств имён обычно очень строгие. Для пространств имён network, как мы видим, никаких устройств, помимо `loopback`, не будет доступно. Мы можем поднять интерфейс `loopback` без всяких формальностей:

```text
C$ ip link set dev lo up
C$ ping 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.034 ms
...
```

## Сетевое изолирование

Мы уже начинаем понимать, что запустив процесс во вложенном network namespace, таком как `coke`, мы можем быть уверены, что он изолирован от остальной системы в том, что касается сети. Наш шелл-процесс, работающий в `coke`, может общаться только через `loopback`. Это означает, что он может общаться только с процессами, которые также являются членами пространства имён `coke`, но в настоящее время других таких процессов нет (и, во имя изолированности, мы хотели бы, чтобы так и оставалось), так что он немного одинок. Давайте попробуем несколько ослабить эту изолированность. Мы создадим _туннель_ , через который процессы в `coke` смогут общаться с процессами в нашем исходном пространстве имён.

Сейчас любое сетевое общение должно происходить через какое-то сетевое устройство, а устройство может существовать ровно в одном network namespace в данный конкретный момент времени, поэтому связь между любыми двумя процессами в разных пространствах имён должна осуществляться как минимум через два сетевых устройства — по одному в каждом network namespace.

### Устройства veth

Для выполнения этого нашего требования, мы будем использовать сетевое устройство [**v** irtual **eth** ernet](http://man7.org/linux/man-pages/man4/veth.4.html) (или сокращённо `veth`). Устройства veth всегда создаются как пара устройств, связанных по принципу туннеля, так что сообщения, отправленные на одном конце, выходят из устройства на другом. Вы могли бы предположить, что мы могли бы легко иметь один конец в исходном network namespace, а другой — в нашем дочернем network namespace, а всё общение между пространствами имён network проходило бы через соответствующее оконечное устройство veth (и вы были бы правы).

```bash
# Создание пары veth (veth0 <=> veth1)
$ ip link add veth0 type veth peer name veth1
# Перемещение veth1 в новое пространство имён
$ ip link set veth1 netns coke
# Просмотр сетевых устройств в новом пространстве имён
C$ ip link list
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
7: veth1@if8: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000
    link/ether ee:16:0c:23:f3:af brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

Наше устройство `veth1` теперь появилось в пространстве имён `coke`. Но чтобы заставить пару veth работать, нам нужно назначить там IP-адреса и поднять интерфейсы. Мы сделаем это в каждом соответствующем network namespace.

```bash
# В исходном пространстве имён
$ ip addr add 10.1.1.1/24 dev veth0
$ ip link set dev veth0 up

# В пространстве имён coke
C$ ip addr add 10.1.1.2/24 dev veth1
C$ ip link set dev veth1 up

C$ ip addr show veth1
7: veth1@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether ee:16:0c:23:f3:af brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 10.1.1.2/24 scope global veth1
       valid_lft forever preferred_lft forever
    inet6 fe80::ec16:cff:fe23:f3af/64 scope link
       valid_lft forever preferred_lft forever
```

Мы должны увидеть, что интерфейс `veth1` поднят и имеет назначенный нами адрес `10.1.1.2`. Тоже самое должно произойти с `veth0` в исходном пространстве имён. Теперь у нас должна быть возможность сделать интер-namespace ping между двумя процессами, запущенными в обоих пространствах имён.

```bash
$ ping -I veth0 10.1.1.2
PING 10.1.1.2 (10.1.1.2) 56(84) bytes of data.
64 bytes from 10.1.1.2: icmp_seq=1 ttl=64 time=0.041 ms
...
C$ ping 10.1.1.1
PING 10.1.1.1 (10.1.1.1) 56(84) bytes of data.
64 bytes from 10.1.1.1: icmp_seq=1 ttl=64 time=0.067 ms
...
```

## Реализация

> _Исходный код к этому посту[можно найти здесь](https://github.com/iffyio/isolate/tree/part-4)._

Как обычно, теперь мы попытаемся воспроизвести то, что мы рассматривали до сих пор, в коде. В частности, нам нужно будет сделать следующее:

  1. Выполнить команду в новом network namespace.
  2. Создать пару veth (veth0 <=> veth1).
  3. Переместить устройство veth1 в новый namespace.
  4. Назначить IP-адреса обоим устройствам и поднять их.

Шаг `1` прост: мы создаём наш командный процесс в новом пространстве имён network путём добавления флага `CLONE_NEWNET` к `clone`:

```text
int clone_flags = SIGCHLD | CLONE_NEWUTS | CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET;
```

### Netlink

Для остальных шагов мы будем преимущественно использовать [Netlink](http://www.infradead.org/~tgr/libnl/doc/core.html#_introduction) [интерфейс](http://man7.org/linux/man-pages/man7/netlink.7.html) чтобы общаться с Linux. Netlink в основном используется для связи между обычными приложениями (вроде `isolate`) и ядром Linux. Он предоставляет API поверх сокетов на основе [протокола](http://www.infradead.org/~tgr/libnl/doc/core.html#core_netlink_fundamentals), который определяет структуру и содержание сообщения. Используя этот протокол, мы можем отправлять сообщения, которые получает Linux и преобразует в запросы вроде _создать пару veth с именами veth0 и veth1_.

Давайте начнем с создания нашего сокета netlink. При этом мы укажем, что хотим использовать протокол `NETLINK_ROUTE` — этот протокол охватывает реализации сетевой маршрутизации и управления устройствами.

```text
int create_socket(int domain, int type, int protocol)
{
    int sock_fd = socket(domain, type, protocol);
    if (sock_fd < 0)
        die("cannot open socket: %m\n");

    return sock_fd;
}

int sock_fd = create_socket(
  PF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
```

### Netlink Message Format

[Сообщение](http://www.infradead.org/~tgr/libnl/doc/core.html#core_msg_format) в netlink — это четырехбайтовый выровненный блок данный, содержащий заголовок (`struct nlmsghdr`) и полезную нагрузку. Формат заголовка описан [здесь](https://tools.ietf.org/html/rfc3549#section-2.3.2). [Модуль The Network Interface Service (NIS)](https://tools.ietf.org/html/rfc3549#section-2.3.1) определяет формат (`struct ifinfomsg`), с которого должна начинаться полезная нагрузка, относящаяся к управлению сетевым интерфейсом.

Наш следующий запрос будет представлен следующей структурой `C`:

```c
#define MAX_PAYLOAD 1024
```

```c
struct nl_req {
    struct nlmsghdr n;     // Заголовок сообщения Netlink
    struct ifinfomsg i;    // Полезная нагрузка начинается с информации модуля NIS
    char buf[MAX_PAYLOAD]; // Остальная полезная нагрузка
};
```

### Атрибуты Netlink

Модуль NIS требует, чтобы полезная нагрузка была закодирована как [атрибуты Netlink](http://www.infradead.org/~tgr/libnl/doc/core.html#core_attr). Атрибуты обеспечивают способ сегментировать полезную нагрузку на подсекции. Атрибут имеет тип и длину в дополнение к полезной нагрузке, содержащей сами данные.

Полезная нагрузка в сообщении Netlink будет закодирована как список атрибутов (где любой такой атрибут, в свою очередь, может иметь вложенные атрибуты), а у нас будет несколько вспомогательных функций для заполнения его атрибутами. В коде атрибут представлен в заголовочном файле `linux/rtnetlink.h` структурой `rtattr` как:

```c
struct rtattr {
  unsigned short  rta_len;
  unsigned short  rta_type;
};
```

`rta_len` — это длина полезной нагрузки атрибута, что следует в памяти сразу за структурой `rt_attr struct` (то есть следующие `rta_len` байты). Как интерпретируется содержимое этой полезной нагрузки, задается `rta_type`, а возможные значения полностью зависят от реализации получателя и отправляемого запроса.

В попытке собрать всё это вместе, давайте посмотрим, как `isolate` делает netlink запрос для создания для создания пары veth с помощью следующей функции `create_veth`, которая выполняет шаг `2`:

```c
// ip link add ifname type veth ifname name peername
void create_veth(int sock_fd, char *ifname, char *peername)
{
    __u16 flags =
            NLM_F_REQUEST  // Это сообщение запроса
            | NLM_F_CREATE // Создание устройства, если оно не существует
            | NLM_F_EXCL   // Если оно уже существует, ничего не делать
            | NLM_F_ACK;   // Ответ с подтверждением или ошибкой
```

```c
    // Инициализация сообщения запроса.
    struct nl_req req = {
            .n.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg)),
            .n.nlmsg_flags = flags,
            .n.nlmsg_type = RTM_NEWLINK, // Это сообщение netlink
            .i.ifi_family = PF_NETLINK,
    };
    struct nlmsghdr *n = &req.n;
    int maxlen = sizeof(req);
```

```c
    /*
     * Создание атрибута r0 с информацией о veth. Например, если ifname - veth0,
     * тогда нижеследующее будет добавлено к сообщению
     * {
     *   rta_type: IFLA_IFNAME
     *   rta_len: 5 (len(veth0) + 1)
     *   data: veth0\0
     * }
     */
    addattr_l(n, maxlen, IFLA_IFNAME, ifname, strlen(ifname) + 1);
```

```c
    // Добавление вложенного атрибута r1 в r0, содержащего информацию iface
    struct rtattr *linfo =
            addattr_nest(n, maxlen, IFLA_LINKINFO);
    // Указание типа устройства veth
    addattr_l(&req.n, sizeof(req), IFLA_INFO_KIND, "veth", 5);
```

```c
    // Добавление еще одного вложенного атрибута r2
    struct rtattr *linfodata =
            addattr_nest(n, maxlen, IFLA_INFO_DATA);
```

```c
    // Следующий вложенный атрибут r3 содержит имя соседнего устройства, например veth1
    struct rtattr *peerinfo =
            addattr_nest(n, maxlen, VETH_INFO_PEER);
    n->nlmsg_len += sizeof(struct ifinfomsg);
    addattr_l(n, maxlen, IFLA_IFNAME, peername, strlen(peername) + 1);
    addattr_nest_end(n, peerinfo); // конец вложенного атрибута r3
```

```c
    addattr_nest_end(n, linfodata); // конец вложенного атрибута r2
    addattr_nest_end(n, linfo); // конец вложенного атрибута r1
```

```c
    // Отправка сообщения
    send_nlmsg(sock_fd, n);
}
```

Как мы видим, нам нужно быть точными в том, что мы отправляем сюда: нам нужно было закодировать сообщение точно так, как оно будет интерпретироваться реализацией ядра, и здесь нам потребовалось три вложенных атрибута для этого. Я уверен, что это где-то задокументировано, хотя, немного погуглив, мне не удалось этого найти — в основном я разобрался с помощью [strace](https://linux.die.net/man/1/strace) и [исходного кода](https://github.com/shemminger/iproute2/tree/master/ip) команды `ip`.

Далее, для шага `3`, этот метод, который, учитывая имя интерфейса `ifname` и network namespace файлового дескриптора `netns`, перемещает устройство, связанное с этим интерфейсом, в указанный network namespace.

```c
// $ ip link set veth1 netns coke
void move_if_to_pid_netns(int sock_fd, char *ifname, int netns)
{
    struct nl_req req = {
            .n.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg)),
            .n.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK,
            .n.nlmsg_type = RTM_NEWLINK,
            .i.ifi_family = PF_NETLINK,
    };
```

```text
    addattr_l(&req.n, sizeof(req), IFLA_NET_NS_FD, &netns, 4);
    addattr_l(&req.n, sizeof(req), IFLA_IFNAME,
              ifname, strlen(ifname) + 1);
    send_nlmsg(sock_fd, &req.n);
}
```

После создания пары veth и перемещения одного конца в наш целевой network namespace, на шаге `4` мы назначаем IP-адреса обоим конечным устройствам и поднимаем их интерфейсы. Для этого у нас есть вспомогательная функция `if_up`, которая, учитывая имя интерфейса `ifname` и IP-адрес `ip`, назначает `ip` устройству `ifname` и поднимает его. Для краткости мы не показываем их тут, но вместо этого они могут быть [найдены здесь](https://github.com/iffyio/isolate/blob/part-4/netns.c#L155).

Наконец, мы объединяем эти методы, чтобы подготовить наш network namespace для нашего командного процесса.

```c
static void prepare_netns(int child_pid)
{
    char *veth = "veth0";
    char *vpeer = "veth1";
    char *veth_addr = "10.1.1.1";
    char *vpeer_addr = "10.1.1.2";
    char *netmask = "255.255.255.0";
```

```c
    // Создание нашего сокета netlink
    int sock_fd = create_socket(
            PF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
```

```c
    // ... и нашей пары veth veth0 <=> veth1.
    create_veth(sock_fd, veth, vpeer);
```

```c
    // veth0 находится в нашем текущем (исходном) namespace
    // так что мы можем сразу поднять его.
    if_up(veth, veth_addr, netmask);
```

```c
    // ... veth1 будет перемещен в namespace команды.
    // Для этого нам нужно получить файловый дескриптор
    // и перейти в namespace команды, но сначала мы должны
    // запомнить наш текущий namespace, чтобы мы могли вернуться в него
    // когда закончим.
    int mynetns = get_netns_fd(getpid());
    int child_netns = get_netns_fd(child_pid);
```

```c
    // Перемещение veth1 в network namespace команды.
    move_if_to_pid_netns(sock_fd, vpeer, child_netns);
```

```c
    // ... и переход туда
    if (setns(child_netns, CLONE_NEWNET)) {
        die("cannot setns for child at pid %d: %m\n", child_pid);
    }
```

```c
    // ... и поднятие veth1-интерфейса
    if_up(vpeer, vpeer_addr, netmask);
```

```c
    // ... перед возвращением в наш исходный network namespace.
    if (setns(mynetns, CLONE_NEWNET)) {
        die("cannot restore previous netns: %m\n");
    }
```

```text
    close(sock_fd);
}
```

Затем мы можем вызвать `prepare_netns` сразу после того, как мы закончим настройку нашего user namespace.

```c
    ...
    // Получение записываемого конца пайпа.
    int pipe = params.fd[1];
```

```text
    prepare_userns(cmd_pid);
    prepare_netns(cmd_pid);
```

```c
    // Сигнал командному процессу, что мы закончили настройку.
    ...
```

Давайте попробуем!

```bash
$ sudo ./isolate sh
===========sh============
$ ip link list
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
31: veth1@if32: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP qlen 1000
    link/ether 2a:e8:d9:df:b4:3d brd ff:ff:ff:ff:ff:ff
# Проверим связность между пространствами имён
$ ping 10.1.1.1
PING 10.1.1.1 (10.1.1.1): 56 data bytes
64 bytes from 10.1.1.1: seq=0 ttl=64 time=0.145 ms
```

**********

[Linux](/tags/linux.md)
[namespaces](/tags/namespaces.md)
