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

Мы будем использовать этот последний вариант, поэтому установите _cgroup-tools_ с

```console
$ sudo apt-get install cgroup-tools
```

Debian по умолчанию отключает контроллер памяти, мы можем включить его, добавив следующее в `/etc/default/grub`

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet cgroup_enable=memory swapaccount=1"
```

Итак, обновите Grub

```console
$ sudo update-grub
```

Теперь, когда среда и инструменты готовы, мы определим некоторые «роли» в `/etc/cgconfig.conf`

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

Максимальное значение для `cpu.shares` равно 1000, поэтому 300 устанавливает 30% предела использования для приложения с этой «ролью». `memory.limit_in_bytes` является самоописательной.

Мы свяжем эти «роли» и приложения в `/etc/cgrules.conf`

```
    *:emacs         cpu,memory      app/editor/
    *:conkeror      cpu,memory      app/browser/
    *:firefox       cpu,memory      app/browser/
    *:slack         cpu,memory      app/util/
    *:dropbox       cpu,memory      app/util/
```   

Теперь нам нужно применить правила с помощью команд

```console
$ cgconfigparser -l /etc/cgconfig.conf
$ cgrulesengd
```    

Добавьте их в `/etc/rc.local` для применения при перезагрузке.

Вот и все!

Мы можем проверить, были ли применены наши новые правила, используя

```console
$ cat /proc/`pidof dropbox`/cgroup | grep app
# 5:memory:/app/util
# 2:cpu,cpuacct:/app/util
```

И мы можем проверить использование памяти процесса с

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