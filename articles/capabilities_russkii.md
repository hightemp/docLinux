# Capabilities (Русский)

Источник: [Capabilities (Русский)](https://wiki.archlinux.org/title/Capabilities_(Русский)

Привилегии (POSIX 1003.1e, [capabilities(7)](https://man.archlinux.org/man/capabilities.7)) позволяют предоставить программам доступ к определённым возможностям, которые обычно есть только у суперпользователя, позволяя избежать запуска программ от имени root. Разработчикам программ рекомендуется заменить использование мощного атрибута [setuid](https://en.wikipedia.org/wiki/ru:suid "wikipedia:ru:suid") в системных исполняемых файлах на минимально необходимый программе набор привилегий. Многие пакеты используют привилегии; например, привилегия `CAP_NET_RAW` используется в [fping](https://archlinux.org/packages/?name=fping). Это позволяет запускать `fping` от имени обычного пользователя (как при использовании метода **setuid**), но при этом процесс не получает root-права, что ограничивает возможность эксплуатации потенциальных уязвимостей в `fping`.

## Реализация

Для реализации привилегий в Linux используются [расширенные атрибуты](/title/%D0%A0%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5_%D0%B0%D1%82%D1%80%D0%B8%D0%B1%D1%83%D1%82%D1%8B "Расширенные атрибуты") ([xattr(7)](https://man.archlinux.org/man/xattr.7)) в пространстве имён _security_. Расширенные атрибуты поддерживаются всеми основными [файловыми системами](/title/File_systems_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "File systems \(Русский\)") Linux, в том числе Ext2, Ext3, Ext4, Btrfs, JFS, XFS и Reiserfs. Следующий пример выводит привилегии fping с помощью `getcap`, а затем выводит те же данные в закодированном виде с помощью `getfattr`:

```bash
$ getcap /usr/bin/fping

/usr/bin/fping cap_net_raw=ep

$ getfattr -d -m "^security\\." /usr/bin/fping

# file: usr/bin/fping
security.capability=0sAQAAAgAgAAAAAAAAAAAAAAAAAAA=
```

Расширенные атрибуты копируются автоматически при использовании `cp -a`, но некоторые другие программы требуют специального флага: например, `rsync -X`.

Привилегии устанавливаются install-скриптами в пакетах Arch (например, `fping.install`).

## Администрирование и обслуживание

Если у пакета слишком много ненужных привилегий — это считается ошибкой, о которой стоит сообщить. Использование привилегий, фактически эквивалентных root-доступу (`CAP_SYS_ADMIN`) или позволяющих легко получить root-доступ (`CAP_DAC_OVERRIDE`), ошибкой не считается, так как Arch не поддерживает какую-либо систему [мандатного управления доступом](/title/Security_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\)#Мандатное_управление_доступом "Security \(Русский\)").

**Важно** Многие привилегии позволяют тривиально получить root-доступ. Примеры и объяснения можно посмотреть в сообщении Брэда Шпенглера: [False Boundaries and Arbitrary Code Execution](https://forums.grsecurity.net/viewtopic.php?f=7&t=2522&sid=c6fbcf62fd5d3472562540a7e608ce4e#p10271).

## Программы, для которых удобно использовать привилегии

Перечисленные ниже пакеты не имеют файлов с атрибутом setuid и для работы требуют права root. Для них можно добавить привилегии, чтобы обычные пользователи могли использовать программу без получения root-доступа.

Символы `+ep` означают «effective permitted», подробнее в man-странице [capabilities(7) § File capabilities](https://man.archlinux.org/man/capabilities.7#File_capabilities).

### beep

```text
# setcap cap_dac_override,cap_sys_tty_config+ep /usr/bin/beep
```

### chvt

```text
# setcap cap_dac_read_search,cap_sys_tty_config+ep /usr/bin/chvt
```

### iftop

```text
# setcap cap_net_raw+ep /usr/bin/iftop
```

### mii-tool

```text
# setcap cap_net_admin+ep /usr/bin/mii-tool
```

### mtr

```text
# setcap cap_net_raw+ep /usr/bin/mtr-packet
```

### nethogs

```text
# setcap cap_net_admin,cap_net_raw+ep /usr/bin/nethogs
```

### wavemon

```text
# setcap cap_net_admin+ep /usr/bin/wavemon
```

## Полезные команды

Поиск файлов с setuid-root:

```bash
$ find /usr/bin /usr/lib -perm /4000 -user root
```

Поиск файлов с setgid-root:

```bash
$ find /usr/bin /usr/lib -perm /2000 -group root
```

## Временная выдача привилегий

С помощью [capsh(1)](https://man.archlinux.org/man/capsh.1) можно запустить программу с указанными привилегиями без редактирования расширенных атрибутов исполняемого файла. Следующий пример демонстрирует, как подключиться к процессу через [GDB](/title/GNU_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\)#Инструментарий "GNU \(Русский\)") с помощью привилегии `CAP_SYS_PTRACE`:

```bash
$ sudo -E capsh --caps="cap_setpcap,cap_setuid,cap_setgid+ep cap_sys_ptrace+eip" --keep=1 --user="$USER" --addamb="cap_sys_ptrace" --shell=/usr/bin/gdb -- -p <pid>
```

Пример прослушивания привилегированного порта с помощью [netcat](/title/Network_tools_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\)#Netcat "Network tools \(Русский\)"):

```bash
$ sudo -E capsh --caps="cap_setpcap,cap_setuid,cap_setgid+ep cap_net_bind_service+eip" --keep=1 --user="$USER" --addamb="cap_net_bind_service" --shell=/usr/bin/nc -- -lvtn 123
Listening on 0.0.0.0 123
```

## Смотрите также

  * Man-страницы: [capabilities(7)](https://man.archlinux.org/man/capabilities.7), [setcap(8)](https://man.archlinux.org/man/setcap.8), [getcap(8)](https://man.archlinux.org/man/getcap.8)
  * [Wikibooks:Grsecurity/Appendix/Capability Names and Descriptions](https://en.wikibooks.org/wiki/Grsecurity/Appendix/Capability_Names_and_Descriptions "wikibooks:Grsecurity/Appendix/Capability Names and Descriptions")
  * [Seccomp BPF (SECure COMPuting with filters)](https://docs.kernel.org/userspace-api/seccomp_filter.html)

Retrieved from "[https://wiki.archlinux.org/index.php?title=Capabilities_(Русский)&oldid=788191](https://wiki.archlinux.org/index.php?title=Capabilities_\(Русский\)&oldid=788191)"

[Category](/title/Special:Categories "Special:Categories"):

  * [Security (Русский)](/title/Category:Security_\(%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9\) "Category:Security \(Русский\)")

**********

[capabilities](/tags/capabilities.md)
