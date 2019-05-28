# Производительность Linux

hi-res: observability + static + perf-tools/bcc ([svg](http://www.brendangregg.com/Perf/linux_perf_tools_full.svg))  
[![](/images/linux_perf_tools_full_1000.jpg)](http://www.brendangregg.com/Perf/linux_perf_tools_full.png)  
slides: observability  
[![](/images/linux_observability_tools.png)](http://www.brendangregg.com/Perf/linux_observability_tools.png)  
slides: static, benchmarking, tuning  
[![](/images/linux_static_tools_333.png)](http://www.brendangregg.com/Perf/linux_static_tools.png)[![](/images/linux_benchmarking_tools_333.png)](http://www.brendangregg.com/Perf/linux_benchmarking_tools.png)[![](/images/linux_tuning_tools_333.png)](http://www.brendangregg.com/Perf/linux_tuning_tools.png)  
sar,[perf-tools](https://github.com/brendangregg/perf-tools#contents),[bcc/BPF](https://github.com/iovisor/bcc#tools):  
[![](/images/linux_observability_sar_333.png)](http://www.brendangregg.com/Perf/linux_observability_sar.png)[![](/images/perf-tools_2016_333.png)](http://www.brendangregg.com/Perf/perf-tools_2016.png)[![](/images/bcc_tracing_tools_2016_333.png)](http://www.brendangregg.com/Perf/bcc_tracing_tools.png)  
Лицензия на изображения: Creative Commons [Attribution-ShareAlike 4.0](http://creativecommons.org/licenses/by-sa/4.0/).  

Эта страница содержит ссылки на различные материалы о производительности Linux, которые я создал, включая карты инструментов справа. Первая - это высококачественная версия, сочетающая в себе наблюдаемость, статическую настройку производительности и perf-tools/bcc (см. [Обсуждение](https://www.reddit.com/r/linux/comments/4x4smu/linux_performance_tools_full_version_draft/)). Остальные были предназначены для использования в слайд-колодах и имеют более крупные шрифты и стрелки, и показывают: [Инструменты наблюдения Linux](http://www.brendangregg.com/Perf/linux_observability_tools.png), [Инструменты тестирования Linux](http://www.brendangregg.com/Perf/linux_benchmarking_tools.png), [Инструменты настройки Linux](http://www.brendangregg.com/Perf/linux_tuning_tools.png) и [Linux sar](http://www.brendangregg.com/Perf/linux_observability_sar). Еще больше диаграмм смотрите в моих слайдах ниже.

## Инструменты

*   [perf\_events](http://www.brendangregg.com/perf.html): Перфорированные строки, примеры, визуализации.
*   [eBPF tools](http://www.brendangregg.com/ebpf.html): Инструменты трассировки eBPF и примеры с ОЦК.
*   [perf-tools](https://github.com/brendangregg/perf-tools): Инструменты анализа перфорации с использованием ftrace (github).
*   [bcc](https://github.com/iovisor/bcc#tools): Инструменты анализа перфорации с использованием eBPF (github).
*   [ktap](http://www.brendangregg.com/ktap.html): однострочники, примеры и сценарии.
*   [Flame Graphs](http://www.brendangregg.com/flamegraphs.html): с помощью [perf](http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html#perf),[SystemTap](http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html#SystemTap), а также [ktap](http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html#ktap).

## Документация

*   [Анализ производительности Linux за 60 000 миллисекунд](http://techblog.netflix.com/2015/11/linux-performance-analysis-in-60s.html) показывает первые десять команд, которые будут использоваться в расследовании ([видео](http://www.brendangregg.com/blog/2015-12-03/linux-perf-60s-video.html), [PDF](http://www.brendangregg.com/Articles/Netflix_Linux_Perf_Analysis_60s.pdf)), Написано мной и командой инженеров по производительности в Netflix (2015).
*   Мой пост [Настройка производительности экземпляров Linux на ЕС2](http://www.brendangregg.com/blog/2015-03-03/performance-tuning-linux-instances-on-ec2.html) включает в себя используемые нами переменные на Netflix (2015).
*   Пост в [Средняя загрузка Linux: разгадывание тайны](http://www.brendangregg.com/blog/2017-08-08/linux-load-averages.html), объясняющий, что они из себя представляют и почему они включают в себя состояние сна (2017).
*   [Полный пример отладки gdb (учебник)](http://www.brendangregg.com/blog/2016-08-09/gdb-example-ncurses.html), включая использование некоторых инструментов perf/отладка (2016).
*   Генерация графиков пламени в Linux с использованием perf & eBPF:
	* [Графики пламени CPU](http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html#Linux)
	* [Графики пламени вне процессора](http://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html#Linux)
	* [Графики пламени памяти](http://www.brendangregg.com/FlameGraphs/memoryflamegraphs.html#Linux)
*   Посты о eBPF, bcc и bpftrace (2015-8):
	* [Linux eBPF](http://www.brendangregg.com/blog/2015-05-15/ebpf-one-small-step.html) (2015)
	* [bcc: Укрощение Linux 4.3+ Tracing Superpowers](http://www.brendangregg.com/blog/2015-09-22/bcc-linux-4.3-tracing.html)
	* [tcpconnect и tcpaccept для Linux (bcc)](http://www.brendangregg.com/blog/2015-10-31/tcpconnect-tcpaccept-bcc.html)
	* [Отслеживание стека eBPF в Linux (скрытая копия)](http://www.brendangregg.com/blog/2016-01-18/ebpf-stack-trace-hack.html) (2016)
	* [График пламени вне процессора CPU Linux (bcc)](http://www.brendangregg.com/blog/2016-01-20/ebpf-offcpu-flame-graph.html)
	* [Linux Wakeup и Off-Wake Profiling (bcc)](http://www.brendangregg.com/blog/2016-02-01/linux-wakeup-offwake-profiling.html)
	* [Прототип графа цепочек Linux (bcc)](http://www.brendangregg.com/blog/2016-02-05/ebpf-chaingraph-prototype.html)
	* [Linux eBPF / bcc uprobes](http://www.brendangregg.com/blog/2016-02-08/linux-ebpf-bcc-uprobes.html)
	* [Linux BPF / bcc Road Ahead](http://www.brendangregg.com/blog/2016-03-28/linux-bpf-bcc-road-ahead-2016.html)
	* [Ubuntu Xenial bcc / BPF](http://www.brendangregg.com/blog/2016-06-14/ubuntu-xenial-bcc-bpf.html)
	* [Linux bcc / BPF Отслеживание возможностей безопасности](http://www.brendangregg.com/blog/2016-10-01/linux-bcc-security-capabilities.html)
	* [Трассировка медленного запроса Linux MySQL с помощью bcc / BPF](http://www.brendangregg.com/blog/2016-10-04/linux-bcc-mysqld-qslower.html)
	* [Linux bcc / BPF ext4 Отслеживание задержки](http://www.brendangregg.com/blog/2016-10-06/linux-bcc-ext4dist-ext4slower.html)
	* [Задержка запуска очереди Linux (bcc / BPF) (планировщик)](http://www.brendangregg.com/blog/2016-10-08/linux-bcc-runqlat.html)
	* [Linux bcc / BPF Node.js Трассировка USDT](http://www.brendangregg.com/blog/2016-10-12/linux-bcc-nodejs-usdt.html)
	* [Linux bcc tcptop](http://www.brendangregg.com/blog/2016-10-15/linux-bcc-tcptop.html)
	* [Эффективный профилировщик на основе BPF в Linux 4.9](http://www.brendangregg.com/blog/2016-10-21/linux-efficient-profiler.html)
	* [DTrace для Linux 2016](http://www.brendangregg.com/blog/2016-10-27/dtrace-for-linux-2016.html)
	* [Инструменты трассировки Linux 4.x: Использование сверхдержав BPF](http://www.slideshare.net/brendangregg/linux-4x-tracing-tools-using-bpf-superpowers) 
	* [Linux bcc/BPF tcplife: TCP Lifespans](http://www.brendangregg.com/blog/2016-11-30/linux-bcc-tcplife.html)  
	* [Golang bcc/BPF Function Tracing](http://www.brendangregg.com/blog/2017-01-31/golang-bcc-bpf-function-tracing.html) (2017)  
	* [7 BPF tools for performance analysis on Fedora](https://opensource.com/article/17/11/bccbpf-performance)  
	* [TCP Tracepoints](http://www.brendangregg.com/blog/2018-03-22/tcp-tracepoints.html) (2018)  
	* [Linux bcc/eBPF tcpdrop](http://www.brendangregg.com/blog/2018-05-31/linux-tcpdrop.html)  
	* [bpftrace (DTrace 2.0) for Linux 2018](http://www.brendangregg.com/blog/2018-10-08/dtrace-for-linux-2018.html)  
    
*   В моей статье [lwn.net](http://lwn.net/) [Ftrace: скрытый выключатель света](http://lwn.net/Articles/608497/) показан пример использования Linux ftrace (август 2014 г.) ).
*   Сообщения о Perf-инструментах на основе ftrace (2014-5):
    [iosnoop для Linux](http://www.brendangregg.com/blog/2014-07-16/iosnoop-for-linux.html), [тепловые карты задержки iosnoop](http://www.brendangregg.com/ blog / 2014-07-23 / linux-iosnoop-latency-heat-maps.html), [opensnoop для Linux](http://www.brendangregg.com/blog/2014-07-25/opensnoop-for-linux .html), [execsnoop для Linux](http://www.brendangregg.com/blog/2014-07-28/execsnoop-for-linux.html), [ftrace: скрытый выключатель света](http: // www.brendangregg.com/blog/2014-08-30/ftrace-the-hidden-light-switch.html), [tcpretrans](http://www.brendangregg.com/blog/2014-09-06/linux -ftrace-ТСР-ретранслировать-tracing.html)
    [Коэффициент попадания в кэш страниц] (http://www.brendangregg.com/blog/2014-12-31/linux-page-cache-hit-ratio.html), [uprobe: динамическая трассировка на уровне пользователя] (http: //www.brendangregg.com/blog/2015-06-28/linux-ftrace-uprobe.html),[Hacking Linux USDT] (http://www.brendangregg.com/blog/2015-07-03/hacking -linux-USDT-ftrace.html)
*   Posts about perf-based perf-tools:[perf Hacktogram](http://www.brendangregg.com/blog/2014-07-10/perf-hacktogram.html).
*   Posts about perf\_events (2014-7):
    [perf CPU Sampling](http://www.brendangregg.com/blog/2014-06-22/perf-cpu-sample.html),[perf Static Tracepoints](http://www.brendangregg.com/blog/2014-06-29/perf-static-tracepoints.html),[perf Heat Maps](http://www.brendangregg.com/blog/2014-07-01/perf-heat-maps.html),[perf Counting](http://www.brendangregg.com/blog/2014-07-03/perf-counting.html),[perf Kernel Line Tracing](http://www.brendangregg.com/blog/2014-09-11/perf-kernel-line-tracing.html),  
    [perf Off-CPU Time Flame Graphs](http://www.brendangregg.com/blog/2015-02-26/linux-perf-off-cpu-flame-graph.html),[Linux Profiling at Netflix](http://www.brendangregg.com/blog/2015-02-27/linux-profiling-at-netflix.html),[Java Mixed-Mode Flame Graphs](http://techblog.netflix.com/2015/07/java-in-flames.html)([PDF](http://www.brendangregg.com/Articles/Netflix_Java_in_Flames.pdf)),[Linux 4.5 perf folded format](http://www.brendangregg.com/blog/2016-04-30/linux-perf-folded.html),  
    [perf sched for Linux CPU scheduler analysis](http://www.brendangregg.com/blog/2017-03-16/perf-sched.html)
*   A page on[Working Set Size Estimation](http://www.brendangregg.com/wss.html)for Linux (2018+).
*   A post on[KPTI/KAISER Meltdown Initial Performance Regressions](http://www.brendangregg.com/blog/2018-02-09/kpti-kaiser-meltdown-performance.html)(2018).
*   In[The PMCs of EC2: Measuring IPC](http://www.brendangregg.com/blog/2017-05-04/the-pmcs-of-ec2.html)I showed the new Performance Monitoring Counter (PMC) support in the AWS EC2 cloud (2017).
*   [CPU Utilization is Wrong](http://www.brendangregg.com/blog/2017-05-09/cpu-utilization-is-wrong.html): a post explaining the growing problem of memory stall cycles dominating the %CPU metric (2017).
*   A post about[Linux 4.7 Hist Triggers](http://www.brendangregg.com/blog/2016-06-08/linux-hist-triggers.html)(2016).
*   The blog post[strace Wow Much Syscall](http://www.brendangregg.com/blog/2014-05-11/strace-wow-much-syscall.html)discusses strace(1) for production use, and compares it to advanced tracing tools (2014).
*   [USE Method: Linux Performance Checklist](http://www.brendangregg.com/USEmethod/use-linux.html); also see the[USE Method](http://www.brendangregg.com/usemethod.html)page for the description of this methodology.
*   [Off-CPU Analysis Method](http://www.brendangregg.com/offcpuanalysis.html), where I demonstrate this methodology on Linux.
*   [Systems Performance: Enterprise and the Cloud](http://www.brendangregg.com/sysperfbook.html)(Prentice Hall, 2013) uses Linux distributions as the primary example.