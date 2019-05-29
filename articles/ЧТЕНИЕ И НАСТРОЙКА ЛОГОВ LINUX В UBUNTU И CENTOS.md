# ЧТЕНИЕ И НАСТРОЙКА ЛОГОВ LINUX В UBUNTU И CENTOS

Администраторам Linux часто нужно заглядывать в лог-файл для устранения неполадок. По сути, это действие первой необходимости для любого админа.

Система Linux и ее приложения могут создавать разные типы сообщений, которые записываются в различные журналы. Linux использует набор конфигурационных файлов, каталогов, программ, команд и демонов для создания, хранения и повторного использования таких сообщений. Поэтому зная, где система хранит свои журналы и как воспользоваться определенными командами, можно сэкономить драгоценное время во время устранения неполадок.

Данное руководство рассматривает различные части механизма журналирования Linux.

**Примечание**: Команды данного руководства были протестированы на простых установках CentOS 6.4, Ubuntu 12 и Debian 7.

## Стандартные логи

По умолчанию журналы в Linux хранятся в  /var/log.

Для просмотра списка журналов, находящихся в данном каталоге, используйте команду ls -l /var/log.

В системе CentOS это выглядит так:

`[root@TestLinux ~]# ls -l /var/log  
total 1472  
-rw-------. 1 root root   4524 Nov 15 16:04 anaconda.ifcfg.log  
-rw-------. 1 root root  59041 Nov 15 16:04 anaconda.log  
-rw-------. 1 root root  42763 Nov 15 16:04 anaconda.program.log  
-rw-------. 1 root root 299910 Nov 15 16:04 anaconda.storage.log  
-rw-------. 1 root root  40669 Nov 15 16:04 anaconda.syslog  
-rw-------. 1 root root  57061 Nov 15 16:04 anaconda.xlog  
-rw-------. 1 root root   1829 Nov 15 16:04 anaconda.yum.log  
drwxr-x---. 2 root root   4096 Nov 15 16:11 audit  
-rw-r--r--  1 root root   2252 Dec  9 10:27 boot.log  
-rw-------  1 root utmp    384 Dec  9 10:31 btmp  
-rw-------. 1 root utmp   1920 Nov 28 09:28 btmp-20131202  
drwxr-xr-x  2 root root   4096 Nov 29 15:47 ConsoleKit  
-rw-------  1 root root   2288 Dec  9 11:01 cron  
-rw-------. 1 root root   8809 Dec  2 17:09 cron-20131202  
-rw-r--r--  1 root root  21510 Dec  9 10:27 dmesg  
-rw-r--r--  1 root root  21351 Dec  6 16:37 dmesg.old  
-rw-r--r--. 1 root root 165665 Nov 15 16:04 dracut.log  
-rw-r--r--. 1 root root 146876 Dec  9 10:44 lastlog  
-rw-------  1 root root    950 Dec  9 10:27 maillog  
-rw-------. 1 root root   4609 Dec  2 17:00 maillog-20131202  
-rw-------  1 root root 123174 Dec  9 10:27 messages  
-rw-------. 1 root root 458481 Dec  2 17:00 messages-20131202  
-rw-------  1 root root   2644 Dec  9 10:44 secure  
-rw-------. 1 root root  15984 Dec  2 17:00 secure-20131202  
-rw-------  1 root root      0 Dec  2 17:09 spooler  
-rw-------. 1 root root      0 Nov 15 16:02 spooler-20131202  
-rw-------. 1 root root      0 Nov 15 16:02 tallylog  
-rw-rw-r--. 1 root utmp  89856 Dec  9 10:44 wtmp  
-rw-------  1 root root   3778 Dec  6 16:48 yum.log`

## Просмотр логов

В каталоге /var/log находится несколько общих журналов:

*   wtmp
*   utmp
*   dmesg
*   messages
*   maillog или mail.log
*   spooler
*   auth.log или secure

Файлы wtmp и utmp отслеживают пользователей, вошедших и покинувших систему. Содержимое данных журналов нельзя читать с помощью простой команды «cat», для этого есть специальные команды, с которыми теперь нужно ознакомиться.

Чтобы узнать, кто в текущий момент находится на сервере Linux, нужно использовать команду «who». Она извлекает информацию из /var/run/utmp (в CentOS и Debian) или из /run/utmp (в Ubuntu).

Это пример ее работы в CentOS:

