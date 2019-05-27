# How to Limit CPU and Memory Usage With Cgroups on Debian/Ubuntu

Cgroups is a flexible Linux kernel feature to _limit_, _police_ and _account_ resources usage. A _cgroup_ is a set of _tasks_ for a _subsystems_, that is typically a _resource controller_.

A file system of type _cgroup_ is mounted and all operations are run over it.

## Installation

The installation can be done using any of_libcgroup_,_cgmanager_or_systemd_.

## Usage

They can be used in multiple ways

*   By accessing the cgroup_filesystem_directly.
*   Using the_cgm_client (part of the_cgmanager_).
*   Via_cgcreate_,_cgexec_and_cgclassify_(part of_cgroup-tools_).
*   Via_cgconfig.conf_and_cgrules.conf_(also part of_cgroup-tools_).

We will use this last option, so install_cgroup-tools_with

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