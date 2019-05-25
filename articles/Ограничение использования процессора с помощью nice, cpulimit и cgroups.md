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

Команда **nice** настраивает уровень приоритета процесса, чтобы он выполнялся реже. Это полезно, когда вам нужно запустить задачу с интенсивным использованием процессора в качестве фонового или пакетного задания. Уровень привлекательности варьируется от -20 (наиболее благоприятный график) до 19 (наименее благоприятный). Процессы в Linux по умолчанию запускаются со значением 0. Команда **nice** (без каких-либо дополнительных параметров) запустит процесс с изящностью 10. На этом уровне планировщик увидит его как задачу с более низким приоритетом и даст ему меньше ресурсов ЦП.

Запустите две задачи с простыми числами: одно с хорошим и одно без:

```bash
nice matho-primes 0 9999999999 > /dev/null &
matho-primes 0 9999999999 > /dev/null &
```

Теперь запустите **топ**.

![](/images/noOl6isSjiqS6ImxiLvm)

Заметьте, что процесс, запущенный без **nice** (на уровне 0), получает больше процессорного времени, а процесс с уровнем 10 - меньше.

В реальном выражении это означает, что если вы хотите запустить задачу, интенсивно использующую процессор, вы можете запустить ее, используя команду **nice**, и планировщик всегда будет гарантировать, что другие задачи имеют приоритет над ней. Это означает, что сервер (или настольный компьютер) будет реагировать даже при большой нагрузке.

У **nice** есть связанная команда, называемая **renice**. Это изменяет уровень привлекательности уже запущенного процесса. Чтобы его использовать, узнайте PID процесса, занимающего все процессорное время (используя **ps**), а затем запустите renice:

```bash
renice +10 1234
```

Где 1234 - это PID.

Не забудьте убить процессы **matho-primes**, как только вы закончите экспериментировать с командами **nice** и **renice**.

### cpulimit

Инструмент **cpulimit** ограничивает использование процессором процесса, останавливая процесс через различные интервалы времени, чтобы удерживать его под определенным потолком. Это делается путем отправки сигналов **SIGSTOP** и **SIGCONT** процессу. Он не меняет полезную ценность процесса, он контролирует и контролирует реальное использование процессора.

**cpulimit** полезен, когда вы хотите убедиться, что процесс использует не более определенной части процессора. Недостатком по сравнению с **nice** является то, что процесс не может использовать все доступное время процессора, когда система простаивает.

Чтобы установить его на CentOS типа:

```bash
wget -O cpulimit.zip https://github.com/opsengine/cpulimit/archive/master.zip
unzip cpulimit.zip
cd cpulimit-master
make
sudo cp src/cpulimit /usr/bin
```

Приведенные выше команды загрузят исходный код из GitHub, распакуют файл архива, соберут двоичный файл и скопируют его в **/usr/bin**.

**cpulimit** используется аналогично **nice**, однако вам нужно явно определить максимальное ограничение ЦП для процесса, используя параметр «-l». Например:

```bash
cpulimit -l 50 matho-primes 0 9999999999 > /dev/null &
```

![](/images/ZGPMohnLTFmYshntAepX)

Обратите внимание, что процесс **matho-primes** теперь использует только 50% доступного процессорного времени. В моем примере система все остальное время проводит в режиме ожидания.

Вы также можете ограничить запущенный в данный момент процесс, указав его PID с помощью параметра «-p». Например

```bash
cpulimit -l 50 -p 1234
```

Где 1234 - PID процесса.

### cgroups

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
[cgroups](/tags/cgroups.md)
