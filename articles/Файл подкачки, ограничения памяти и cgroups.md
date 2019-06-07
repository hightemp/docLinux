# Файл подкачки, ограничения памяти и cgroups

https://jvns.ca/blog/2017/02/17/mystery-swap/

This week there was a bug at work, and I learned something new about memory & swap & cgroups!

Understanding how memory usage works has been an ongoing project for a while – back in December, I wrote [How much memory is my process using?](https://jvns.ca/blog/2016/12/03/how-much-memory-is-my-process-using-/) which explains how memory works on Linux.

So I felt surprised and worried yesterday when something was happening with memory on Linux that I didn’t understand! Here’s the situation and why I was confused:

We had some machines running builds. They were swapping. They had say 30GB of RAM in total. 15GB was being used by some processes and 15GB by the filesystem cache. I was really confused about why these machines were swapping, because – I know about memory! If 15GB of memory is being used by the filesystem cache, the OS can always free that memory! There’s no reason to swap!

I then learned about the “swappiness” setting, and that if “swappiness” is high, then the OS is more likely to swap, even if it doesn’t absolutely need to. We tried setting `sysctl vm.swappiness=1`, which lets you tell the operating system “no, really, please don’t swap, just take memory away from the filesystem cache instead”. The machine continued to swap. I was confused.

After a while, we turned off swap and things got worse. Some processes started being OOM killed. (the OOM killer on Linux will kill processes if you run out of memory) But why? The boxes had free memory, didn’t they? In my head I had an axiom “if a computer has free memory, there is no reason the processes on it should get OOM killed”. Obviously there was something I did not understand.

I finally looked at the output of `dmesg` (which is how you see messages the Linux kernel prints about what it’s up to) to understand why the processes were being OOM killed. And then there was this magic word:`cgroups`. Everything became clear pretty quickly:

*   the processes that were being killed were in a cgroup (which we talked about back in this [namespaces & groups](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/) post)
*   cgroups can have **memory limits**, which are like “you are only allowed to use 15GB of memory otherwise your processes will get killed by the OOM killer”
*   and this memory limit was the reason the processes were being killed even though there was free memory!

### swap + cgroup memory limits = a little surprising

My model of memory limits on cgroups was always “if you use more than X memory, you will get killed right away”. It turns out that that assumptions was wrong! If you use more than X memory, you can still use swap!

And apparently some kernels also support setting separate swap limits. So you could set your memory limit to X and your swap limit to 0, which would give you more predictable behavior. Swapping is weird and confusing.

Anyway, we found out through all this that the processes in question had recently started using much more memory for very understandable reasons, and rolled back that change, and everything made sense again.

And more importantly than everything making sense, the build system was happy again.

### does swap even make sense?

It’s not completely clear to me under what circumstances having swap on a computer at all even makes sense. It seems like swap has some role on desktop computers.

I am not sure though if any of the servers we operate benefit by having swap enabled? This seems like it would be a good thing to understand.

Like I hear the advice “no, just always turn off swap, it will be better overall” a lot and maybe that is the right thing! I think the reason that swap is considered bad in production systems is that it has weird/unpredictable effects and predictability is good.

Somewhat relately, this [swap insanity](https://blog.jcole.us/2010/09/28/mysql-swap-insanity-and-the-numa-architecture/)article looks really interesting.

### understanding memory models is cool

I learned

*   the vm.swappiness exists and you can use it to make a machine more or less likely to swap
*   that when Linux OOM kills a process in a cgroup (“container”), it actually prints a bunch of very useful stuff about the memory usage of everything else in the cgroup at the time. I should remember to look at dmesg earlier on!

It’s really important to me to understand what’s happening on the computers that I work with – when something happens like “this computer is swapping and I don’t know WHY” it bothers me a lot.

Now if I ever see a process mysteriously swapping hopefully I will remember about memory limits!

**********
[swap](/tags/swap.md)
