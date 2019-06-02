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

Note that if /data/mysql/mysql7 doesn’t exist and you start this instance anyway then myqld\_multi will call mysqld\_install\_db itself to have the datadir created and the system tables installed inside it. Alternatively, from restoring a backup or having a new datadir created you can make a physical copy of the existing one from the main instance – just make sure to stop it first with a clean shutdown, so any pending changes are flushed to disk first.

Now, you may have noted I wrote above that you need toreplaceyour original MySQL instance group (\[mysqld\]) by one with an option group number (\[mysql_N_\]). That’s not entirely true, as they can co-exist in harmony. However, the usual start/stop script used to manage MySQL won’t work with the additional instances, nor mysqld\_multi really manages \[mysqld\]. The simple solution here is to have the group \[mysqld\] renamed with a suffix integer, say \[mysqld0\] (you don’t need to make any changes to its current options though), and let mysqld\_multi manage all instances.

Two commands you might find useful when configuring multiple instances are:

```
$ mysqld_multi --example
```

…which provides an example of a my.cnf file configured with multiple instances and showing the use of different options, and:

```
$ my_print_defaults --defaults-file=/etc/my.cnf mysqld7
```

…which shows how a given group (“mysqld7” in the example above) was defined within my.cnf.

## Managing multiple instances

_mysqld\_multi_ allows you to start, stop, reload (which is effectively a restart) and report the current status of a given instance, all instances or a subset of them. The most important observation here is that the “stop” action is managed through mysqladmin – and internally that happens on an individual basis, with one “mysqladmin … stop” call per instance, even if you have mysqld\_multi stop all of them. For this to work properly you need to setup a MySQL account with the SHUTDOWN privilege and defined with the same user name and password in all instances. Yes, it will work out of the box if you run mysqld\_multi as root in a freshly installed server where the root user can access MySQL passwordless in all instances. But as the[manual](http://dev.mysql.com/doc/refman/5.6/en/mysqld-multi.html "mysqld_multi — Manage Multiple MySQL Servers")suggests, it’s better to have a specific account created for this purpose:

```
mysql> GRANT SHUTDOWN ON *.* TO 'multi_admin'@'localhost' IDENTIFIED BY 'multipass';
mysql> FLUSH PRIVILEGES;
```

If you plan on replicating the datadir of the main server across your other instances you can have that account created before you make copies of it, otherwise you just need to connect to each instance and create a similar account (remember, the privileged account is only needed by mysqld_multi to stop the instances, not to start them). There’s a special group that can be used on my.cnf to define options for mysqld_multi, which should be used to store these credentials. You might also indicate in there the path for the mysqladmin and mysqld (or [mysqld\_safe](http://dev.mysql.com/doc/refman/5.6/en/mysqld-safe.html "mysqld_safe — MySQL Server Startup Script")) binaries to use, though you might have a specific mysqld binary defined for each instance inside its respective group. Here’s one example:

```
[mysqld_multi]
mysqld     = /usr/bin/mysqld_safe
mysqladmin = /usr/bin/mysqladmin
user       = multi_admin
password   = multipass
```

You can use mysqld_multi to start, stop, restart or report the status of a particular instance, all instances or a subset of them. Here are a few examples that speak for themselves:

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

### Managing the MySQL daemon

What is missing here is an init script to automate the start/stop of all instances upon server initialization/shutdown; now that we use mysqld\_multi to control the instances, the usual /etc/init.d/mysql won’t work anymore. But a similar startup script (though much simpler and less robust) relying on mysqld\_multi is provided alongside MySQL/Percona Server, which can be found in /usr/share/<mysql|percona-server>/mysqld\_multi.server. You can simply copy it over as /etc/init.d/mysql, effectively replacing the original script while maintaining its name._**Please note:**_ You may need to edit it first and modify the first two lines defining “basedir” and “bindir” as this script was not designed to find out the good working values for these variables itself, which the original single-instance /etc/init.d/mysql does. Considering you probably have mysqld\_multi installed in /usr/bin, setting these variables as follows is enough:

```
basedir=/usr
bindir=/usr/bin
```

## Configuring an instance with a different version of MySQL

If you’re planning to have multiple instances of MySQL running concurrently chances are you want to use a mix of different versions for each of them, such as during a development cycle to test application compatibility. This is a common use for mysqld\_multi, and simple enough to achieve. To showcase its use I downloaded the latest version of MySQL 5.6 available and extracted the TAR file in /opt:

```
$ tar -zxvf mysql-5.6.20-linux-glibc2.5-x86_64.tar.gz -C /opt
```

Then I made a cold copy of the datadir from one of the existing instances to /data/mysql/mysqld574:

```
$ mysqld_multi stop 0
$ cp -r /data/mysql/mysql1 /data/mysql/mysql5620
$ chown mysql:mysql -R /data/mysql/mysql5620
```

and added a new group to my.cnf as follows:

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

Note the use of basedir, pointing to the path were the binaries for MySQL 5.6.20 were extracted, as well as a specific mysqld to be used with this instance. If you have made a copy of the datadir from an instance running a previous version of MySQL/Percona Server you will need to consider the same approach use when upgrading and run_mysql\_upgrade_.

\* I did try to use the latest experimental release of MySQL 5.7 (mysql-5.7.4-m14-linux-glibc2.5-x86\_64.tar.gz) but it crashed with:

```
*** glibc detected *** bin/mysqld: double free or corruption (!prev): 0x0000000003627650 ***
```

## Using the conventional tools to start and stop an instance

Even though mysqld\_multi makes things easier to control in general let’s not forget it is a wrapper; you can still rely (though not always, as shown below) on the conventional tools directly to start and stop an instance: mysqld\* and mysqladmin. Just make sure to use the parameter _–defaults-group-suffix_to identify which instance you want to start:

```
mysqld --defaults-group-suffix=5620
```

and _–socket_ to indicate the one you want to stop:

```
$mysqladmin -S /var/run/mysqld/mysqld5620.sock shutdown
```

_\* However_, mysqld won’t work to start an instance if you have redefined the option ‘mysqld’ on the configuration group, as I did for [mysqld5620] above, stating:

```
[ERROR] mysqld: unknown variable 'mysqld=/opt/mysql-5.6.20-linux-glibc2.5-x86_64/bin/mysqld_safe'
```

I’ve tested using “ledir” to indicate the path to the directory containing the binaries for MySQL 5.6.20 instead of “mysqld” but it also failed with a similar error. If nothing else, that shows you need to stick with mysqld_multi when starting instances in a mixed-version environment.

## Backups

The backup of multiple instances must be done on an individual basis like you would if each instance was located in a different server. You just need to provide the appropriate parameters to identify the instance you’re targeting. For example, we can simply use_socket_ with mysqldump when running it locally:

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