`[root@TestLinux ~]# who  
root     tty1         2013-12-09 10:44  
root      pts/0        2013-12-09 10:29 (10.0.2.2)  
sysadmin pts/1        2013-12-09 10:31 (10.0.2.2)  
joeblog  pts/2        2013-12-09 10:39 (10.0.2.2)`

Команда «sysadmin» выводит историю входа пользователей:

`[root@TestLinux ~]# last | grep sysadmin  
sysadmin pts/1        10.0.2.2         Mon Dec  9 10:31   still logged in  
sysadmin pts/0        10.0.2.2         Fri Nov 29 15:42 - crash  (00:01)  
sysadmin pts/0        10.0.2.2         Thu Nov 28 17:06 - 17:13  (00:06)  
sysadmin pts/0        10.0.2.2         Thu Nov 28 16:17 - 17:05  (00:48)  
sysadmin pts/0        10.0.2.2         Thu Nov 28 09:29 - crash  (06:04)  
sysadmin pts/0        10.0.2.2         Wed Nov 27 16:37 - down   (00:29)  
sysadmin tty1                          Wed Nov 27 14:05 - down   (00:36)  
sysadmin tty1                          Wed Nov 27 13:49 - 14:04  (00:15)`

В данном примере нужно было получить историю входа пользователя sysadmin. Как можно видеть,  было пару случаев, когда он приводил к сбою системы.

Чтобы узнать время последней перезагрузки системы, используйте следующую команду:

`[root@TestLinux ~]# last reboot`

Результат имеет примерно такой вид:

`reboot   system boot  2.6.32-358.el6.x Mon Dec  9 10:27 - 10:47  (00:19)  
reboot   system boot  2.6.32-358.el6.x Fri Dec  6 16:37 - 10:47 (2+18:10)  
reboot   system boot  2.6.32-358.el6.x Fri Dec  6 16:28 - 16:36  (00:08)    reboot   system boot  2.6.32-358.el6.x Fri Dec  6 11:06 - 16:36  (05:29)  
reboot   system boot  2.6.32-358.el6.x Mon Dec  2 17:00 - 16:36 (3+23:36)  
reboot   system boot  2.6.32-358.el6.x Fri Nov 29 16:01 - 16:36 (7+00:34)  
reboot   system boot  2.6.32-358.el6.x Fri Nov 29 15:43 - 16:36 (7+00:53)  
...  
...  
wtmp begins Fri Nov 15 16:11:54 2013`

Чтобы узнать время последнего входа в систему, используйте lastlog:

`[root@TestLinux ~]# lastlog`

Результат на CentOS выглядит примерно так:

`Username        Port        From            Latest  
root            tty1                        Mon Dec  9 10:44:30 +1100 2013  
bin                                        **Never logged in**  
daemon                                     **Never logged in**  
adm                                        **Never logged in**  
lp                                         **Never logged in**  
sync                                       **Never logged in**  
shutdown                                   **Never logged in**  
halt                                       **Never logged in**  
mail                                       **Never logged in**  
uucp                                       **Never logged in**  
operator                                   **Never logged in**  
games                                      **Never logged in**  
gopher                                     **Never logged in**  
ftp                                        **Never logged in**  
nobody                                     **Never logged in**  
vcsa                                       **Never logged in**  
saslauth                                   **Never logged in**  
postfix                                    **Never logged in**  
sshd                                       **Never logged in**  
sysadmin         pts/1    10.0.2.2         Mon Dec  9 10:31:50 +1100 2013  
dbus                                       **Never logged in**  
joeblog          pts/2    10.0.2.2         Mon Dec  9 10:39:24 +1100 2013`

Для просмотра содержимого текстовых журналов можно использовать команды «cat», «head» или «tail».

В приведенном ниже примере просматриваются последние 10 строк журнала /var/log/messages на Debian:

`debian@debian:~$ sudo tail /var/log/messages`

Вывод:

