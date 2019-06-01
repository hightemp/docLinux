# Оптимизация настроек MySQL с помощью Mysqltuner

Mysqltuner — это perl-скрипт, который анализирует статистику работы Mysql и выдает свои рекомендации по оптимизации настроек Mysql сервера.

Скачать скрипт можно следующим образом:

```
# wget [https://raw.githubusercontent.com/major/MySQLTuner-perl/master/mysqltuner.pl](https://raw.githubusercontent.com/major/MySQLTuner-perl/master/mysqltuner.pl)
```

Если возникает ошибка вида:

```
 ERROR: cannot verify raw.githubusercontent.com's certificate, issued by '/C=US/O=DigiCert Inc/OU=www.digicert.com/CN=DigiCert SHA2 High Assurance Server CA':
 Unable to locally verify the issuer's authority.
 To connect to raw.githubusercontent.com insecurely, use `--no-check-certificate'.
```

Запускаем с ключом --no-check-certificate:

```
# wget [https://raw.githubusercontent.com/major/MySQLTuner-perl/master/mysqltuner.pl](https://raw.githubusercontent.com/major/MySQLTuner-perl/master/mysqltuner.pl) --no-check-certificate
```

Также, можно произвести установку:

Debian/Ubuntu:

```
# apt-get -y install mysqltuner
```

CentOS:

```
# yum -y install mysqltuner
```

**Чтобы данные анализа и статистика были более корректными, сервер Mysql должен проработать некоторое время без смены параметров конфигурации и без перезагрузок, по рекомендации самого Mysqltuner не менее 24 часов.**

Теперь можно запускать Mysqltuner.

Если производилось скачивание скрипта:

```
# perl mysqltuner.pl
```

или

```
# perl mysqltuner.pl --user root --pass rootpassword
```

Если производилась установка:

```
#  mysqltuner
```

или

```
#  mysqltuner --user root --pass rootpassword
```
  
После запуска скрипт произведет анализ и выдаст следующую информацию:

```
# perl mysqltuner.pl --user root --pass rootpassword
>>  MySQLTuner 1.2.0 - Major Hayden <major@mhtx.net>
>>  Bug reports, feature requests, and downloads at [http://mysqltuner.com/](http://mysqltuner.com/)
>>  Run with '--help' for additional options and output filtering
[OK] Logged in using credentials passed on the command line

-------- General Statistics --------------------------------------------------
[--] Skipped version check for MySQLTuner script
[OK] Currently running supported MySQL version 5.5.33
[OK] Operating on 32-bit architecture with less than 2GB RAM

-------- Storage Engine Statistics -------------------------------------------
[--] Status: -Archive -BDB -Federated +InnoDB -ISAM -NDBCluster 
[--] Data in PERFORMANCE_SCHEMA tables: 0B (Tables: 17)
[!!] InnoDB is enabled but isn't being used
[OK] Total fragmented tables: 0

-------- Security Recommendations  -------------------------------------------
[OK] All database users have passwords assigned

-------- Performance Metrics -------------------------------------------------
[--] Up for: 20h 45m 49s (101 q [0.001 qps], 7 conn, TX: 28K, RX: 3K)
[--] Reads / Writes: 100% / 0%
[--] Total buffers: 160.0M global + 832.0K per thread (151 max threads)
[OK] Maximum possible memory usage: 282.7M (55% of installed RAM)
[OK] Slow queries: 0% (0/101)
[OK] Highest usage of available connections: 1% (2/151)
[!!] Key buffer size / total MyISAM indexes: 16.0K/679.0K
[!!] Query cache is disabled
[OK] Temporary tables created on disk: 3% (3 on disk / 94 total)
[!!] Thread cache is disabled
[!!] Table cache hit rate: 11% (4 open / 35 opened)
[OK] Open file limit used: 0% (6/7K)
[OK] Table locks acquired immediately: 100% (37 immediate / 37 locks)
[!!] Connections aborted: 14%

-------- Recommendations -----------------------------------------------------
General recommendations:
   Add skip-innodb to MySQL configuration to disable InnoDB
   MySQL started within last 24 hours - recommendations may be inaccurate
   Enable the slow query log to troubleshoot bad queries
   Set thread_cache_size to 4 as a starting value
   Increase table_cache gradually to avoid file descriptor limits
   Your applications are not closing MySQL connections properly
Variables to adjust:
   key_buffer_size (> 679.0K)
   query_cache_size (>= 8M)
   thread_cache_size (start at 4)
   table_cache (> 4)
```
  

**Особое внимание стоит уделить строкам, помеченным символами \[!!\] и секции Recommendations.**

Параметры указанные после строки **Variables to adjust** нужно изменить в файле my.cnf, в соответствии с рекомендациями Mysqltuner. Если указанного параметра нет в файле my.cnf, то его следует дописать.

Расположение конфигурационного файла my.cnf:

Debian/Ubuntu:

```
/etc/mysql/my.cnf
```

CentOS:

```
/etc/my.cnf
```

После внесения изменений в файл my.cnf нужно перезагрузить Mysql-сервер:

Debian/Ubuntu:

```
# /etc/init.d/mysql restart
```

CentOS 6:

```
# /etc/init.d/mysqld restart
```

Centos 7

```
# systemctl restart mariadb
```

После изменения конфигурации Mysql-сервер должен проработать минимум 24 часа без перезагрузок. Затем, можно снова запустить утилиту Mysqltuner и проанализировать вывод статистики. Таким образом, можно привести конфигурационный файл my.cnf и работу Mysql-сервера, соответственно, к оптимальному состоянию.

Сайт:[http://mysqltuner.com/](http://mysqltuner.com/)

**********
[Ubuntu](/tags/Ubuntu.md)
[CentOS](/tags/CentOS.md)
[MySQL](/tags/MySQL.md)
