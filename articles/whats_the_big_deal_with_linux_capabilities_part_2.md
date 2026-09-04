# В чём суть Linux Capabilities? (Часть 2)

Источник: [What's the Big Deal with Linux Capabilities? (Part 2)](https://hackernoon.com/whats-the-big-deal-with-linux-capabilities-part-2)

inaeem · 10 декабря 2021 · 1790 прочтений

Эта история — продолжение [предыдущей](https://hackernoon.com/whats-the-big-deal-with-linux-capabilities?ref=hackernoon.com), в которой мы подробно обсудили наборы возможностей (Capabilities Sets) процесса. Некоторые из вас могут спрашивать себя, как эти **наборы возможностей** определяются или применяются к **непривилегированным и привилегированным бинарникам программ**. Эта статья предназначена для них.

Прежде чем начать детально описывать механику создания процессов и возможности Linux, я хотел бы пройтись по двум ключевым концепциям.

## Приложения, знающие о возможностях (Capability Aware Applications)

Приложения, знающие о возможностях (capability-aware), могут манипулировать своим набором возможностей с помощью системных вызовов (**capset, capget, prctl**) после загрузки. В какой-то момент исполнения, когда приложению больше не нужны определённые возможности, оно может сбросить некоторые возможности из своего эффективного набора, чтобы ограничить риск для привилегированных задач. Пока возможность присутствует в разрешённом (permitted) наборе, оно всегда может вернуть её в свой эффективный набор.

Например, runc, ping и т.д.

## Приложения, не знающие о возможностях (Capability Dump Applications)

Приложения не делают никаких системных вызовов (capset) для изменения своих возможностей и полагаются на наборы возможностей, унаследованные от родителя и сформированные при загрузке приложения. Другими словами, они полагаются на эффективный набор возможностей для выполнения своей работы.

Например, cat, ls и т.д.

**********

# Непривилегированный бинарник программы

Непривилегированный бинарник программы (Unprivileged Program Binary) — это когда на исполняемом файле не включены **файловые возможности (File Capabilities)**. Когда мы загружаем непривилегированный бинарник (например, ls, cat), наборы возможностей потока (родителя) вместе с битом SETUID файла используются для определения возможностей этого потока после execve(2).

В случае непривилегированного бинарника программы ambient-возможности (окружающие) критичны для определения возможностей потока.

Давайте посмотрим, как определяются наборы возможностей для непривилегированного бинарника после execve(2) при определённых условиях.

## Переход возможностей (Capabilities Transition)

![Непривилегированный бинарник программы — переход возможностей](/images/a3a22a4afef0e1da4356d92f8392a921.png)

## Пояснение

- **inheritable & bounding:** В наследуемом (inheritable) и ограничивающем (bounding) наборах изменений не будет.
- **effective & permitted:** Эти возможности теряются во время execve() и пересчитываются на основе ambient-возможностей.
- **ambient:** Ambient-возможности введены для усиления возможностей, потерянных в эффективном и разрешённом наборах.

Ambient-возможности должны присутствовать в ограничивающем наборе.

## Сценарий №1: Непривилегированный bash-процесс

Непривилегированный пользователь (bash-процесс) использует исполняемый файл ping, чтобы пропинговать локальный сервер.

**Условия:**

- **Владелец файла:** бит setuid не установлен && владелец == root
- **Родительский процесс:** непривилегированный bash-процесс работает без возможностей или с ограниченными возможностями
- **Исполняемый бинарник:** непривилегированный бинарник ping.

## Схематичная диаграмма

![Схематичная диаграмма непривилегированного bash-процесса](/images/d24d7d21850c7d7af7e3166a1f32697b.png)

## Подготовка окружения

```bash
# File Ownership: setuid bit != set && owner == root
$ ls -la ping_clone
-rwxr-xr-x ... root root ... ping_clone

# Parent Process: Unprivileged bash proces which runs with no
# or limited capabilities
$ capsh --print
Current: =
Bounding set =cap_chown,cap_dac_override, .....
 .....
uid=1000(ubuntu)
gid=1000(ubuntu)

# Executable Binary: Unprivileged ping binary
$ getcap ping_clone
```

## Демо №1: Использование утилиты capsh

Используйте утилиту capsh, чтобы поднять непривилегированный bash-процесс, а затем пропинговать локальный сервер.

```bash
$ sudo capsh --caps="cap_net_admin,cap_net_raw,cap_setpcap,cap_setuid,cap_setgid+ep"
--keep=1 --user=ubuntu --addamb="cap_net_admin,cap_net_raw" --print -- -c "./ping_clone -c 1 localhost"
Current: = cap_setgid,cap_setuid,cap_setpcap,cap_net_admin,cap_net_raw+p
Bounding set = cap_chown,cap_dac_override,cap_dac_read_search,
    cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,
    cap_setpcap,cap_linux_immutable,cap_net_bind_service,
    cap_net_broadcast,cap_net_admin,cap_net_raw,
    cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,
    cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,
    cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,
    cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,
    cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,
    cap_syslog,35,36,37
Securebits: 020/0x10/5'b10000
 secure-noroot: no (unlocked)
 secure-no-suid-fixup: no (unlocked)
 secure-keep-caps: yes (unlocked)
uid=1000(ubuntu)
gid=1000(ubuntu)
groups=4(adm),10(wheel),190(systemd-journal),991(docker),1000(ubuntu)
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=255 time=0.033 ms
--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.033/0.033/0.033/0.000 ms
```

Так что же здесь происходит? Давайте посмотрим:

- **Current & Bounding set:** Создают благоприятное окружение для ping_clone, а именно:

sudo(root)───>su───>bash───>ping_clone(ubuntu)

- **\--user=$USER:** Сбрасывает все возможности при смене UID, так как мы переходим от **root** к **$USER**.

- **\--addamb=cap_net_raw:** Добавляет ambient-набор к эффективному и разрешённому наборам при исполнении непривилегированных бинарников.

## Демо №2: Использование утилиты **setpriv**

Возможно, вам понадобится установить **утилиту setpriv**.

```bash
$ sudo apt install setpriv
```

Мы будем использовать **утилиту setpriv**, чтобы запустить бинарник ping_clone от непривилегированного пользователя.

```bash
$ sudo setpriv --inh-caps '-all,+net_raw' \
--bounding-set '-all,+net_raw' \
--reuid=ubuntu \
--ambient-caps='+net_raw' \
./ping_clone -c1 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.019 ms
--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.019/0.019/0.019/0.000 ms
```

Когда аргумент --ambient-caps не передан, утилита ping_clone пожалуется на 'socket: Operation not permitted'.

Итак, что же здесь происходит? Позвольте прояснить.

- **\--reuid=ubuntu:** Все эффективные и разрешённые наборы возможностей будут сброшены с бинарника ping_clone.

- **\--ambient-caps=+net_raw:** Пересчитывает эффективный и разрешённый наборы возможностей на основе заданных ambient-наборов возможностей.

**********

## Сценарий №2: Привилегированный bash-процесс

Привилегированный пользователь (bash-процесс) пингует локальный сервер, используя непривилегированный бинарник ping.

**Условия**

- **Владелец файла:** бит setuid не установлен && владелец == root.
- **Родительский процесс:** привилегированный bash-процесс работает со всеми включёнными возможностями.
- **Исполняемый бинарник:** непривилегированный бинарник ping (файловые возможности не установлены).

## Схематичная диаграмма

![Схематичная диаграмма привилегированного bash-процесса](/images/383d8979435bdc96d709229a2828d955.png)

## Подготовка окружения

```bash
# File Ownership: setuid bit != set && owner == root.
$ ls -la ping_clone
-rwxr-xr-x ... root root ... ping_clone

# Parent Process: Privileged bash process runs with full capabilities.
$ capsh --print
Current: = cap_net_admin,cap_net_raw,cap_chown,cap_dac_override, .....
Bounding set = cap_net_admin,cap_net_raw,cap_chown,cap_dac_override, .....
 .....
uid=0(root)
gid=0(root)
...

# Executable Binary: Unprivileged ping binary (file capabilities aren't set).
$ getcap ping_clone
```

## Переход возможностей

Когда вы входите как root, ваш эффективный идентификатор пользователя (Effective User ID) устанавливается в 0, и вы получаете неограниченный доступ к системе, чтобы делать (почти) всё, что хотите.

**Вход как пользователь root объясняет всё.**

При (Effective User ID == 0) bash-процесс становится привилегированным процессом. Несмотря на то, что все возможности Linux включены, ядро обычно пропускает все проверки ограничений, когда Effective User ID == 0.

**********

## Сценарий №3: Специальные права (SUID, SGID)

**Set User ID** (setuid) и **Set Group ID** (sgid) — это специальные права для исполняемых файлов.

Когда эти права назначены файлу, исполняемый файл принимает привилегии владельца или группы файла.

Бит **setuid** меняет эффективный uid программы (euid) при исполнении.

Условия:

- **Владелец файла:** бит setuid установлен && владелец == root.
- **Родительский процесс:** непривилегированный bash-процесс (без возможностей или с ограниченными).
- **Исполняемый бинарник:** непривилегированный бинарник ping (файловые возможности не установлены).

## Схематичная диаграмма

![Специальные права (SUID, SGID) — схематичная диаграмма](/images/86751f3a214d8c5b7598b478d42db33d.png)

## Подготовка окружения

```bash
# File Ownership: setuid bit == set && owner == root.
$ ls -la ping_clone
-rwsr-xr-x ... root root ... ping_clone

# Parent Process: Unprivileged bash process(no or limited capabilities).
$ capsh --print
Current: =
Bounding set =cap_chown,cap_dac_override, .....
 .....
uid=1000(ubuntu)
gid=1000(ubuntu)
...

# Executable Binary: Unprivileged ping binary. (file capabilities aren't set).
$ getcap ping_clone
# setuid bit set
$ ls -la
...
-rwsr-xr-x ... root root ... ping_clone
```

## Переход возможностей

Когда пользователь без прав root исполняет утилиту ping_clone, принадлежащую пользователю root и с установленным битом setuid, файл всегда будет работать в контексте пользователя root (EUID = 0), пока программа не изменит свой эффективный uid (euid) во время исполнения.

```text
~$ ping_clone localhost &
[1] 31994
~# PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.027 ms

~$ cat /proc/31994/status
Name:   ping_clone
...
...
Uid:    1000    1000    0       1000
Gid:    1000    1000    1000    1000
...
CapInh: 0000000000000000
CapPrm: 0000000000003000
CapEff: 0000000000000000
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
...
```

Так, что же здесь происходит?

- **uid=1000:** Разве не должно быть Uid: 1000 0 0 0, как утверждается выше?
- **CapPrm: 0000000000003000:** Разрешённый набор сокращён до **cap_net_admin**, **cap_net_raw**.
- **CapEff: 0000000000000000:** Как процесс выполняет привилегированные сетевые действия, если эффективные наборы пусты?

Давайте посмотрим на **утилиту ping_clone** с точки зрения системных вызовов. Помните, что это **приложение, знающее о возможностях**, которое может менять свои возможности программно.

![strace-вывод утилиты ping_clone](/images/3244c17c1c1464cb99175d7a7391d874.png)

Взгляните на вывод **инструмента трассировки strace**.

- **В строке 4:** Получает все возможности в наборах {effective, permitted}.
- **В строке 6:** Сбрасывает все эффективные возможности и удаляет все ненужные возможности из разрешённого набора, оставляя только **CAP_NET_ADMIN и CAP_NET_RAW**.
- **В строке 7:** **prctl(PR_SET_KEEPCAPS, 1)** используется для сохранения наборов возможностей при будущем переходе EUID.
- **В строке 9:** Меняет эффективный идентификатор пользователя на менее привилегированного.
- **В строке 21:** Набор возможностей **CAP_NET_RAW** восстановлен как эффективный набор возможностей для чувствительных сетевых операций.

**********

# Привилегированный бинарник программы

Привилегированный бинарник программы (Privileged Program Binary) означает, что исполняемому файлу назначены определённые возможности. Когда мы загружаем привилегированный бинарник (например, ping clone), набор возможностей исполняемого файла играет значительную роль для потока после **execve(2)**.

Используйте **утилиту getcap**, чтобы определить привилегированный статус бинарника программы.

## Переход возможностей

![Привилегированный бинарник программы — переход возможностей](/images/030db0bdc56a5b63645fae2ce34e10ed.png)

## Пояснение

- **ambient:** Ambient-возможности не играют роли в переходе возможностей и устанавливаются в ноль.
- **inheritable & bounding:** В наследуемом и ограничивающем наборах изменений не будет.
- **permitted:** Логика определения финального состояния разрешённого набора сложна. Всё зависит от старых наследуемых возможностей и файловых возможностей и подчиняется следующей логике перехода:

```text
* File permitted set and old bounding set (before execve()) are logically ANDed.
```

_P1 = Bounding Old & File Permitted Set_

```text
* File inheritable set and old inheritable set (before execve()) are logically ANDed.
```

P2 = Inheritable Old & File Inheritable Set

```text
* Final state of permitted set is calculated by doing logical OR P1 and P2.
```

P = P1 | P2

- **effective:** Логика перехода следующая:

```text
* **Capabilities Aware Application has the luxury to activate/deactivate a capability** in permitted set as effective capability whenever required.
* **File effective flag/bit is introduced for Capabilities Unaware Applications** (Dump applications) to control the auto enforcement of permitted set as effective set after **execve()**.
```

## Сценарий №1: Непривилегированный bash-процесс

Непривилегированный пользователь (bash-процесс) пингует локальный сервер, используя привилегированный бинарник ping.

**Условия:**

- **Владелец файла:** бит setuid не установлен && владелец != root.
- **Родительский процесс:** непривилегированный bash-процесс (без возможностей или с ограниченными)
- **Исполняемый бинарник:** привилегированный бинарник ping (файловые возможности установлены с помощью **capset()**)

## Схематичная диаграмма

![Привилегированный бинарник программы — схематичная диаграмма](/images/44745c54e682ba9bf40429df9b221719.png)

## Подготовка окружения

```bash
# setuid bit != set && owner != root
$ ls -la ping_clone
-rwxr-xr-x ... ubuntu ubuntu ... ping_clone

# Privileged ping binary
$ getcap ping_clone
ping_clone = cap_net_raw+i

# Unprivileged User
$ capsh --print
Current: =
Bounding set =cap_chown,cap_dac_override, .....
 .....
uid=1000(ubuntu)
gid=1000(ubuntu)
...
```

## Пример №1: Когда файловый наследуемый набор установлен

**Условие:** Убедитесь, что для **утилиты ping_clone** установлена **cap_net_raw** как её наследуемая возможность.

**Терминал 1**

```bash
# Privileged ping binary
$ getcap ping_clone
ping_clone = cap_net_raw+i

$ sudo capsh
--caps="cap_net_admin,cap_net_raw,cap_setpcap,cap_setuid,cap_setgid+ep"
--keep=1 --user=ubuntu --inh="cap_net_raw"
--print -- -c "./ping_clone localhost"
Current: = cap_net_raw+ip cap_setgid,cap_setuid,cap_setpcap,cap_net_admin+p
Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read
Securebits: 020/0x10/5'b10000
 secure-noroot: no (unlocked)
 secure-no-suid-fixup: no (unlocked)
 secure-keep-caps: yes (unlocked)
uid=1000(ubuntu)
gid=1000(ubuntu)
groups=4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),108(lxd),114(netdev),999(docker),1000(ubuntu)
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.023
```

**Терминал 2**

```bash
$ cat /proc/4696/status | grep Cap
CapInh: 0000000000000000
CapPrm: 0000000000002000
CapEff: 0000000000000000
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
```

Так что же здесь происходит? Давайте посмотрим:

- **\--user=$USER:** Нам нужен менее привилегированный сеанс bash с нужными возможностями перед запуском ping_clone.
- **\--inh=cap_net_raw:** Сеанс bash должен включить cap_net_raw в наследуемый набор согласно логике перехода возможностей для привилегированного бинарника программы.
- **Terminal 1#7 Current:** Мы хотим убедиться, что **cap_net_raw** присутствует в наследуемом наборе сеанса bash.

## Пример №2: Файловый разрешённый набор установлен

Когда файловый разрешённый набор ограничен **cap_net_raw**.

**Терминал 1**

```bash
# Privileged ping binary
$ getcap ping_clone
ping_clone = cap_net_raw+p

$ sudo capsh
--caps="cap_net_admin,cap_net_raw,cap_setpcap,cap_setuid,cap_setgid+ep"
--user=ubuntu
--print -- -c "./ping_clone localhost"
Current: =
Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read
Securebits: 020/0x10/5'b10000
 secure-noroot: no (unlocked)
 secure-no-suid-fixup: no (unlocked)
 secure-keep-caps: yes (unlocked)
uid=1000(ubuntu)
gid=1000(ubuntu)
groups=4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),108(lxd),114(netdev),999(docker),1000(ubuntu)
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.023 ms
```

**Терминал 2**

```bash
$ cat /proc/4696/status | grep Cap
CapInh: 0000000000000000
CapPrm: 0000000000002000
CapEff: 0000000000000000
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
```

Так что же здесь происходит? Поясним:

- **\--user=$USER:** Снова нам нужен менее привилегированный сеанс bash с определёнными возможностями перед запуском ping_clone.
- **\--inh=cap_net_raw:** Мы намеренно убрали этот аргумент, чтобы доказать, что ping_clone всё ещё работает без наследуемых возможностей.
- **Terminal 1#9 Current:** Это нормально, поскольку мы не указали аргумент **\--keep**, чтобы сбросить разрешённый набор из родительского сеанса bash после **fork()**.

## Пример №3: Когда файловый эффективный бит установлен

Файловый эффективный бит имеет больше смысла, когда бинарники приложений вроде cat, nice и т.д. не знают о системных вызовах **capget()** и **capset()** и не могут менять свой эффективный набор потока. В этом случае они полагаются на внешние условия, такие как файловый эффективный бит, чтобы скопировать все возможности разрешённого набора в эффективный набор.

Вместо **утилиты ping_clone** мы будем использовать для демонстрации утилиту top_clone.

**Терминал 1**

```bash
# Privileged ping binary
$ getcap top_clone
top_clone = cap_chown+ep

$ ./top_clone
....
uid=1000(ubuntu)
top - 09:44:35 up 13:25,  0 users,  load average: 0.15, 0.05, 0.01
Tasks: 120 total,   2 running,   79 sleeping,   0 stopped,   0 zombie
.....
```

**Терминал 2**

```text
CapInh: 0000000000000000
CapPrm: 0000000000000001
CapEff: 0000000000000001
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
```

Так что происходит с возможностями потока:

- **Terminal 2#2 CapPrm:** Приведённый выше переход возможностей поможет нам определить финальное состояние разрешённого набора потока (0x0000000000000001=cap_chown), которое совпадает с файловым разрешённым набором.

```bash
$ getcap top_clone
top_clone = cap_chown+ep
```

- **Terminal 2#3 CapEff:** Поскольку для top_clone установлен файловый флаг/бит effective, он автоматически копирует разрешённый набор в эффективный набор.

```text
CapPrm: 0000000000000001
CapEff: 0000000000000001
```

**********

[linux](/tags/linux.md)
[capabilities](/tags/capabilities.md)
[security](/tags/security.md)