`Dec 16 01:21:08 debian kernel: [    9.584074] Bluetooth: BNEP (Ethernet Emulation) ver 1.3  
Dec 16 01:21:08 debian kernel: [    9.584074] Bluetooth: BNEP filters: protocol multicast  
Dec 16 01:21:08 debian kernel: [    9.648220] Bridge firewalling registered  
Dec 16 01:21:08 debian kernel: [    9.696728] Bluetooth: SCO (Voice Link) ver 0.6  
Dec 16 01:21:08 debian kernel: [    9.696728] Bluetooth: SCO socket layer initialized  
Dec 16 01:21:08 debian kernel: [    9.832215] lp: driver loaded but no devices found  
Dec 16 01:21:08 debian kernel: [    9.868897] ppdev: user-space parallel port driver  
Dec 16 01:21:11 debian kernel: [   12.748833] [drm] Initialized drm 1.1.0 20060810  
Dec 16 01:21:11 debian kernel: [   12.754412] pci 0000:00:02.0: PCI INT A -> Link[LNKB] -> GSI 11 (level, low) -> IRQ 11  
Dec 16 01:21:11 debian kernel: [   12.754412] [drm] Initialized vboxvideo 1.0.0 20090303 for 0000:00:02.0 on minor 0`

## Демон rsyslog

Центром механизма журналирования является демон rsyslog. Данный сервис отвечает за прослушивание зарегистрированных сообщений различных частей системы Linux и маршрутизацию сообщения к соответствующему журналу в каталоге /var/log. Он также может передавать зарегистрированные сообщения другому серверу Linux.

### Конфигурационный файл rsyslog

Демон rsyslog получает конфигурации из файла «rsyslog.conf», который находится в каталоге /etc.

В основном, файл rsyslog.conf говорит демону, где хранить сообщения. Данная информация имеет вид серии строк, состоящих из двух частей.

Этот файл можно найти в rsyslog.d/50-default.conf в Ubuntu.

Под двумя частями строк подразумеваются селектор и действие (selector и action). Они разделяются пробельным символом.

Селектор указывает на  источник и важность сообщения, а действие говорит, что нужно сделать с данным сообщением.

Сам селектор также разделен на 2 части символом точки (.). Часть перед символом точки называется объектом (источник сообщения), а часть за символом называется приоритетом (степень важности сообщения).

Комбинация объекта-приоритета и действия говорит rsyslog, что делать, если сообщение соответствует указанным параметрам.

Вот отрывок из файла rsyslog.conf на CentOS:

`# rsyslog v5 configuration file  
...  
...  
# Include all config files in /etc/rsyslog.d/  
IncludeConfig /etc/rsyslog.d/*.conf  
#### RULES ####  
# Log all kernel messages to the console.  
# Logging much else clutters up the screen.  
#kern.*  /dev/console  
# Log anything (except mail) of level info or higher.  
# Don't log private authentication messages!  
*.info;mail.none;authpriv.none;cron.none                /var/log/messages  
# The authpriv file has restricted access.  
authpriv.*                                              /var/log/secure  
# Log all the mail messages in one place.  
mail.*                                                  -/var/log/maillog  
# Log cron stuff  
cron.*                                                  /var/log/cron  
# Everybody gets emergency messages  
*.emerg                                                 *  
# Save news errors of level crit and higher in a special file.  
uucp,news.crit                                          /var/log/spooler  
# Save boot messages also to boot.log  
local7.*                                                /var/log/boot.log  
...  
...`

Чтобы понять, что все это значит, нужно рассмотреть типы объектов, которые распознает Linux:

*   auth or authpriv: Сообщения, поступающие от сервисов авторизации и безопасности;
*   kern: сообщения ядра Linux;
*   mail: сообщения подсистемы почты;
*   cron: сообщения демона Cron;
*   daemon: сообщения от демонов;
*   news: сообщения подсистемы новостей сети;
*   lpr: сообщения, связанные с печатью;
*   user: сообщения пользовательских программ;
*   local0 до local7:Зарезервировано для локального использования.

Ниже приведен список приоритетов по возрастанию:

*   Debug: Отладочная информация от программ;
*   info: простое информационное сообщение – никакого вмешательства не требуется;
*   notice: состояние, которое может потребовать внимания;
*   warn: Предупреждение;
*   err: ошибка;
*   crit: критическое состояние;
*   alert: состояние, требующее немедленного вмешательства;
*   emerg: аварийное состояние.

Изучите следующую строку из файла:

`cron.*              /var/log/cron`

Она говорит rsyslog сохранять все сообщения, приходящие от демона cron, в файле /var/log/cron. Звездочка (\*) поле точки значит, что зарегистрированы будут сообщения всех приоритетов. Аналогичным образом, если объект был определен звездочкой, это объединяет все источники.

