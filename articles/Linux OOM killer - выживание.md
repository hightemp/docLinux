# Linux OOM killer - выживание

When your Linux machine runs out of memory, **Out of Memory (OOM) killer** is called by kernel to free some memory. It is often encountered on servers which have a number of memory intensive processes running. In this post, we dig a little deeper into when does OOM killer get called, how it decides which process to kill and if we can prevent it from killing important processes like databases.

### How does OOM Killer choose which process to kill?

The Linux kernel gives a score to each running process called `oom_score` which shows how likely it is to be terminated in case of low available memory. The score is proportional to the amount of memory used by the process. The score is `10 x percent of memory used by process` . So the maximum score is 100% x 10 = 1000. In addition, if a process is running as a **privileged user** , it gets a **slightly lower oom\_score** as compared to same memory usage by a normal user process. In earlier versions of Linux ( v2.6.32 kernel), there was a more elaborate heuristic which calculated this score.

The `oom_score` of a process can be found in the `/proc` directory. Let's say that the process id (pid) of your process is 42, `cat /proc/42/oom_score` will give you the process' score.

### Can I ensure some important processes do not get killed by OOM Killer?

Yes! The OOM killer checks `oom_score_adj` to adjust its final calculated score. This file is present in `/proc/$pid/oom_score_adj` . You can add a large negative score to this file to ensure that your process gets a lower chance of being picked and terminated by OOM killer. The `oom_score_adj` can vary from -1000 to 1000. If you assign -1000 to it, it can use 100% memory and still avoid getting terminated by OOM killer. On the other hand, if you assign 1000 to it, the Linux kernel will keep killing the process even when it uses minimal memory.

Let's go back to our process with pid 42. Here is how you can change its `oom_score_adj` :

```console
$ sudo echo -200 > /proc/42/oom_score_adj
```

We need to do this as `root` user or `sudo` because Linux does not allow normal users to reduce the OOM score. You can increase the OOM score as a normal user without any special permissions. e.g `echo 100 > /proc/42/oom_score_adj` 

There is also another, less fine-grained score called `oom_adj` which varies from -16 to 15. It is similar to `oom_score_adj` . In fact, when you set `oom_score_adj` , the kernel automatically scales it down and calculates `oom_adj` . `oom_adj` has a magic value of -17 which indicates that the given process should never be killed by OOM killer.

### Display OOM scores of all running processes

This script displays the OOM score and OOM adjusted score of all running processes, in descending order of OOM score

```bash
#!/bin/bash
# Displays running processes in descending order of OOM score
printf 'PID\tOOM Score\tOOM Adj\tCommand\n'
while read -r pid comm; do [ -f /proc/$pid/oom_score ] && [ $(cat /proc/$pid/oom_score) != 0 ] && printf '%d\t%d\t\t%d\t%s\n' "$pid" "$(cat /proc/$pid/oom_score)" "$(cat /proc/$pid/oom_score_adj)" "$comm"; done < <(ps -e -o pid= -o comm=) | sort -k 2nr
```

### Check if any of your processes have been OOM-killed

The easiest way is to `grep` your system logs. In Ubuntu: `grep -i kill /var/log/syslog` . If a process has been killed, you may get results like `my_process invoked oom-killer: gfp_mask=0x201da, order=0, oom_score_adj=0` 

### Caveats of adjusting OOM scores

Remember that OOM is a symptom of a bigger problem - low available memory. The best way to solve it is by either increasing the available memory (e.g better hardware) or moving some programs to other machines or by reducing memory consumption of programs (e.g allocate less memory where possible).

Too much tweaking of the OOM adjusted score will result in random processes getting killed and not being able to free enough memory.

### References

1.   [proc](http://man7.org/linux/man-pages/man5/proc.5.html) man page
2.   [https://askubuntu.com/questions/60672/how-do-i-use-oom-score-adj/](https://askubuntu.com/questions/60672/how-do-i-use-oom-score-adj/) 
3.   [Walkthrough](https://linux-mm.org/OOM_Killer) on which part of Linux code is called
4.  Classic [LWN article](https://lwn.net/Articles/317814/) (a bit dated)
5.   [Invoking the OOM killer manually](https://www.lynxbee.com/how-to-invoke-oom-killer-manually-for-understanding-which-process-gets-killed-first/)

**********
[OOM killer](/tags/OOM%20killer.md)
