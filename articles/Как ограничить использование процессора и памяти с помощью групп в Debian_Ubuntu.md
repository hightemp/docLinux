# Как ограничить использование процессора и памяти с помощью групп в Debian/Ubuntu

Cgroups - это гибкая функция ядра Linux, позволяющая ограничивать, контролировать и использовать ресурсы аккаунта. _Cgroup_ - это набор задач для подсистем, обычно это контроллер ресурсов.

Файловая система типа _cgroup_ монтируется и все операции выполняются над ней.

## Установка

Установка может быть выполнена с использованием любого из _libcgroup_, _cgmanager_ или _systemd_.

## Использование

Их можно использовать несколькими способами

* Получая прямой доступ к файловой системе cgroup.
* Использование клиента cgm (часть _cgmanager_).
* Через _cgcreate_, _cgexec_ и _cgclassify_ (часть _cgroup-tools_).
* Через _cgconfig.conf_ и _cgrules.conf_ (также является частью _cgroup-tools_).

We will use this last option, so install _cgroup-tools_ with

```console
$ sudo apt-get install cgroup-tools
```

Debian, by default, disables the memory controller, we can enable it adding the following in`/etc/default/grub`

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet cgroup_enable=memory swapaccount=1"
```    

So, update Grub

```console
$ sudo update-grub
```

Now the environment and tools are ready, we will define some “roles” in`/etc/cgconfig.conf`

```
    group app/editor {
      cpu {
        cpu.shares = 500;
      }
      memory {
        memory.limit_in_bytes = 1000000000;
      }
    }
    
    group app/browser {
      cpu {
        cpu.shares = 300;
      }
      memory {
        memory.limit_in_bytes = 1000000000;
      }
    }
    
    group app/util {
      cpu {
        cpu.shares = 300;
      }
      memory {
        memory.limit_in_bytes = 500000000;
      }
    }
```    

The maximum value for`cpu.shares`is 1000, so 300 is setting as 30% the usage limit for an application with this “role”.`memory.limit_in_bytes`is self descriptive.

We will associate these “roles” and the applications in`/etc/cgrules.conf`

```
    *:emacs         cpu,memory      app/editor/
    *:conkeror      cpu,memory      app/browser/
    *:firefox       cpu,memory      app/browser/
    *:slack         cpu,memory      app/util/
    *:dropbox       cpu,memory      app/util/
```   

Now we need apply the rules with the commands

```console
$ cgconfigparser -l /etc/cgconfig.conf
$ cgrulesengd
```    

Add them in `/etc/rc.local` for applying on reboot.

That’s it!

We can check if our new rules were applied using

```console
$ cat /proc/`pidof dropbox`/cgroup | grep app
# 5:memory:/app/util
# 2:cpu,cpuacct:/app/util
```

And we can check the memory usage of a process with

```console
smem -P dropbox    
# PID User     Command                         Swap      USS      PSS      RSS
# 1955 fernando /home/fernando/.dropbox-dis        0   191800   192388   201124
```

## References

*   [https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt](https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt)
*   [https://www.kernel.org/doc/Documentation/cgroup-v1/memory.txt](https://www.kernel.org/doc/Documentation/cgroup-v1/memory.txt)
*   [https://wiki.archlinux.org/index.php/cgroups](https://wiki.archlinux.org/index.php/cgroups)
*   [https://github.com/docker/docker/issues/396#issuecomment-179470044](https://github.com/docker/docker/issues/396#issuecomment-179470044)