Объекты и приоритеты могут быть связаны в несколькими способами.

Вид по умолчанию, когда после точки указан только один приоритет, значит, что будут охвачены все сообщения с таким или высшим уровнем приоритета. Таким образом, данное указание регистрирует все сообщения, приходящие от почтовой подсистемы с приоритетом «warn» и выше в специальном файле в /var/log:

`mail.warn           /var/log/mail.warn`

Такие параметры будут регистрировать все сообщения с таким же или высшим, чем warn, приоритетом и пропускать все остальное. То есть, сообщения с приоритетом err, crit, alert и emerg также будут внесены в файл.

Знак равности (=) после точки указывает регистрировать только сообщения с указанным приоритетом. То есть, если нужно регистрировать только сообщения от почтовой подсистемы с приоритетом info, указание будет таким:

`mail.=info          /var/log/mail.info`

Опять же, если нужно регистрировать все сообщения почтовой подсистемы, кроме сообщений с приоритетом  info, строка будет выглядеть так:

`mail.!info          /var/log/mail.info`

или так:

`mail.!=info         /var/log/mail.info`

В первом случае файл mail.info содержал бы все сообщения с приоритетом ниже info. Во втором случае он содержал бы все сообщения с приоритетом выше info.

Несколько объектов в одной строке нужно разделить запятой.

Несколько селекторов в одной строке также разделяются запятой.

Отмеченное звездочкой действие объединяет всех пользователей.

К примеру, об этом говорит запись в файле rsyslog.conf на CentOS:

`# Everybody gets emergency messages  
*.emerg                                                 *`

По возможности проверьте, что говорит rsyslog.conf на других системах Linux. Вот отрывок из Debian:

`#  /etc/rsyslog.conf    Configuration file for rsyslog.  
#  
#           For more information see  
#           /usr/share/doc/rsyslog-doc/html/rsyslog_conf.html  
...  
...  
auth,authpriv.*         /var/log/auth.log  
*.*;auth,authpriv.none      -/var/log/syslog  
#cron.*             /var/log/cron.log  
daemon.*            -/var/log/daemon.log  
kern.*              -/var/log/kern.log  
lpr.*               -/var/log/lpr.log  
mail.*              -/var/log/mail.log  
user.*              -/var/log/user.log  
#  
# Logging for the mail system.  Split it up so that  
# it is easy to write scripts to parse these files.  
#  
mail.info           -/var/log/mail.info  
mail.warn           -/var/log/mail.warn  
mail.err            /var/log/mail.err  
#  
# Logging for INN news system.  
#  
news.crit           /var/log/news/news.crit  
news.err            /var/log/news/news.err  
news.notice         -/var/log/news/news.notice`

Как можно видеть, Debian сохраняет сообщения безопасности/авторизации всех уровней в /var/log/auth.log, в то время как CentOS делает это в /var/log/secure.

Конфигурации для rsyslog могут исходить также от других пользовательских файлов. Эти файлы пользовательских конфигураций, как правило, расположены в разных каталогах в /etc/rsyslog.d. Файл rsyslog.conf включает эти каталоги, используя директиву «$IncludeConfig».

Так это выглядит в Ubuntu:

`#  Default logging rules can be found in /etc/rsyslog.d/50-default.conf  
....  
....  
$IncludeConfig /etc/rsyslog.d/*.conf  
Содержимое каталога /etc/rsyslog.d выглядит так:  
-rw-r--r-- 1 root root  311 Mar 17  2012 20-ufw.conf  
-rw-r--r-- 1 root root  252 Apr 11  2012 21-cloudinit.conf  
-rw-r--r-- 1 root root 1655 Mar 30  2012 50-default.conf`

Теперь сохранять сообщение в журнал необязательно; сообщение можно переслать консоли пользователя. В таком случае, поле действия будет содержать имя пользователя. Если сообщение нужно отправить нескольким пользователям, их имена нужно разделить запятыми. Если же сообщение нужно распространить между всеми пользователями, в поле действия вносится символ \*.

Будучи частью сетевой операционной системы, демон rsyslog может не только хранить зарегистрированные сообщения локально, но и передавать их на другие серверы Linux, а также действовать как репозиторий для других систем. Демон прослушивает сообщения через UDP-порт 514. В приведенном ниже примере он пересылает критические сообщения ядра на сервер под названием «texas»:

