# Ограничение использования процессора с помощью nice, cpulimit и cgroups

### Имитация высокой загрузки процессора

Прежде чем рассматривать эти три метода, нам нужно найти инструмент, который будет моделировать высокую загрузку ЦП в системе. Мы будем использовать CentOS в качестве нашей базовой системы, и для искусственной загрузки процессора мы можем использовать генератор простых чисел из набора инструментов Mathomatic.

Для CentOS нет готового пакета, поэтому вам нужно будет собрать его самостоятельно. Загрузите исходный код с http://mathomatic.orgserve.de/mathomatic-16.0.5.tar.bz2, а затем распакуйте файл архива. Перейдите в каталог **mathomatic-16.0.5/primes**. Запустите **make** и **sudo make install**, чтобы собрать и установить двоичные файлы. Теперь у вас будет бинарный файл **matho-primes** в **/usr/local/bin**.

Запустите команду так:

```bash
/usr/local/bin/matho-primes 0 9999999999 > /dev/null &
```

Это создаст список простых чисел от нуля до девяти миллиардов девятьсот девяносто девять миллионов девятьсот девяносто девять тысяч девятьсот девяносто девять. Поскольку мы действительно не хотим сохранять список, вывод перенаправляется в **/dev/null**.

Теперь запустите top, и вы увидите, что процесс **matho-primes** использует весь доступный процессор.

![](/images/YDXs9CYWSHi0tDZReHFI)

Выйдите из **top** (нажмите клавишу q) и завершите процесс **Мато-штрихи** (**fg**, чтобы вывести процесс на передний план, и нажмите CTRL + C).

### nice

The nice command tweaks the priority level of a process so that it runs less frequently. This is useful when you need to run a CPU intensive task as a background or batch job. The niceness level ranges from -20 (most favorable scheduling) to 19 (least favorable). Processes on Linux are started with a niceness of 0 by default. The nice command (without any additional parameters) will start a process with a niceness of 10. At that level the scheduler will see it as a lower priority task and give it less CPU resources.

Start two matho-primes tasks, one with nice and one without:

nice matho-primes 0 9999999999 > /dev/null &
matho-primes 0 9999999999 > /dev/null &
Now run top.

top

Observe that the process started without nice (at niceness level 0) gets more processor time, whereas the process with a niceness level of 10 gets less.

What this means in real terms is that if you want to run a CPU intensive task you can start it using nice and the scheduler will always ensure that other tasks have priority over it. This means that the server (or desktop) will remain responsive even when under heavy load.

Nice has an associated command called renice. It changes the niceness level of an already running process. To use it, find out the PID of process hogging all the CPU time (using ps) and then run renice:

renice +10 1234
Where 1234 is the PID.

Donâ€™t forget to kill the matho-primes processes once you have finished experimenting with the nice and renice commands.

cpulimit
The cpulimit tool curbs the CPU usage of a process by pausing the process at different intervals to keep it under the defined ceiling. It does this by sending SIGSTOP and SIGCONT signals to the process. It does not change the nice value of the process, instead it monitors and controls the real-world CPU usage.

cpulimit is useful when you want to ensure that a process doesn't use more than a certain portion of the CPU. The disadvantage over nice is that the process can't use all of the available CPU time when the system is idle.

To install it on CentOS type:

wget -O cpulimit.zip https://github.com/opsengine/cpulimit/archive/master.zip
unzip cpulimit.zip
cd cpulimit-master
make
sudo cp src/cpulimit /usr/bin
The commands above will download the source code from GitHub, unpack the archive file, build the binary, and copy it to /usr/bin.

cpulimit is used in a similar way to nice, however you need to explicitly define the maximum CPU limit for the process using the ‘-l’ parameter. For example:

cpulimit -l 50 matho-primes 0 9999999999 > /dev/null &
top

Note how the matho-primes process is now only using 50% of the available CPU time. On my example system the rest of the time is spent in idle.

You can also limit a currently running process by specifying its PID using the‘-p’  parameter. For example

cpulimit -l 50 -p 1234
Where 1234 is the PID of the process.

cgroups
Control groups (cgroups) are a Linux kernel feature that allows you to specify how the kernel should allocate specific resources to a group of processes. With cgroups you can specify how much CPU time, system memory, network bandwidth, or combinations of these resources can be used by the processes residing in a certain group.

The advantage of control groups over nice or cpulimit is that the limits are applied to a set of processes, rather than to just one. Also, nice or cpulimit only limit the CPU usage of a process, whereas cgroups can limit other process resources.

By judiciously using cgroups the resources of entire subsystems of a server can be controlled. For example in CoreOS, the minimal Linux distribution designed for massive server deployments, the upgrade processes are controlled by a cgroup. This means the downloading and installing of system updates doesn't affect system performance.

To demonstrate cgroups, we will create two groups with different CPU resources allocated to each group. The groups will be called "cpulimited" and "lesscpulimited"

The groups are created with the cgcreate command like this:

sudo cgcreate -g cpu:/cpulimited
sudo cgcreate -g cpu:/lesscpulimited
The â€œ-g cpuâ€ part of the command tell cgroups that the groups can place limits on the amount of CPU resources given to the processes in the group. Other contollers include cpuset, memory, and blkio. The cpuset controller is related to the cpu controller in that it allows the processes in a group to be bound to a specific CPU, or set of cores in a CPU.

The cpu controller has a property known as cpu.shares. It is used by the kernel to determine the share of CPU resources available to each process across the cgroups. The default value is 1024. By leaving one group (lesscpulimited) at the default of 1024 and setting the other (cpulimited) to 512, we are telling the kernel to split the CPU resources using a 2:1 ratio.

To set the cpu.shares to 512 in the cpulimited group, type:

sudo cgset -r cpu.shares=512 cpulimited
To start a task in a particular cgroup you can use the cgexec command. To test the two cgroups, start matho-primes in the cpulimited group, like this:

sudo cgexec -g cpu:cpulimited /usr/local/bin/matho-primes 0 9999999999 > /dev/null &
If you run top you will see that the process is taking all of the available CPU time.

top

This is because when a single process is running, it uses as much CPU as necessary, regardless of which cgroup it is placed in. The CPU limitation only comes into effect when two or more processes compete for CPU resources.

Now start a second matho-primes process, this time in the lesscpulimited group:

sudo cgexec -g cpu:lesscpulimited /usr/local/bin/matho-primes 0 9999999999 > /dev/null &
The top command shows us that the process in the cgroup with the greater cpu.shares value is getting more CPU time.

top

Now start another matho-primes process in the cpulimited group:

sudo cgexec -g cpu:cpulimited /usr/local/bin/matho-primes 0 9999999999 > /dev/null &

"https://s3-us-west-1.amazonaws.com/scout-blog/cpu<emusageblog/image04.jpg"/>

Observe how the CPU is still being proportioned in a 2:1 ratio. Now the two matho-primes tasks in the cpulimited group are sharing the CPU equally, while the process in the other group still gets more processor time.
**********
[centos](/tags/centos.md)
[nice](/tags/nice.md)
[cpulimit](/tags/cpulimit.md)
