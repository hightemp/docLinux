# Journalctl — анализ логов Linux

Источник: [Journalctl — анализ логов Linux](https://vk.com/@greyteam-kak-ispolzovat-journalctl-dlya-analiza-logov-na-linux)

systemd – это системный менеджер по умолчанию в большинстве основных дистрибутивов Linux, который поставляется с новым демоном ведения журнала под названием «journald».

В течение многих лет системные логи и журналы ядра в традиционной системе SysVinit обрабатывались syslogd, который хранит логи в простых текстовых файлах, тогда как journald хранит логи в двоичном формате.

systemd собирает логи из нескольких источников, таких как система, ядро и различные службы или демоны, и предоставляет решение для централизованного управления через journald.

Это очень оптимизированный процесс, и логи можно просматривать в зависимости от требований, тогда как журналы syslogd анализируются вручную с помощью различных команд, таких как find, grep, cut и т. д.

В этой статье мы продемонстрируем, как просматривать и анализировать системные логи Linux с помощью команды journalctl.

### Что такое journald?

journald – это демон из systemd, который собирает логи из различных источников, таких как система, ядро и службы, и сохраняет их в двоичном формате для упрощения манипуляций.

Все эти события журналирования обрабатываются демоном journald, который обеспечивает централизованный способ обработки журналов независимо от того, откуда исходят сообщения.

### Что такое journalctl?

journalctl – это инструмент командной строки, используемый для просмотра логов, которые собирает демон journald в systemd.

Логи хорошо проиндексированы и структурированы таким образом, что позволяет системным администраторам легко анализировать их и управлять ими на основе различных параметров, таких как фильтрация логов по времени, последовательности загрузки, конкретной службе, серьезности и т. д.

### 1) Как сделать логи постоянным в вашей системе?

По умолчанию логи включены в большинстве дистрибутивов Linux, но данные журнала хранятся в папке «/run/log/journal/», которая по умолчанию стирается при перезагрузке.

Чтобы сделать их постоянными, выполните следующие действия, которые автоматически создадут для вас каталог «/var/log/journal/».

Обратите внимание: каталог «/var/log/journal/» должен существовать с правильным владельцем и правами, чтобы служба systemd-journald могла хранить свои данные.

От пользователя root откройте файл «/etc/systemd/journald.conf» и раскомментируйте строку, содержащую **«Storage = auto»** , и измените ее на **«Storage = persistent»**.

В качестве альтернативы вы можете использовать команду sed для замены соответствующей строки в файле.

```bash
$ sudo sed -i '/Storage/ c\Storage=persistent' /etc/systemd/journald.conf
```

После внесения изменений вы можете подтвердить их вступление в силу, выполнив следующую команду:

```bash
$ cat /etc/systemd/journald.conf

[Journal]
Storage=persistent
#Compress=yes
#Seal=yes
#SplitMode=uid
#SyncIntervalSec=5m
#RateLimitIntervalSec=30s
#RateLimitBurst=1000
```

Перезапустите systemd-journald, как показано ниже:

```bash
$ sudo systemctl restart systemd-journald
```

Измените права доступа к файлу, как показано ниже:

```text
sudo chown -R root:systemd-journal /var/log/journal
```

Теперь вы сможете просматривать журналы из следующего каталога:

```bash
$ ls -lh /var/log/journal
total 0
drwxr-sr-x 1 root systemd-journal 392 Mar 15 15:56 7a138ee71db94e8785d1a4dbe54dde7e
```

### 2) Понимание полезных флагов journalctl

Прежде чем переходить к команде Journalctl, вы должны знать список часто используемых флагов, которые упростят использование journalctl.

Они перечислены ниже:

  * -f: показывает только самые последние логи и сообщения журнала в реальном времени.
  * -e: перейти в конец журнала, чтобы показать последние события.
  * -r: вывести сообщения логов в обратном хронологическом порядке.
  * -k: показать только сообщения ядра.
  * -u: показать только сообщения для указанного модуля systemd.
  * -b: показать сообщения о конкретной загрузке и отображает текущие загрузочные сообщения, если определенные загрузочные сеансы не включены.
  * –List-boots: показывает сеансы загрузки в таблице, включая их идентификаторы и временные метки первого и последнего сообщения, относящегося к загрузке.
  * –Utc: выразить время в формате всемирного координированного времени (UTC).
  * -p, –priority =: фильтровать вывод по приоритетам сообщений.
  * -S, –since =: фильтровать журналы по времени начала.
  * -U, –until =: фильтровать журналы по времени окончания.
  * –Disk-usage: показывает текущее использование диска всеми файлами логов.

### 3) Как использовать journalctl для чтения логов

Вы можете фильтровать логи в соответствии с вашими потребностями с помощью различных параметров и полей.

Мы покажем вам, как их использовать.

### Просмотр основного журнала с помощью команды journalctl

Когда вы запускаете команду journalctl без флагов, она показывает все содержимое логов, причем самые старые записи отображаются первыми.

Команда использует команду «less» на бэкенде, чтобы показать вам логи.

Следовательно, вы можете использовать те же клавиши для перемещения по журналам, которые вы используете с командой «less».

```bash
$ sudo journalctl
```

Представление логов по умолчанию может быть легко прочитано, но если вам нужен более подробный вывод, запустите:

```bash
$ sudo journalctl -o verbose
```

### Отображение логов в обратном порядке

Как вы заметили, в приведенном выше выводе логи показаны в хронологическом порядке.

Чтобы сначала отобразить последние логи, запустите команду journalctl с параметром «-r».

```bash
$ sudo journalctl **-r**

-- Logs begin at Sat 2021-03-13 15:51:12 IST, end at Thu 2021-03-18 01:56:20 IST. --
Mar 18 01:56:20 itsecforu sudo[23711]: pam_unix(sudo:session): session opened for user root by (uid=1000)
Mar 18 01:56:20 itsecforu sudo[23711]: linuxgeek : TTY=pts/0 ; PWD=/home/linuxgeek ; USER=root ; COMMAND=/usr/bin/journalctl -r
Mar 18 01:56:20 itsecforu sudo[23711]: gkr-pam: unable to locate daemon control file
Mar 18 01:55:11 itsecforusystemd[1]: Started Network Manager Script Dispatcher Service.
Mar 18 01:55:11 itsecforu dbus-daemon[1190]: [system] Successfully activated service 'org.freedesktop.nm_dispatcher'
Mar 18 01:55:11 itsecforu systemd[1]: Starting Network Manager Script Dispatcher Service…
Mar 18 01:55:11 itsecforu NetworkManager[1487]:   [1616012711.5640] dhcp4 (wlan0): state changed bound -> extended
Mar 18 01:55:11 itsecforu NetworkManager[1487]:   [1616012711.5639] dhcp4 (wlan0): option subnet_mask          => '255.255.255.0'
Mar 18 01:55:11 itsecforu NetworkManager[1487]:   [1616012711.5639] dhcp4 (wlan0): option routers              => '192.168.1.1'
....
```

### Отображение только “N” последних строк

Вы можете отобразить только определенное количество последних строк из журнала логов, используя параметр ‘-n’ вместо всего журнала, как показано ниже:

```text
 sudo journalctl -n 20
-- Logs begin at Fri 2021-02-12 14:26:01 +0630, end at Fri 2021-03-19 13:24:41 +0630. --
Mar 19 12:01:01 DevSexOps run-parts(/etc/cron.hourly)[27459]: finished 0anacron
Mar 19 12:01:01 DevSexOps systemd[1]: Removed slice User Slice of root.
Mar 19 13:00:01 DevSexOps systemd[1]: Starting Docker Cleanup...
Mar 19 13:00:01 DevSexOps systemd[1]: Started Docker Cleanup.
Mar 19 13:01:01 DevSexOps systemd[1]: Created slice User Slice of root.
Mar 19 13:01:01 DevSexOps systemd[1]: Started Session 881 of user root.
Mar 19 13:01:01 DevSexOps CROND[30364]: (root) CMD (run-parts /etc/cron.hourly)
Mar 19 13:01:01 DevSexOps run-parts(/etc/cron.hourly)[30367]: starting 0anacron
Mar 19 13:01:01 DevSexOps run-parts(/etc/cron.hourly)[30373]: finished 0anacron
Mar 19 13:01:01 DevSexOps systemd[1]: Removed slice User Slice of root.
Mar 19 13:05:46 DevSexOps sshd[30600]: Accepted password for root from 10.2.67.11 port 64283 ssh2
Mar 19 13:05:46 DevSexOps systemd[1]: Created slice User Slice of root.
Mar 19 13:05:46 DevSexOps systemd-logind[752]: New session 882 of user root.
Mar 19 13:05:46 DevSexOps systemd[1]: Started Session 882 of user root.
Mar 19 13:05:46 DevSexOps sshd[30600]: pam_unix(sshd:session): session opened for user root by (uid=0)
Mar 19 13:05:56 DevSexOps sudo[30634]: root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/journalctl
Mar 19 13:05:56 DevSexOps sudo[30634]: pam_unix(sudo:session): session opened for user root by root(uid=0)
Mar 19 13:24:39 DevSexOps sudo[30634]: pam_unix(sudo:session): session closed for user root
Mar 19 13:24:41 DevSexOps sudo[31542]: root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/journalctl -n 20
Mar 19 13:24:41 DevSexOps sudo[31542]: pam_unix(sudo:session): session opened for user root by root(uid=0)
```

### Проверка логов в реальном времени

Логи в реальном времени можно просмотреть с помощью опции «-f», используя команду «journalctl», как показано ниже.

Это может быть полезно при устранении неполадок.

```bash
$ sudo journalctl **-f**
```

### Фильтрация определенного лога загрузки

```text
journalctl --list-boots
0 7ff1965b851448b3996046d8cefa4805 Fri 2021-02-12 14:26:01 +0630—Fri 2021-03-19 13:24:41 +0630
```

Журналы загрузки имеют префикс, начинающийся с нуля. «0» относится к текущей загрузке.

Сеанс загрузки «-1» – это последний загруженный сеанс и так далее.

Чтобы просмотреть сообщения из конкретной загрузки, выполните следующую команду.

Покажем все сообщения из текущей загрузки:

```text
sudo journalctl -b
-- Logs begin at Fri 2021-02-12 14:26:01 +0630, end at Fri 2021-03-19 13:29:11 +0630. --
Feb 12 14:26:01 DevSexOps systemd-journal[97]: Runtime journal is using 8.0M (max allowed 189.4M, trying to leave 284.2M free of 1.8G available
Feb 12 14:26:01 DevSexOps kernel: Initializing cgroup subsys cpuset
Feb 12 14:26:01 DevSexOps kernel: Initializing cgroup subsys cpu
Feb 12 14:26:01 DevSexOps kernel: Initializing cgroup subsys cpuacct
Feb 12 14:26:01 DevSexOps kernel: Linux version 3.10.0-1160.15.2.el7.x86_64 (mockbuild@kbuilder.bsys.centos.org) (gcc version 4.8.5 20150623 (Re
Feb 12 14:26:01 DevSexOps kernel: Command line: BOOT_IMAGE=/vmlinuz-3.10.0-1160.15.2.el7.x86_64 root=/dev/mapper/centos-root ro crashkernel=auto
Feb 12 14:26:01 DevSexOps kernel: Disabled fast string operations
Feb 12 14:26:01 DevSexOps kernel: e820: BIOS-provided physical RAM map:
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x0000000000000000-0x000000000009f3ff] usable
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x000000000009f400-0x000000000009ffff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000000dc000-0x00000000000fffff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x0000000000100000-0x00000000bfedffff] usable
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000bfee0000-0x00000000bfefefff] ACPI data
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000bfeff000-0x00000000bfefffff] ACPI NVS
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000bff00000-0x00000000bfffffff] usable
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000f0000000-0x00000000f7ffffff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000fec00000-0x00000000fec0ffff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000fee00000-0x00000000fee00fff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x00000000fffe0000-0x00000000ffffffff] reserved
Feb 12 14:26:01 DevSexOps kernel: BIOS-e820: [mem 0x0000000100000000-0x000000013fffffff] usable
Feb 12 14:26:01 DevSexOps kernel: NX (Execute Disable) protection: active
Feb 12 14:26:01 DevSexOps kernel: SMBIOS 2.7 present.
Feb 12 14:26:01 DevSexOps kernel: DMI: VMware, Inc. VMware Virtual Platform/440BX Desktop Reference Platform, BIOS 6.00 12/12/2018
Feb 12 14:26:01 DevSexOps kernel: Hypervisor detected: VMware
Feb 12 14:26:01 DevSexOps kernel: vmware: TSC freq read from hypervisor : 2194.843 MHz
Feb 12 14:26:01 DevSexOps kernel: vmware: Host bus clock speed read from hypervisor : 66000000 Hz
Feb 12 14:26:01 DevSexOps kernel: vmware: using sched offset of 7157487822 ns
Feb 12 14:26:01 DevSexOps kernel: e820: update [mem 0x00000000-0x00000fff] usable ==> reserved
Feb 12 14:26:01 DevSexOps kernel: e820: remove [mem 0x000a0000-0x000fffff] usable
Feb 12 14:26:01 DevSexOps kernel: e820: last_pfn = 0x140000 max_arch_pfn = 0x400000000
Feb 12 14:26:01 DevSexOps kernel: MTRR default type: uncachable
Feb 12 14:26:01 DevSexOps kernel: MTRR fixed ranges enabled:
Feb 12 14:26:01 DevSexOps kernel: 00000-9FFFF write-back
Feb 12 14:26:01 DevSexOps kernel: A0000-BFFFF uncachable
Feb 12 14:26:01 DevSexOps kernel: C0000-CFFFF write-protect
Feb 12 14:26:01 DevSexOps kernel: D0000-EFFFF uncachable
Feb 12 14:26:01 DevSexOps kernel: F0000-FFFFF write-protect
Feb 12 14:26:01 DevSexOps kernel: MTRR variable ranges enabled:
```

Чтобы проверить вывод сообщений предыдущего сеанса загрузки, выполните следующую команду:

### Фильтрация на основе временного интервала

Журналы журнала можно фильтровать по временному интервалу.

С фильтром времени можно использовать несколько аргументов, как показано ниже.

Чтобы использовать фильтр времени, используйте ключи командной строки ‘-S или –since’ и ‘-U или –until’.

Чтобы отфильтровать журналы со вчерашнего дня, выполните следующую команду:

```bash
$ sudo journalctl **-S yesterday**
```

Чтобы отфильтровать только сегодняшние логи, выполните следующую команду (мы можем использовать либо **`'today'`** , либо **`'00:00'`** , и оба они одинаковы):

```bash
$ sudo journalctl -S today
или
$ sudo journalctl -S 00:00
```

Чтобы отфильтровать журналы только за вчерашний день, выполните следующую команду:

```bash
$ sudo journalctl --since yesterday --until 00:00
```

Чтобы отфильтровать журналы с 12 марта, выполните следующую команду:

```bash
$ sudo journalctl **--since "2021-03-11 20:10:00" --until "2021-03-15"**
```

Чтобы отфильтровать сообщения за последний час, используйте следующую команду:

```bash
$ sudo journalctl **-S -1h**
```

### Фильтрация по приоритету

Фильтрация может применяться к приоритету сообщения, что может быть полезно, если вы хотите отфильтровать конкретное сообщение, такое как **“warning”** или **“error”** и т.д.

В таблице ниже перечислены все уровни приоритета

![Journalctl — анализ логов Linux, изображение №3](/images/67333d3ebac172c117ea254d1adb13f5.png)

```bash
$ sudo journalctl -p 3 -b
или
$ sudo journalctl -p err -b

Feb 12 14:26:02 DevSexOps kernel: sd 2:0:0:0: [sda] Assuming drive cache: write through
Feb 12 14:26:04 DevSexOps kernel: piix4_smbus 0000:00:07.3: SMBus Host Controller not enabled!
Feb 15 13:39:25 DevSexOps sudo[11546]: pam_unix(sudo-i:auth): conversation failed
Feb 15 13:39:25 DevSexOps sudo[11546]: pam_unix(sudo-i:auth): auth could not identify password for [user]
Feb 15 13:39:27 DevSexOps sudo[11546]: user : user NOT in sudoers ; TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash
Feb 15 13:46:54 DevSexOps sudo[11586]: pam_unix(sudo-i:auth): conversation failed
Feb 15 13:46:54 DevSexOps sudo[11586]: pam_unix(sudo-i:auth): auth could not identify password for [user]
Feb 15 13:46:56 DevSexOps sudo[11591]: pam_unix(sudo:auth): conversation failed
Feb 15 13:46:56 DevSexOps sudo[11591]: pam_unix(sudo:auth): auth could not identify password for [user]
Feb 15 13:46:56 DevSexOps sudo[11586]: user : user NOT in sudoers ; TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash
Feb 15 13:46:59 DevSexOps sudo[11589]: pam_unix(sudo-i:auth): conversation failed
Feb 15 13:46:59 DevSexOps sudo[11589]: pam_unix(sudo-i:auth): auth could not identify password for [user]
Feb 15 13:46:59 DevSexOps sudo[11591]: user : user NOT in sudoers ; TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/sh -c toilet -f bubble
Feb 15 13:47:01 DevSexOps sudo[11589]: user : user NOT in sudoers ; TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash
Feb 15 14:17:19 DevSexOps sudo[11936]: pam_unix(sudo-i:auth): conversation failed
Feb 15 14:17:19 DevSexOps sudo[11936]: pam_unix(sudo-i:auth): auth could not identify password for [user]
Feb 15 14:17:21 DevSexOps sudo[11938]: pam_unix(sudo:auth): conversation failed
Feb 15 14:17:21 DevSexOps sudo[11938]: pam_unix(sudo:auth): auth could not identify password for [user]
....
```

### 4) Фильтрация по полям

Логи можно фильтровать по определенным полям.

Синтаксис поля для сопоставления – «FIELD_NAME = MATCHED_VALUE», например «SYSTEMD_UNIT = httpd.service».

Кроме того, вы можете указать несколько совпадений в одном запросе для более удобной фильтрации.

### Фильтрация по системному юниту

Чтобы показать логи, созданные указанной службой, используйте приведенные ниже команды.

Аналогичным образом вы можете фильтровать любые служебные сообщения.

Чтобы проверить доступные журналы служб, введите «journalctl -u» и дважды нажмите клавишу TAB.

```bash
$ sudo journalctl -u httpd.service
или
$ sudo journalctl _SYSTEMD_UNIT=httpd.service
```

### Фильтрация логов по UID, GID и PID

Чтобы показать логи, созданные определенным идентификатором процесса, выполните следующую команду:

```bash
$ sudo journalctl _PID=1039
```

Чтобы показать логи, созданные определенным идентификатором пользователя, выполните следующую команду:

```bash
$ sudo journalctl _UID=1021
```

Чтобы показать логи, созданные определенным идентификатором группы, выполните следующую команду:

```bash
$ sudo journalctl _GID=1050
```

Фильтр можно применять одновременно к нескольким полям, но он будет отображать только записи, соответствующие обоим выражениям:

```bash
$ sudo journalctl _SYSTEMD_UNIT=httpd.service _PID=1500
```

Логические выражения можно использовать с командой «journalctl», как показано ниже.

В следующем примере показаны все сообщения от процесса службы Apache и все сообщения от службы MySQL:

```bash
$ sudo journalctl _SYSTEMD_UNIT=httpd-daemon.service + _SYSTEMD_UNIT=mysqld.service
```

### Фильтр по пути к файлу

```bash
$ sudo journalctl /usr/bin/gnome-shell
```

### Фильтр по пути к устройству

Чтобы отфильтровать логи, относящееся к определенному устройству, выполните следующую команду:

```bash
$ sudo journalctl **/dev/sda**

-- Logs begin at Sat 2021-03-13 15:51:12 IST, end at Thu 2021-03-18 02:10:09 IST. --
Mar 17 13:54:17 2daygeek kernel: pci 0000:00:17.0: [8086:a103] type 00 class 0x010601
Mar 17 13:54:17 2daygeek kernel: pci 0000:00:17.0: reg 0x10: [mem 0x94428000-0x94429fff]
Mar 17 13:54:17 2daygeek kernel: pci 0000:00:17.0: reg 0x14: [mem 0x9442d000-0x9442d0ff]
Mar 17 13:54:17 2daygeek kernel: ahci 0000:00:17.0: version 3.0
Mar 17 13:54:17 2daygeek kernel: scsi 2:0:0:0: Direct-Access     ATA      WDC WD10SPCX-24H 1A02 PQ: 0 ANSI: 5
Mar 17 13:54:17 2daygeek kernel: sd 2:0:0:0: [sda] 1953525168 512-byte logical blocks: (1.00 TB/932 GiB)
....
```

### Проверка использования диска

Когда вы включаете постоянное хранилище логов, оно использует до «10%» файловой системы, в которой находится «/var/log/journal».

Чтобы узнать, сколько места для хранения используют файлы журнала, выполните следующую команду:

```bash
$ sudo journalctl --disk-usage

Archived and active journals take up 40.0M in the file system.
```

### Заключение

В этом руководстве мы показали вам, что такое journal и как использовать команду journalctl для фильтрации логов на основе различных параметров.

[Источник](/away.php?to=https%3A%2F%2Fitsecforu.ru%2F2021%2F03%2F19%2F%26%23128039%3B-%EA%E0%EA-%E8%F1%EF%EE%EB%FC%E7%EE%E2%E0%F2%FC-journalctl-%E4%EB%FF-%E0%ED%E0%EB%E8%E7%E0-%EB%EE%E3%2F&cc_key= "https://itsecforu.ru/2021/03/19/&#128039;-как-использовать-journalctl-для-анализа-лог/")

171 просмотр

**********

[systemd](/tags/systemd.md)
[journald](/tags/journald.md)
