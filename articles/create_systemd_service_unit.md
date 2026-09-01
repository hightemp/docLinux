# Как создать сервисный модуль systemd в Linux

Although systemd has been the object of many controversies, to the point the some distributions were forked just to get rid of it (see Devuan, a fork of Debian which, by default, replaces systemd with sysvinit), in the end it has become the de-facto standard init system in the Linux world.

In this tutorial we will see how a systemd service is structured, and we will learn how to create one.

**In this tutorial you will learn:**

*   What is a service unit..
*   What are the sections of a service unit.
*   What are the most common options which can be used in each section.
*   What are the different types of service that can be defined.

## Software Requirements and Conventions Used

Software Requirements and Linux Command Line Conventions

| Category | Requirements, Conventions or Software Version Used |
| --- | --- |
| System | A GNU/Linux distribution which uses systemd as init system |
| Software | systemd |
| Other | Root permissions are required to install and manage a service. |
| Conventions | **#**\- requires given[linux commands](https://linuxconfig.org/linux-commands) to be executed with root privileges either directly as a root user or by use of `sudo` command  

**$**\- requires given[linux commands](https://linuxconfig.org/linux-commands)to be executed as a regular non-privileged user  
 |

## The systemd init system

All the major distributions, such as Rhel, CentOS, Fedora, Ubuntu, Debian and Archlinux, adopted systemd as their init system. Systemd, actually, is more than just an init system, and that's one of the reasons why some people are strongly against its design, which goes against the well established unix motto: "do one thing and do it well". Where other init systems use simple shell script to manage services, systemd uses its own`.service`files (units with the .service suffix): in this tutorial we will see how they are structured and how to create and install one.

## Anatomy of a service unit

What is a service unit? A file with the`.service`suffix contains information about a process which is managed by systemd. It is composed by three main sections:

*   \[Unit\]: this section contains information not specifically related to the type of the unit, such as the service description
*   \[Service\]: contains information about the specific type of the unit, a service in this case
*   \[Install\]: This section contains information about the installation of the unit

Let's analyze each of them in detail.

## The \[Unit\] section

The`[Unit]`section of a`.service`file contains the description of the unit itself, and information about its behavior and its dependencies: (to work correctly a service can depend on another one). Here we discuss some of the most relevant options which can be used in this section

### The "Description" option

First of all we have the`Description`option. By using this option we can provide a description of the unit. The description will then appear, for example, when calling the`systemctl`command, which returns an overview of the status of systemd. Here it is, as an example, how the description of`httpd`service is defined on a Fedora system:

\[Unit\]
Description=The Apache HTTP Server

### The "After" option

By using the`After`option, we can state that our unit should be started after the units we provide in the form of a space-separated list. For example, observing again the service file where the Apache web service is defined, we can see the following:

After=network.target remote-fs.target nss-lookup.target httpd-init.service

The line above instructs systemd to start the service unit`httpd.service`only after the`network`,`remove-fs`,`nss-lookup`targets and the`httpd-init service`

### Specifying hard dependencies with "Requires"

As we briefly mentioned above, a unit (a service in our case) can depend on other units (not necessarily "service" units) to work correctly: such dependencies can be declared by using the`Requires`option.

If any of the units on which a service depends fails to start, the activation of the service it's stopped: this is why those are called`hard dependencies`. In this line, extracted from the service file of the avahi-daemon, we can see how it is declared as dependent from the avahi-daemon.socket unit:

Requires=avahi-daemon.socket

### Declaring "soft" dependencies with "Wants"

We just saw how to declare the so called "hard" dependencies for the service by using the`Requires`option; we can also list "soft" dependencies by using the`Wants`option.

What is the difference? As we said above, if any "hard" dependency fails, the service will fail itself; a failure of any "soft" dependency, however, doesn't influence what happens to the dependent unit. In the provided example, we can see how the`docker.service`unit has a soft dependency on the`docker-storage-setup.service`one:

```
[Unit]
Wants=docker-storage-setup.service

```

## The \[Service\] section

In the`[Service]`section of a`service`unit, we can specify things as the command to be executed when the service is started, or the type of the service itself. Let's take a look at some of them.

## Starting, stopping, and reloading a service

A service can be started, stopped, restarted or reloaded. The commands to be executed when performing each of these actions can be specified by using the related options in the`[Service]`section.

The command to be executed when a service starts, is declared by using the`ExecStart`option. The argument passed to the option can also be the path to a script. Optionally, we can declare commands to be executed before and after the service is started, by using the`ExecStartPre`and`ExecStartPost`options respectively. Here is the command used to start the NetworkManager service:


```
[Service]
ExecStart=/usr/sbin/NetworkManager --no-daemon

```

In a similar fashion, we can specify the command to be executed when a service is reloaded or stopped, by using the`ExecStop`and`ExecReload`options. Similarly to what happens with`ExecStartPost`, a command or multiple commands to be launched after a process is stopped, can be specified with the`ExecStopPost`option.

### The type of the service

Systemd defines and distinguish between some different type of services depending on their expected behavior. The type of a service can be defined by using the`Type`option, providing one of these values:

*   simple
*   forking
*   oneshot
*   dbus
*   notify

The default type of a service, if the`Type`and`Busname`options are not defined, but a command is provided via the`ExecStart`option, is`simple`. When this type of service is set, the command declared in`ExecStart`is considered to be the main process/service.

The`forking`type works differently: the command provided with`ExecStart`is expected to fork and launch a child process, which will become the main process/service. The parent process it's expected to die once the startup process is over.

The`oneshot`type is used as the default if the`Type`and`ExecStart`options are not defined. It works pretty much like`simple`: the difference is that the process is expected to finish its job before other units are launched. The unit, however, it's still considered as "active" even after the command exits, if the`RemainAfterExit`option is set to "yes" (the default is "no").

The next type of service is`dbus`. If this type of service is used, the daemon is expected to get a name from`Dbus`, as specified in the`BusName`option, which in this case, becomes mandatory. For the rest it works like the`simple`type. Consequent units, however, are launched only after the DBus name is acquired.

Another process works similarly to`simple`, and it is`notify`: the difference is that the daemon is expected to send a notification via the`sd_notify`function. Only once this notification is sent, consequent units are launched.

### Set process timeouts

By using specific options, it's possible to define some timeouts for the service. Let's start with`RestartSec`: by using this option, we can setup the amount of time (by default in seconds) systemd should wait before restarting a service. A timespan can also be used as a value for this option, as "5min 20s". The default is`100ms`.


The`TimeoutStartSec`and`TimeoutStopSec`options can be used to specify, respectively, the timeout for a service startup and stop, in seconds. In the first case, if after the specified timeout the daemon startup process it's not completed, it will be considered to be failed.

In the second case, if a service is to be stopped but is not terminated after the specified timeout, first a`SIGTERM`and then, after the same amount of time, a`SIGKILL`signal are sent to it. Both options accepts also a timespan as a value and can be configured at once, with a shortcut:`TimeoutSec`. If`infinity`is provided as a value, the timeouts are disabled.

Finally, we can setup the limit for the amount of time a service can run, using the`RuntimeMaxSec`. If a service exceeds this timeout, it's terminated and considered as failed.

## The \[Install\] section

In the`[install]`section, we can use options related to the service installation. For example, by using the`Alias`option, we can specify a space separated list of aliases to be used for the service when using the systemctl commands (except`enable`).

Similarly to what happens with the`Requires`and`Wants`options in the`[Unit]`section, to establish dependencies, in the`[install]`section, we can use`RequiredBy`and`WantedBy`. In both cases we declare a list of units which depend on the one we are configuring: with the former option they will be hard-dependent on it, with the latter they will be considered only as weak-dependent. For example:

\[Install\]
WantedBy=multi-user.target

With the line above we declared that the`multi-user`target has a soft dependency on our unit. In systemd terminology, units ending with the`.target`suffix, can be associated with what were called`runtimes`in other init systems as`Sysvinit`. In our case, then, the multi-user target, when reached, should include our service.

## Creating and installing a service unit

There are basically two places in the filesystem where systemd service units are installed:`/usr/lib/systemd/system`and`/etc/systemd/system`. The former path is used for services provided by installed packages, while the latter can be used by the system administrator for its own services which can override the default ones.

Let's create a custom service example. Suppose we want to create a service which disables the wake-on-lan feature on a specific ethernet interface (ens5f5 in our case) when it is started, and re-enables it when it is stopped. We can use the`ethtool`command to accomplish the main task. Here is how our service file could look like:

```shell
[Unit]
Description=Force ens5f5 ethernet interface to 100Mbps
Requires=network.target
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/ethtool -s ens5f5 wol d
ExecStop=/usr/sbin/ethtool -s ens5f5 wol g

[Install]
WantedBy=multi-user.target

```

We set a simple unit description, and declared that the service depends on the`network.target`unit and should be launched after it is reached. In the`[Service]`section we set the type of the service as`oneshot`, and instructed systemd to consider the service to be active after the command is executed, using the`RemainAfterExit`option. We also defined the commands to be run when the service is started and stopped. Finally, in the`[Install]`section we basically declared that our service should be included in the`multi-user`target.

To install the service we will copy the file into the`/etc/systemd/system`directory as`wol.service`, than we will start it:

$ sudo cp wol.service /etc/systemd/system && sudo systemctl start wol.service

We can verify the service is active, with the following command:

$ systemctl is-active wol.service
active

The output of the command, as expected, is`active`. Now to verify that "wake on lan" has been set to`d`, and so it is now disabled, we can run:

$ sudo ethtool ens5f5|grep Wake-on
Supports Wake-on: pg
Wake-on: d

Now, stopping the service should produce the inverse result, and re-enable wol:

$ sudo systemctl stop wol.service && sudo ethtool ens5f5|grep Wake-on
Supports Wake-on: pg
Wake-on: g

## Conclusions

In this tutorial we saw how a systemd service file is composed, what are its sections, and some of the options which can be used in each of them. We learned how to setup a service description, to define its dependencies and to declare the commands that should be executed when it is started, stopped or reloaded.

Since systemd, like it or not, has become the standard init system in the Linux world, it's important to become familiar to its way of doing things. The official systemd services documentation can be found[on the freedesktop website](https://www.freedesktop.org/software/systemd/man/systemd.service.html). You could also be interested in reading our article about[managing services with systemd](https://linuxconfig.org/start-stop-and-restart-services-on-systemd-rhel-7-linux-server).





**********
[service](/tags/service.md)
[systemd](/tags/systemd.md)
[НЕ ПЕРЕВЕДЕНО](/tags/%D0%9D%D0%95%20%D0%9F%D0%95%D0%A0%D0%95%D0%92%D0%95%D0%94%D0%95%D0%9D%D0%9E.md)