`kern.crit           @texas`

## Создание и тестирование сообщений

Теперь попробуйте сами создать сообщение.

Для этого нужно будет сделать следующее:

*   Задать спецификацию в файле /etc/rsyslog.conf;
*   Перезапустить демон rsyslog;
*   Проверить конфигурацию с помощью утилиты «logger».

В следующем примере внесены две строки в файл rsyslog.conf на CentOS. Как видите, обе они исходят от объекта local4 и имеют разные приоритеты.

`[root@TestLinux ~]# vi /etc/rsyslog.conf  
....  
....  
# New lines added for testing log message generation  
local4.crit                                             /var/log/local4crit.log  
local4.=info                                            /var/log/local4info.log`

Затем нужно перезапустить сервис, чтобы обновить данные файла:

`[root@TestLinux ~]# /etc/init.d/rsyslog restart  
Shutting down system logger:                               [  OK  ]  
Starting system logger:                                    [  OK  ]  
[root@TestLinux ~]#`

Теперь нужно вызвать приложение logger, чтобы создать сообщение:

`[root@TestLinux ~]# logger -p local4.info " This is a info message from local 4"`

Каталог /var/log показывает два новых сообщения:

`...  
...  
-rw-------  1 root root      0 Dec  9 11:21 local4crit.log  
-rw-------  1 root root     72 Dec  9 11:22 local4info.log`

Размер local4info.log не равен нулю, а это значит, что сообщение было записано:

`[root@TestLinux ~]# cat /var/log/local4info.log  
Dec  9 11:22:32 TestLinux root:  This is a info message from local 4`

## Ротация  лог-файлов

Со временем журналы становятся больше, поскольку в них появляется новая информация. Это создает потенциальную проблему производительности. Кроме того, управление файлами становится затруднительным.

Linux использует понятие «ротации» журналов вместо их очистки или удаления. При ротации создается новый каталог, а старый переименуется и при необходимости сжимается. Таким образом, журналы имеют несколько старых версий. Эти файлы будут возвращаться в течение определенного периода времени в виде так называемых backlog-ов. Как только будет получено определенное количество backlog-ов, новая ротация удалит самый старый журнал.

Ротация выполняется при помощи утилиты «logrotate».

### Конфигурационный файл logrotate

Как и rsyslog, logrotate зависит от конфигурационного файла по имени logrotate.conf, который находится в /etc.

Вот что находится в данном файле на Debian:

`debian@debian:~$ cat /etc/logrotate.conf  
# see "man logrotate" for details  
# rotate log files weekly  
weekly  
# keep 4 weeks worth of backlogs  
rotate 4  
# create new (empty) log files after rotating old ones  
create  
# uncomment this if you want your log files compressed  
#compress  
# packages drop log rotation information into this directory  
include /etc/logrotate.d  
# no packages own wtmp, or btmp -- we'll rotate them here  
/var/log/wtmp {  
missingok  
monthly  
create 0664 root utmp  
rotate 1  
}  
/var/log/btmp {  
missingok  
monthly  
create 0660 root utmp  
rotate 1  
}  
# system-specific logs may be configured here`

По умолчанию журналы ротируются еженедельно, оставляя 4 backlog-а. При запуске программы создается новый пустой журнал, а старые при необходимости будут сжаты.

Файлы wtmp и btmp являются исключениями. wtmp отслеживает вход в систему, а btmp содержит информацию о неудавшихся попытках входа. Эти журнальные файлы ротируются каждый месяц, и ошибки не возвращаются, если можно найти один из предыдущих файлов wtmp или btmp.

Пользовательские конфигурации ротации журналов содержатся в каталоге «etc/logrotate.d». также они включены в logrotate.conf с помощью директивы include. К примеру, Debian показывает такое содержание данного каталога:

`debian@debian:~$ ls -l /etc/logrotate.d  
total 44  
-rw-r--r-- 1 root root 173 Apr 15  2011 apt  
-rw-r--r-- 1 root root  79 Aug 12  2011 aptitude  
-rw-r--r-- 1 root root 135 Feb 24  2010 consolekit  
-rw-r--r-- 1 root root 248 Nov 28  2011 cups  
-rw-r--r-- 1 root root 232 Sep 19  2012 dpkg  
-rw-r--r-- 1 root root 146 May 12  2011 exim4-base  
-rw-r--r-- 1 root root 126 May 12  2011 exim4-paniclog  
-rw-r--r-- 1 root root 157 Nov 16  2010 pm-utils  
-rw-r--r-- 1 root root  94 Aug  8  2010 ppp  
-rw-r--r-- 1 root root 515 Nov 30  2010 rsyslog  
-rw-r--r-- 1 root root 114 Nov 26  2008 unattended-upgrades`

