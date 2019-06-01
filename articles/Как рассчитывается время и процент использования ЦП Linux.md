# Как рассчитывается время и процент использования ЦП Linux

### Overview

CPU time is allocated in discrete time slices (ticks). For a certain number of time slices, the cpu is busy, other times it is not (which is represented by the idle process). In the picture below the CPU is busy for 6 of the 10 CPU slices. 6/10 = .60 = 60% of busy time (and there would therefore be 40% idle time).

![](/images/3b036987b148a55b2e46e60aa3364470)

Note: A tick(cycle) is the time it takes to send a single pulse. A pulse consists of a high voltage followed by a low voltage. There can be billions of ticks per second depending on the frequency(GHz) of the CPU clock.

You can get the number of CPU ticks since boot from /proc/stat

```
 cat /proc/stat
     user nice system idle iowait  irq  softirq steal guest guest_nice
cpu  4705 356  584    3699   23    23     0       0     0          0

```

*   user: normal processes executing in user mode
*   nice: niced processes executing in user mode
*   system: processes executing in kernel mode
*   idle: twiddling thumbs
*   iowait: waiting for I/O to complete
*   irq: servicing interrupts
*   softirq: servicing softirqs
*   steal: involuntary wait
*   guest: running a normal guest
*   guest\_nice: running a niced guest

### Formula

To calculate Linux CPU usage time subtract the idle CPU time from the total CPU time as follows:

**Total CPU time since boot**\= user+nice+system+idle+iowait+irq+softirq+steal

**Total CPU Idle time since boot**\= idle + iowait

**Total CPU usage time since boot**\= Total CPU time since boot - Total CPU Idle time since boot

**Total CPU percentage**\= Total CPU usage time since boot/Total CPU time since boot X 100

If you use the formula on the example data above you should get a Linux CPU usage Percentage of 60%.

Note: Guest and Guest\_nice are already accounted in user and nice, hence they are not included in the total calculation

For real time CPU usage, you will need to calculate the time between two intervals.

Below is an example of a Bash Script by Paul Colby that does this

```
    #!/bin/bash
    # by Paul Colby (http://colby.id.au), no rights reserved ;)

    PREV_TOTAL=0
    PREV_IDLE=0

    while true; do
      # Get the total CPU statistics, discarding the 'cpu ' prefix.
      CPU=(`sed -n 's/^cpu\s//p' /proc/stat`)
      IDLE=${CPU[3]} # Just the idle CPU time.

      # Calculate the total CPU time.
      TOTAL=0
      for VALUE in "${CPU[@]}"; do
        let "TOTAL=$TOTAL+$VALUE"
      done

      # Calculate the CPU usage since we last checked.
      let "DIFF_IDLE=$IDLE-$PREV_IDLE"
      let "DIFF_TOTAL=$TOTAL-$PREV_TOTAL"
      let "DIFF_USAGE=(1000*($DIFF_TOTAL-$DIFF_IDLE)/$DIFF_TOTAL+5)/10"
      echo -en "\rCPU: $DIFF_USAGE%  \b\b"

      # Remember the total and idle CPU times for the next check.
      PREV_TOTAL="$TOTAL"
      PREV_IDLE="$IDLE"

      # Wait before checking again.
      sleep 1
    done

```

Ref[https://www.kernel.org/doc/Documentation/filesystems/proc.txt](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)section 1.8

[https://github.com/pcolby/scripts/blob/master/cpu.sh](https://github.com/pcolby/scripts/blob/master/cpu.sh)

[http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux](http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux)

[http://serverfault.com/questions/648704/how-are-cpu-time-and-cpu-usage-the-same](http://serverfault.com/questions/648704/how-are-cpu-time-and-cpu-usage-the-same)

[http://www.webopedia.com/TERM/C/clock\_tick.html](http://www.webopedia.com/TERM/C/clock_tick.html)

[http://www.pcworld.com/article/221559/cpu.html](http://www.pcworld.com/article/221559/cpu.html)

[http://stackoverflow.com/questions/16726779/how-do-i-get-the-total-cpu-usage-of-an-application-from-proc-pid-stat](http://stackoverflow.com/questions/16726779/how-do-i-get-the-total-cpu-usage-of-an-application-from-proc-pid-stat)

[http://www.ask.com/technology/many-times-system-clock-tick-per-second-1-ghz-processor-b9028ab0b0de7883](http://www.ask.com/technology/many-times-system-clock-tick-per-second-1-ghz-processor-b9028ab0b0de7883)

[https://github.com/torvalds/linux/blob/master/fs/proc/stat.c](https://github.com/torvalds/linux/blob/master/fs/proc/stat.c)