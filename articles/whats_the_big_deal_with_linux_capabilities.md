# Что такого особенного в Linux Capabilities?

Источник: [What's The Big Deal With Linux Capabilities?](https://hackernoon.com/whats-the-big-deal-with-linux-capabilities)

inaeem (HackerNoon) · 1 декабря 2021 · live @ PID 1

![featured image - What's The Big Deal With Linux Capabilities?](/images/64ae6028fa705ac6e20cca8e2610577c.png)

Распространено представление, что в Linux привилегиями пользуются и обладают пользователи, однако это не так. Именно процесс или исполняемый файл, работающий в контексте определённого пользователя, осуществляет права (разрешение выполнять привилегированные операции, охраняемые ядром Linux).

Возможности (capabilities) есть у процессов, а не у пользователей.

В Unix-подобных системах традиционная стратегия работы с **привилегиями процессов — бинарный дизайн (привилегированные процессы и непривилегированные процессы)**. То есть процесс может работать от имени root и иметь полный доступ к системе, либо работать как обычный пользователь без прав root и не иметь возможности выполнять привилегированные действия.

**Привилегированные процессы**: привилегированные процессы обходят все проверки разрешений безопасности ядра. Например, мониторинг производительности perf events полностью доступен привилегированным процессам без каких-либо ограничений доступа, области действия или ресурсов.

Привилегированные процессы (эффективный идентификатор пользователя равен 0)

**Примечание: (Effective User ID == 0)** — это так называемый суперпользователь, или root.

**Непривилегированные процессы** подвергаются полной проверке разрешений безопасности на основе учётных данных процесса (обычно: эффективный UID, эффективный GID).

Непривилегированные процессы (эффективный идентификатор пользователя не равен нулю)

Хотя этот простой дизайн удобен для системных администраторов, которым нужен полный доступ к системе для выполнения критических операций (установка обновлений, добавление пользователей, резервное копирование, монтирование файловых систем, перезагрузка системы и т.д.), он создаёт трудности для операторов системы (HR, финансы и т.д.), когда им нужно выполнять ограниченные операции или обращаться к файлам, принадлежащим другим пользователям, в их повседневной работе.

## Но у нас уже есть DAC

DAC (Discretionary Access Control, дискреционное управление доступом) установлен по умолчанию в файловой системе Linux (файлы/каталоги/устройства), чтобы разрешить управлять доступом. Владельцы файлов или каталогов имеют абсолютную власть над тем, кто имеет доступ к их файлам и какие действия они могут выполнять.

Когда **непривилегированный процесс (Effective User ID != 0)** запрашивает доступ к системе, ядро Linux проводит проверки контроля доступа на основе привилегированного доступа пользователя.

**Недостатки DAC**

* Пользователи с привилегиями root не подчиняются модели безопасности Linux.
* Пользователи root получают полный доступ к системе, минуя все проверки безопасности в ядре.

* * *

## Разделение прав root

Capabilities в Linux используются для предоставления мелкозернистого доступа к ресурсам ядра, который ранее был недоступен непривилегированным процессам. Вместо того чтобы разом выдавать целевому процессу полный доступ, ядро Linux разделяет права root на более мелкие части, которые можно выдавать по отдельности для каждого потока.

В man-странице capabilities [1] есть полный список всех доступных capabilities.

```bash
# A complete list of all available capabilities is present
# in the capability manual page [1].
$ man capabilities

# -------------------- #
# Alternative would be
# -------------------- #

# Capability supported by your kernel
$ cat /proc/sys/kernel/cap_last_cap
37
```

Модель привилегий Linux делит привилегию root на **38+ capabilities**, которые пользователи без root могут использовать для выполнения привилегированных действий (таких как системные вызовы или манипуляции данными).

* Привилегии можно включать у процессов и файлов.
* Каждая привилегированная операция всегда проверяется по соответствующим capabilities (а не по EUID == 0).
* При UID 0 все capabilities включены по умолчанию. Для всех привилегированных операций ядро должно проверять, есть ли у потока требуемая capability в его эффективном наборе.
* Ядро должно предоставлять системные вызовы для изменения и возврата наборов capabilities потока.
* Файловая система должна поддерживать прикрепление capabilities к исполняемому файлу, чтобы процесс получал эти capabilities при выполнении файла.

* * *

## Наборы capabilities процесса

Существует пять различных наборов capabilities, которые можно включать для каждого процесса (потока); каждый представлен 64-битным числом и может содержать ноль или более capabilities.

## Эффективный набор (Effective Capabilities Set)

Эффективный набор помогает ядру узнать окончательные разрешения процесса.

Когда процесс пытается выполнить привилегированную операцию, ядро проверяет, установлен ли соответствующий бит в эффективном наборе. Например, когда процесс запрашивает установку монотонных часов, ядро сначала проверяет, установлен ли бит **CAP_SYS_TIME** в эффективном наборе процесса.

## Разрешённый набор (Permitted Capabilities Set)

Разрешённый набор показывает, какие capabilities процесс может использовать, и ограничивает содержимое эффективного набора.

Процесс может иметь capabilities, установленные в «разрешённом наборе», но не в эффективном. Это значит, что процесс временно отключил эту capability. Процесс может установить бит в своём эффективном наборе, только если он присутствует в разрешённом наборе.

## Наследуемый набор (Inheritable Capabilities Set)

Наследуемые capabilities — это capabilities текущего процесса, которые должны быть унаследованы программой, запущенной текущим процессом.

Разрешённый набор процесса маскируется наследуемым набором при **exec()**, тогда как дочерние процессы и потоки получают точную копию capabilities родительского процесса. Также заметьте, что «наследование» capability не обязательно автоматически даёт какому-либо потоку эффективные capabilities. «Унаследованные» capabilities напрямую влияют только на разрешённый набор нового потока.

## Ограничивающий набор (Bounding Capabilities Set)

Можно ограничить capabilities, которые процесс вообще когда-либо сможет получить, с помощью «bounding set».

В наследуемом и разрешённом наборах будут допустимы только capabilities, входящие в ограничивающий набор. Он используется для ограничения capabilities программы. У вас не может быть какой-либо capability в других наборах, если её нет в ограничивающем наборе.

## Ambient-набор (Ambient Capabilities Set)

Ambient-набор capabilities применяется ко всем не-SUID-бинарникам, не имеющим файловых capabilities.

Ambient capabilities — это capabilities, сохраняемые при **execve()**. Однако сохраняются не все capabilities из ambient-набора: они сбрасываются, если не входят ни в наследуемый, ни в разрешённый набор.

* * *

## Просмотр capabilities процесса

## 1. Файловая система proc (procfs)

Чтобы увидеть capabilities конкретного процесса, используйте файл status в каталоге **/proc/\<PID\>/**.

Capabilities процесса выражены в шестнадцатеричном формате.

**CapInh** = наследуемые capabilities

**CapPrm** = разрешённые capabilities

**CapEff** = эффективные capabilities

**CapBnd** = ограничивающий набор

**CapAmb** = ambient-набор capabilities

Давайте посмотрим на capabilities процесса утилиты **Ping**. Вы можете задаться вопросом, почему эффективные capabilities равны нулю. Простейший ответ: ping — это **приложение, осведомлённое о capabilities** (Capability Aware Application), то есть оно может сбрасывать часть или все эффективные capabilities, когда они больше не нужны, чтобы уменьшить поверхность атаки. Оно всё ещё может вернуть capability в эффективный набор, пока эта capability есть у него в разрешённом наборе.

```text
# Mute the output and get process id
~$ ping 127.0.0.1 > /dev/null &
[1] 21002
~$ cat /proc/21002/status | grep Cap
CapInh: 0000000000000000
CapPrm: 0000000000003000
CapEff: 0000000000000000
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
```

## 2. Используйте команду getpcaps

Альтернатива — использовать утилиту **getpcaps**, чтобы отобразить capabilities конкретного процесса.

**getpcaps** преобразует capabilities в корректные имена:

```text
# suppress the output and get process id
~$ ping 127.0.0.1 > /dev/null &
[1] 21002
~$ getpcaps 21002
Capabilities for `21002': = cap_net_admin,cap_net_raw+p
```

## 3. Используйте утилиту pscap

Аналогично, с помощью **утилиты pscap** мы можем сформировать отчёт о capabilities всех запущенных процессов.

```bash
$ pscap -a
ppid  pid   name        command           capabilities
0     1     root        systemd           full
1     419   root        systemd-journal   chown, dac_override, dac_read_search, fowner, setgid, setuid, sys_ptrace, sys_admin, audit_control, mac_override, syslog, audit_read
1     447   root        lvmetad           full
1     457   root        systemd-udevd     full
1     589   systemd-timesync  systemd-timesyn   sys_time
```

* * *

## Декодирование capabilities процесса

Утилита **capsh** декодирует значение capability, представленное в шестнадцатеричном виде, в имя capability.

Файловая система proc **(procfs)** перечисляет capabilities процесса в шестнадцатеричном формате.

```text
~$ cat /proc/21002/status | grep Cap
CapInh: 0000000000000000
CapPrm: 0000000000003000
CapEff: 0000000000000000
CapBnd: 0000003fffffffff
CapAmb: 0000000000000000
# Decode raw capabilities
~$ capsh --decode=0000000000003000
0x0000000000003000=cap_net_admin,cap_net_raw
~$ capsh --decode=0000000000003000
0x0000001fffffffff=cap_chown,cap_dac_override,
cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,
cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,
cap_net_bind_service,cap_net_broadcast,cap_net_admin,
cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,
cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,
cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,
cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,
cap_audit_write,cap_audit_control,cap_setfcap,
cap_mac_override,cap_mac_admin,cap_syslog,35,36

# -------------------- #
# Alternative would be
# -------------------- #

~$ for line in $(grep Cap /proc/21002/status | awk '{print $2}'); do capsh --decode=$line; done;
0x0000000000000000=
0x0000000000003000=cap_net_admin,cap_net_raw
0x0000000000000000=
0x0000001fffffffff=cap_chown,cap_dac_override,
cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,
cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,
cap_net_bind_service,cap_net_broadcast,cap_net_admin,
cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,
cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,
cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,
cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,
cap_audit_write,cap_audit_control,cap_setfcap,
cap_mac_override,cap_mac_admin,cap_syslog,35,36
0x0000000000000000=
```

* * *

## Сброс capabilities процесса

Утилиту **capsh** можно использовать для сброса capability, передав либо \--drop, либо \--uid.

Аргумент **UID** приводит к потере потоком всех capabilities.

```bash
~$ sudo capsh --caps="cap_setpcap,cap_setuid,cap_setgid+ep" \
--drop="cap_net_admin,cap_net_raw" --keep=1 --uid=1001 \
--print -- -c "ping localhost"
Current: = cap_setgid,cap_setuid,cap_setpcap+p Bounding set =
Securebits: 020/0x10/5'b10000
secure-noroot: no (unlocked)
secure-no-suid-fixup: no (unlocked)
secure-keep-caps: yes (unlocked) uid=1001(test1) gid=0(root) groups=0(root)
ping: socket: Operation not permitted Super-powers are granted randomly so please submit an issue if you're not happy with yours.

# -------------------- #
# Alternative would be
# -------------------- #

$ sudo capsh --drop=cap_net_raw --print -- -c "/bin/ping -c 1 localhost"
Current: = cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,35,36,37+ep
Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,35,36,37
Securebits: 00/0x0/1'b0
 secure-noroot: no (unlocked)
 secure-no-suid-fixup: no (unlocked)
 secure-keep-caps: no (unlocked)
uid=0(root)
gid=0(root)
groups=0(root)
ping: socket: Operation not permitted
```

* * *

## Capabilities файлов (бинарников)

С исполняемым файлом можно ассоциировать **три различных набора capabilities**. Ядро вычисляет capabilities нового процесса **в сочетании с текущими capabilities процесса и capabilities файла (бинарника)**.

## Разрешённый набор файла (бинарника)

Эти capabilities добавляются к разрешённому набору процесса при выполнении.

## Наследуемый набор файла (бинарника)

После **execve()** пересечение (логическое И) наследуемого набора потока и наследуемого набора файла добавляется к разрешённому набору потока.

## Эффективный флаг файла (бинарника)

В отличие от других файловых наборов capabilities, это просто флаг. Когда флаг установлен, эффективный набор процесса после execve() устанавливается равным новому разрешённому набору процесса; иначе он пуст.

* * *

## Поиск capabilities бинарников

В зависимости от сценария нам может понадобиться искать файлы с включёнными capabilities.

## 1. Используйте утилиту getcap

Чтобы найти все файлы с установленными файловыми capabilities, используйте **getcap -r**.

Злонамеренный пользователь может с помощью **getcap -r** найти в системе эксплойтабельный исполняемый бинарник.

```bash
$ getcap -r / 2>/dev/null
/home/ubuntu/environment/cat_clone = cap_setuid+ep
/home/ubuntu/environment/top_clone = cap_chown+ep
/home/ubuntu/environment/ping_clone = cap_net_raw+p
/usr/bin/mtr-packet = cap_net_raw+ep
```

## 2. Используйте утилиту filecap

**Утилита filecap** выполняет аналогичную работу, перечисляя capabilities файлов.

```text
~$ filecap /usr
file                 capabilities
/usr/bin/mtr-packet     net_
```

## 3. Используйте утилиту pscap

Аналогично, мы можем найти набор capabilities всех запущенных процессов с помощью утилиты **pscap**.

```text
# pscap -a
ppid  pid   name        command           capabilities
6148  6152  root        bash              full
```

## Установка capabilities бинарнику

Утилита **setcap** добавляет capabilities к исполняемому файлу как разрешённые и эффективные.

Только привилегированные пользователи (CAP_SETFCAP) могут выполнять эту операцию.

`$ setcap cap_net_raw,cap_net_admin+ep ping_clone unable to set CAP_SETFCAP` effective capability: Operation not permitted

## 1. Наследуемый набор файла

Добавьте **cap_net_raw** в наследуемый набор файла.

```text
# Privileged ping binary
~# setcap cap_net_raw+i ping_clone
~$ getcap ping_clone
ping_clone = cap_net_raw+i
```

## 2. Разрешённый набор файла

Добавьте **cap_net_raw, cap_net_admin** в разрешённый набор файла.

```text
# Privileged ping binary
~# setcap cap_net_raw,cap_net_admin+p ping_clone
~$ getcap ping_clone
ping_clone = cap_net_raw,cap_net_admin+p
```

## 3. Эффективный бит/флаг файла

Включение эффективного флага файла приводит к автоматическому переносу разрешённого набора потока в эффективный набор потока.

```text
# Privileged ping binary
~# setcap ping_clone
ping_clone = cap_net_raw,cap_net_admin+ep
~$ getcap ping_clone
ping_clone = cap_net_raw,cap_net_admin+ep
```

## Просмотр capabilities бинарника

Чтобы изучить файловые capabilities исполняемого файла, используйте утилиту **getcap**.

```text
~$ getcap ping_clone
ping_clone = cap_net_raw+i
```

Альтернативная техника — сравнить набор capabilities файла с произвольным значением и проверить совпадение.

Используйте **setcap -v** для проверки файловых capabilities.

```bash
# When it confirms file capabilities
$ setcap -v cap_net_admin,cap_net_raw+ep ping_clone
ping_clone: OK
# When file capabilities differs
$ setcap -v cap_net_raw+ep ping_clone
ping_clone differs in [pe]
```

* * *

В следующей главе мы посмотрим, как определяются наборы capabilities для непривилегированных и привилегированных бинарников после execve(2).

Продолжение следует…

**********

[capabilities](/tags/capabilities.md)
[linux](/tags/linux.md)
[proc](/tags/proc.md)