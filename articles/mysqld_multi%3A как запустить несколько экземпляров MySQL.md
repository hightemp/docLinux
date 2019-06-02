# mysqld_multi: как запустить несколько экземпляров MySQL

The need to have multiple instances of MySQL (the well-known_mysqld_process) running in the same server concurrently in a transparent way, instead of having them executed in separate containers/virtual machines, is not very common. Yet from time to time the[Percona Support](https://www.percona.com/products/mysql-support)team receives a request from a customer to assist in the configuration of such an environment. MySQL provides a tool to facilitate the execution of multiple instances called[mysqld\_multi](http://dev.mysql.com/doc/refman/5.6/en/mysqld-multi.html "mysqld_multi — Manage Multiple MySQL Servers"):

> _“mysqld_multiis designed to manage severalmysqldprocesses that listen for connections on different Unix socket files and TCP/IP ports. It can start or stop servers, or report their current status.”_

For tests and development purposes,[MySQL Sandbox](http://mysqlsandbox.net/ "MySQL Sandbox")might be more practical and I personally prefer to use it for my own tests. Both tools work around launching and managing multiple mysqld processes but Sandbox has, as the name suggests, a “sandbox” approach, making it easy to both create and dispose of a new instance (including all data inside it). It is more usual to see mysqld\_multi being used in production servers: It’s provided with the server package and uses the same single configuration file that people are used to looking for when setting up MySQL. So, how does it work? How do we configure and manage the instances? And as importantly, how do we backup all the instances we create?

## Understanding the concept of groups in my.cnf

You may have noticed already that MySQL’s main configuration file (or “[option file](http://dev.mysql.com/doc/refman/5.6/en/option-files.html "Using Option Files")“), my.cnf, is arranged under what is called_group_structures: Sections defining configuration options specific to a given program or purpose. Usually, the program itself gives a name to the group, which appears enclosed by brackets. Here’s a basic my.cnf showing three such groups:

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

The options defined in the group [client] above are used by the _mysql _command-line tool. As such, if you don’t specify any other option when executing _mysql_ it will attempt to connect to the local MySQL server through the socket in /var/run/mysqld/mysqld.sock and using the credentials stated in that group. Similarly, _mysqld_ will look for the options defined under its section at startup, and the same happens with [Percona XtraBackup](https://www.percona.com/software/percona-xtrabackup) when you run a backup with that tool. However, the operating parameters defined by the above groups may also be stated as command-line options during the execution of the program, in which case they replace the ones defined in my.cnf.

## Getting started with multiple instances of MySQL

To have multiple instances of MySQL running we mustreplacethe \[mysqld\] group in my.cnf configuration file by as many \[mysql_N_\] groups as we want instances running, with “N” being a positive integer, also calledoption group number. This number is used by mysqld\_multi to identify each instance, so it must be unique across the server. Apart from the distinct group name, the same options that are valid for \[mysqld\] applies on \[mysqld_N_\] groups, the difference being that while stating them is optional for \[mysqld\] (it’s possible to start MySQL with an empty my.cnf as default values are used if not explicitly provided) some of them (like socket, port, pid-file, and datadir) are mandatory when defining multiple instances – so they don’t step on each other’s feet. Here’s a simple modified my.cnf showing the original \[mysqld\] group plus two other instances:

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