# mysqld_multi: как запустить несколько экземпляров MySQL

Необходимость иметь несколько экземпляров MySQL (хорошо известный процесс _mysqld_), работающих на одном и том же сервере одновременно прозрачным образом, вместо того, чтобы выполнять их в отдельных контейнерах / виртуальных машинах, не очень распространена. Тем не менее, время от времени команда [Percona Support](https://www.percona.com/products/mysql-support) получает запрос от клиента для помощи в настройке такой среды. MySQL предоставляет инструмент для облегчения выполнения нескольких экземпляров, который называется [mysqld\_multi](http://dev.mysql.com/doc/refman/5.6/en/mysqld-multi.html "«mysqld_multi» - управление несколькими серверами MySQL."):

> _“mysqld_multiis предназначен для управления несколькими процессами mysqld, которые прослушивают соединения в различных файлах сокетов Unix и портах TCP / IP. Он может запускать или останавливать серверы или сообщать об их текущем состоянии.”_

В целях тестирования и разработки [MySQL Sandbox](http://mysqlsandbox.net/ "MySQL Sandbox") может быть более практичным, и я лично предпочитаю использовать его для своих собственных тестов. Оба инструмента работают вокруг запуска и управления несколькими процессами mysqld, но Sandbox имеет, как следует из названия, подход «песочницы», облегчающий создание и удаление нового экземпляра (включая все данные внутри него). Чаще всего mysqld\_multi используется на производственных серверах: он поставляется с серверным пакетом и использует тот же единственный файл конфигурации, который люди привыкли искать при настройке MySQL. Итак, как это работает? Как мы настраиваем и управляем экземплярами? И, что важно, как мы создаем резервные копии всех созданных нами экземпляров?

## Понимание концепции групп в my.cnf

Возможно, вы уже заметили, что основной файл конфигурации MySQL (или [файл опций](http://dev.mysql.com/doc/refman/5.6/en/option-files.html "Использование файлов опций") ), my.cnf организован в соответствии с так называемой_группой_структур: разделами, определяющими параметры конфигурации, специфичные для данной программы или цели. Обычно сама программа дает имя группе, которая отображается в квадратных скобках. Вот простой my.cnf, показывающий три такие группы:

```
[client]
port		= 3306
socket		= /var/run/mysqld/mysqld.sock
user            = john
password        = p455w0rd

[mysqld]
user		= mysql
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
port		= 3306
datadir		= /var/lib/mysql

[xtrabackup]
target_dir = /backups/mysql/
```

Параметры, определенные в группе \[клиент\] выше, используются инструментом командной строки _mysql_. Таким образом, если вы не укажете какую-либо другую опцию при выполнении _mysql_, она попытается подключиться к локальному серверу MySQL через сокет в /var/run/mysqld/mysqld.sock и использовать учетные данные, указанные в этой группе. Точно так же _mysqld_ будет искать параметры, определенные в его разделе при запуске, и то же самое происходит с [Percona XtraBackup](https://www.percona.com/software/percona-xtrabackup) при запуске резервного копирования с этим инструмент. Однако рабочие параметры, определенные вышеупомянутыми группами, также могут быть указаны как параметры командной строки во время выполнения программы, и в этом случае они заменяют параметры, определенные в my.cnf.

## Начало работы с несколькими экземплярами MySQL

Чтобы иметь несколько запущенных экземпляров MySQL, мы должны заменить группу \[mysqld\] в файле конфигурации my.cnf на столько групп \[mysql _N_\], сколько мы хотим, чтобы экземпляры работали, причем «N» - это положительное целое число, а также группа вызываемых действий число. Этот номер используется mysqld\_multi для идентификации каждого экземпляра, поэтому он должен быть уникальным для всего сервера. Помимо отдельного имени группы, те же параметры, которые действительны для \[mysqld\], применяются к \[mysqld _N_\] группам, с той разницей, что указывать их необязательно для \[mysqld\] (это возможно для запуска MySQL с пустым my.cnf, поскольку значения по умолчанию используются, если не указано иное), некоторые из них (например, сокет, порт, pid-файл и datadir) обязательны при определении нескольких экземпляров, поэтому они не Не наступайте друг другу на ноги. Вот простой модифицированный my.cnf, показывающий исходную группу \[mysqld\] плюс два других экземпляра:

```
[mysqld]
user		= mysql
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
port		= 3306
datadir		= /var/lib/mysql

[mysqld1]
user		= mysql
pid-file	= /var/run/mysqld/mysqld1.pid
socket		= /var/run/mysqld/mysqld1.sock
port		= 3307
datadir		= /data/mysql/mysql1

[mysqld7]
user		= mysql
pid-file	= /var/run/mysqld/mysqld7.pid
socket		= /var/run/mysqld/mysqld7.sock
port		= 3308
datadir		= /data/mysql/mysql7
```

Помимо использования разных pid-файлов, портов и сокетов для новых экземпляров, я также определил разные datadir для каждого - очень важно, чтобы экземпляры [не **не** совместно использовали один и тот же datadir](http://dev.mysql.com/doc/refman/5.6/en/multiple-data-directories.html "Настройка нескольких каталогов данных"). Скорее всего, вы импортируете данные из резервной копии, но если это не так, вы можете просто использовать mysql_install_db для создания каждого дополнительного каталога данных (но убедитесь, что родительский каталог существует и что у пользователя mysql есть доступ для записи в него):

```
mysql_install_db --user=mysql --datadir=/data/mysql/mysql7
```

Обратите внимание, что если /data/mysql/mysql7 не существует, и вы все равно запустите этот экземпляр, то myqld\_multi сам вызовет mysqld\_install\_db, чтобы создать каталог данных и установить внутри него системные таблицы. В качестве альтернативы, восстановив резервную копию или создав новый каталог данных, вы можете сделать физическую копию существующего из основного экземпляра - просто убедитесь, что сначала остановили его с чистым завершением, так что все ожидающие изменения будут сначала записаны на диск ,

Теперь вы, возможно, заметили, что я написал выше, что вам нужно заменить исходную группу экземпляров MySQL (\[mysqld\]) на группу с номером группы параметров (\[mysql _N_ \]). Это не совсем верно, так как они могут сосуществовать в гармонии. Однако обычный скрипт start / stop, используемый для управления MySQL, не будет работать с дополнительными экземплярами, и mysqld\_multi действительно не управляет \[mysqld\]. Простое решение здесь состоит в том, чтобы переименовать группу \[mysqld\] с суффиксным целым числом, скажем, \[mysqld0\] (вам не нужно вносить какие-либо изменения в его текущие параметры), и позволить mysqld\_multi управлять все случаи.

Две команды, которые могут оказаться полезными при настройке нескольких экземпляров:

```
$ mysqld_multi --example
```

…который предоставляет пример файла my.cnf, настроенного с несколькими экземплярами и показывающего использование различных параметров, и:

```
$ my_print_defaults --defaults-file=/etc/my.cnf mysqld7
```

…который показывает, как данная группа («mysqld7» в приведенном выше примере) была определена в my.cnf.

## Управление несколькими экземплярами

_mysqld\_multi_ позволяет запускать, останавливать, перезагружать (что фактически является перезапуском) и сообщать о текущем состоянии данного экземпляра, всех экземпляров или их подмножества. Наиболее важным наблюдением здесь является то, что действие «остановки» управляется через mysqladmin - и внутренне, что происходит на индивидуальной основе, с одним вызовом «mysqladmin» - stop »на экземпляр, даже если у вас есть mysqld\_multi останови их всех. Чтобы это работало должным образом, вам необходимо настроить учетную запись MySQL с привилегией SHUTDOWN, для которой во всех случаях задано одно и то же имя пользователя и пароль. Да, он будет работать «из коробки», если вы запустите mysqld\_multi от имени пользователя root на только что установленном сервере, где пользователь root может получить доступ к MySQL без пароля во всех случаях. Но, как предполагает [руководство](http://dev.mysql.com/doc/refman/5.6/en/mysqld-multi.html "mysqld_multi - управление несколькими серверами MySQL"), лучше иметь определенная учетная запись, созданная для этой цели:

```
mysql> GRANT SHUTDOWN ON *.* TO 'multi_admin'@'localhost' IDENTIFIED BY 'multipass';
mysql> FLUSH PRIVILEGES;
```

Если вы планируете реплицировать каталог данных главного сервера на другие ваши экземпляры, вы можете создать эту учетную запись, прежде чем создавать ее копии, в противном случае вам просто нужно подключиться к каждому экземпляру и создать аналогичную учетную запись (помните, привилегированная учетная запись является только необходим mysqld_multi для остановки экземпляров, а не для их запуска). В my.cnf можно использовать специальную группу для определения параметров mysqld_multi, которую следует использовать для хранения этих учетных данных. Вы также можете указать там путь для mysqladmin и mysqld (или [mysqld\_safe](http://dev.mysql.com/doc/refman/5.6/en/mysqld-safe.html "mysqld_safe - MySQL Сценарий запуска сервера")) двоичные файлы для использования, хотя у вас может быть определенный двоичный файл mysqld, определенный для каждого экземпляра в соответствующей группе. Вот один пример:

```
[mysqld_multi]
mysqld     = /usr/bin/mysqld_safe
mysqladmin = /usr/bin/mysqladmin
user       = multi_admin
password   = multipass
```

Вы можете использовать mysqld_multi, чтобы запускать, останавливать, перезапускать или сообщать о состоянии конкретного экземпляра, всех экземпляров или их подмножества. Вот несколько примеров, которые говорят сами за себя:

```
$ mysqld_multi report
Reporting MySQL (Percona Server) servers
MySQL (Percona Server) from group: mysqld0 is not running
MySQL (Percona Server) from group: mysqld1 is not running
MySQL (Percona Server) from group: mysqld7 is not running
$ mysqld_multi start
$ mysqld_multi report
Reporting MySQL (Percona Server) servers
MySQL (Percona Server) from group: mysqld0 is running
MySQL (Percona Server) from group: mysqld1 is running
MySQL (Percona Server) from group: mysqld7 is running
$ mysqld_multi stop 7,0
$ mysqld_multi report 7
Reporting MySQL (Percona Server) servers
MySQL (Percona Server) from group: mysqld7 is not running
$ mysqld_multi report
Reporting MySQL (Percona Server) servers
MySQL (Percona Server) from group: mysqld0 is not running
MySQL (Percona Server) from group: mysqld1 is running
MySQL (Percona Server) from group: mysqld7 is not running
```

### Управление демоном MySQL

Чего здесь не хватает, так это сценария инициализации, который автоматизирует запуск/останов всех экземпляров при инициализации/завершении работы сервера; теперь, когда мы используем mysqld\_multi для управления экземплярами, обычный /etc/init.d/mysql больше не будет работать. Но аналогичный скрипт запуска (хотя и намного более простой и менее надежный), использующий mysqld\_multi, предоставляется вместе с MySQL/Percona Server, который можно найти в /usr/share/<mysql|percona-server>/mysqld\_multi.server. Вы можете просто скопировать его как /etc/init.d/mysql, эффективно заменив оригинальный скрипт, сохранив его имя . 

_**Обратите внимание:**_ Возможно, вам придется сначала отредактировать его и изменить первые две строки, определяющие «Baseir» и «bindir», так как этот сценарий не был предназначен для определения хороших рабочих значений для самих этих переменных, как это делает оригинальный единственный экземпляр /etc/init.d/mysql. Учитывая, что у вас, вероятно, есть mysqld\_multi, установленный в /usr/bin, достаточно установить следующие переменные:

```
basedir=/usr
bindir=/usr/bin
```

## Настройка экземпляра с другой версией MySQL

Если вы планируете запускать несколько экземпляров MySQL одновременно, есть вероятность, что вы захотите использовать разные версии для каждой из них, например, во время цикла разработки для проверки совместимости приложений. Это обычное использование для mysqld\_multi, и достаточно простое для достижения. Чтобы продемонстрировать его использование, я скачал последнюю версию MySQL 5.6 и извлек файл TAR в /opt:

```
$ tar -zxvf mysql-5.6.20-linux-glibc2.5-x86_64.tar.gz -C /opt
```

Затем я сделал холодную копию dadadir из одного из существующих экземпляров в /data/mysql/mysqld574:

```
$ mysqld_multi stop 0
$ cp -r /data/mysql/mysql1 /data/mysql/mysql5620
$ chown mysql:mysql -R /data/mysql/mysql5620
```

и добавил новую группу в my.cnf следующим образом:

```
[mysqld5620]
user            = mysql
pid-file        = /var/run/mysqld/mysqld5620.pid
socket          = /var/run/mysqld/mysqld5620.sock
port            = 3309
datadir         = /data/mysql/mysql5620
basedir         = /opt/mysql-5.6.20-linux-glibc2.5-x86_64
mysqld          = /opt/mysql-5.6.20-linux-glibc2.5-x86_64/bin/mysqld_safe
```

Обратите внимание на использование basedir, указывающее на путь, куда были извлечены двоичные файлы для MySQL 5.6.20, а также определенный mysqld для использования с этим экземпляром. Если вы сделали копию каталога данных из экземпляра, на котором запущена предыдущая версия MySQL / Percona Server, вам нужно будет рассмотреть тот же подход, который используется при обновлении и запустить _mysql\_upgrade_.

\* Я пытался использовать последний экспериментальный выпуск MySQL 5.7 (mysql-5.7.4-m14-linux-glibc2.5-x86\_64.tar.gz), но он потерпел крах:

```
*** glibc detected *** bin/mysqld: double free or corruption (!prev): 0x0000000003627650 ***
```

## Использование обычных инструментов для запуска и остановки экземпляра

Хотя mysqld\_multi упрощает управление, в общем, давайте не будем забывать, что это обертка; Вы все еще можете полагаться (хотя и не всегда, как показано ниже) на обычные инструменты для запуска и остановки экземпляра: mysqld\* и mysqladmin. Просто убедитесь, что вы используете параметр _--defaults-group-suffix_, чтобы определить, какой экземпляр вы хотите запустить:

```
mysqld --defaults-group-suffix=5620
```

и _–socket_ для указания того, кого вы хотите остановить:

```
$mysqladmin -S /var/run/mysqld/mysqld5620.sock shutdown
```

_\* Однако_, mysqld не будет работать для запуска экземпляра, если вы переопределили опцию «mysqld» в группе конфигурации, как я это сделал для \[mysqld5620\] выше, заявив:

```
[ERROR] mysqld: unknown variable 'mysqld=/opt/mysql-5.6.20-linux-glibc2.5-x86_64/bin/mysqld_safe'
```

Я проверил, используя «ledir», чтобы указать путь к каталогу, содержащему двоичные файлы для MySQL 5.6.20 вместо «mysqld», но он также потерпел неудачу с похожей ошибкой. Если ничего другого, это показывает, что вам нужно придерживаться mysqld_multi при запуске экземпляров в среде со смешанной версией.

## Резервные копии

Резервное копирование нескольких экземпляров должно выполняться на индивидуальной основе, как если бы каждый экземпляр находился на отдельном сервере. Вам просто нужно предоставить соответствующие параметры, чтобы идентифицировать экземпляр, на который вы нацеливаетесь. Например, мы можем просто использовать _socket_ с mysqldump при локальном запуске:

```
$ mysqldump --socket=/var/run/mysqld/mysqld7.sock --all-databases > mysqld7.sql
```

In Percona XtraBackup there’s an option named  [_–defaults-group_](https://www.percona.com/doc/percona-xtrabackup/2.2/innobackupex/innobackupex_option_reference.html#cmdoption-innobackupex--defaults-group "XtraBackup's --defaults-group option description") that should be used in environments running multiple instances to indicate which one you want to backup :

```
$ innobackupex --defaults-file=/etc/my.cnf --defaults-group=mysqld7 --socket=/var/run/mysqld/mysqld7.sock /root/Backup/
```

Yes, you also need to provide a path to the socket (when running the command locally), even though that information is already available in “–defaults-group=mysqld7”; as it turns out, only the Percona XtraBackup tool (which is called by innobackupex during the backup process) makes use of the information available in the group option. You may need to provide credentials as well (“–user” & “–password”), and don’t forget you’ll need to [prepare](https://www.percona.com/doc/percona-xtrabackup/2.2/howtos/recipes_ibkx_local.html "Make a Local Full Backup (Create, Prepare and Restore)") the backup afterward. The option “defaults-group” is not available in all versions of Percona XtraBackup so make sure to use the latest one.

## Summary

Running multiple instances of MySQL concurrently in the same server transparently and without any contextualization or a virtualization layer is possible with both mysqld\_multi and MySQL Sandbox. We have been using the later at Percona Support to quickly spin on new disposable instances (though you might as easily keep them running indefinitely). In this post though, I’ve looked at mysqld\_multi which is provided with MySQL server and remains the official solution for providing an environment with multiple instances.

The key aspect when configuring multiple instances in my.cnf is the notion of group name option, as you replace a single \[mysqld\] section by as many \[mysqld_N_\] sections as you want instances running. It’s important though to pay attention to certain details when defining the options for each one of these groups, especially when mixing instances from different MySQL/[Percona Server](https://www.percona.com/software/percona-server)versions. Different from MySQL Sandbox, where each instance relies on its own configuration file, you should be careful each time you edit the shared my.cnf file as a syntax error when configuring a single group option will prevent all instances from starting upon the server’s (re)initialization.

I hope to have covered the major points about mysqld\_multi here but feel free to leave us a note below if you have something else to add or any comment to contribute.