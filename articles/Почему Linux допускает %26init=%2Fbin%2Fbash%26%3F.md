# Почему Linux допускает "init=/bin/bash"?

When the computer starts, it runs a program called "init", usually found at`/bin/init`or`/sbin/init`. This program is responsible for all the system startup and creating a usable environment.

Specifying`init=/bin/bash`tells the kernel to run`/bin/bash`instead (which is a shell). Specifying`rw`tells the kernel to boot with the hard disk in read-write mode instead of read-only mode. Traditionally the kernel starts with the disk in read-only mode and a process later on checks the integrity of the disk before switching to read-write.