Содержание rsyslog показывает, как вернуть логи в исходное состояние:

`debian@debian:~$ cat /etc/logrotate.d/rsyslog  
/var/log/syslog  
{  
rotate 7  
daily  
missingok  
notifempty  
delaycompress  
compress  
postrotate  
invoke-rc.d rsyslog reload > /dev/null  
endscript  
}  
/var/log/mail.info  
/var/log/mail.warn  
/var/log/mail.err  
/var/log/mail.log  
/var/log/daemon.log  
/var/log/kern.log  
/var/log/auth.log  
/var/log/user.log  
/var/log/lpr.log  
/var/log/cron.log  
/var/log/debug  
/var/log/messages  
{  
rotate 4  
weekly  
missingok  
notifempty  
compress  
delaycompress  
sharedscripts  
postrotate  
invoke-rc.d rsyslog reload > /dev/null  
endscript  
}`

Как видите,  файл «syslog» будет повторно инициализирован каждый день. Другие журнальные файлы ротируются каждую неделю.

Также стоит упомянуть директив postrotate. Она указывает действие, которое происходит после того, как ротация журналов завершена.

### Тестирование ротации

Logrotate можно запустить вручную для ротации одного или нескольких файлов. Чтобы это сделать, нужно просто указать соответствующий конфигурационный файл как аргумент.

Чтобы продемонстрировать, как это работает, ниже приведен неполный список журнальных файлов в каталоге /var/log на CentOS:

`[root@TestLinux ~]# ls -l /var/log  
total 800  
...  
-rw-------  1 root root    359 Dec 17 18:25 maillog  
-rw-------. 1 root root   1830 Dec 16 16:35 maillog-20131216  
-rw-------  1 root root  30554 Dec 17 18:25 messages  
-rw-------. 1 root root 180429 Dec 16 16:35 messages-20131216  
-rw-------  1 root root    591 Dec 17 18:28 secure  
-rw-------. 1 root root   4187 Dec 16 16:41 secure-20131216  
...  
...`

Неполное содержимое файла logrotate.conf выглядит так:

`[root@TestLinux ~]# cat /etc/logrotate.conf  
# see "man logrotate" for details  
# rotate log files weekly  
weekly  
# keep 4 weeks worth of backlogs  
rotate 4  
# create new (empty) log files after rotating old ones  
create  
...  
...`

Затем запустите команду logrotate:

`[root@TestLinux ~]# logrotate -fv /etc/logrotate.conf`

Сообщения прокручиваются при создании новых файлов, обнаружении ошибок и т.д. Затем  попробуйте проверить новые журнальные файлы почты, безопасности и сообщений:

`[root@TestLinux ~]# ls -l /var/log/mail*  
-rw-------  1 root root    0 Dec 17 18:34 /var/log/maillog  
-rw-------. 1 root root 1830 Dec 16 16:35 /var/log/maillog-20131216  
-rw-------  1 root root  359 Dec 17 18:25 /var/log/maillog-20131217  
[root@TestLinux ~]# ls -l /var/log/messages*  
-rw-------  1 root root    148 Dec 17 18:34 /var/log/messages  
-rw-------. 1 root root 180429 Dec 16 16:35 /var/log/messages-20131216  
-rw-------  1 root root  30554 Dec 17 18:25 /var/log/messages-20131217  
[root@TestLinux ~]# ls -l /var/log/secure*  
-rw-------  1 root root    0 Dec 17 18:34 /var/log/secure  
-rw-------. 1 root root 4187 Dec 16 16:41 /var/log/secure-20131216  
-rw-------  1 root root  591 Dec 17 18:28 /var/log/secure-20131217  
[root@TestLinux ~]#`

Как можно видеть, все три новых журнала были созданы. Почтовый журнал и журнал безопасности все еще пусты, но новый журнал сообщений уже содержит некоторые данные.




**********
[Ubuntu](/tags/Ubuntu.md)
[CentOS](/tags/CentOS.md)
[logger](/tags/logger.md)
