# Механизмы профилирования Linux

## Kernel tracepoints

Kernel tracepoints — это фреймворк для трассировки ядра, сделанный через статическое инструментирование кода. Да, вы правильно поняли, большинство важных функций ядра (сеть, управление памятью, планировщик) статически инструментировано. На моём ядре количество tracepoint’ов такое:  

```console
$ perf list tracepointt | wc -l
1271
```
  
Среди них есть kmalloc:  

```console
$ perf list tracepoint | grep "kmalloc "
kmem:kmalloc                                       [Tracepoint event]
```
  
А вот так оно выглядит на самом деле в ядерной функции [`__do_kmalloc`](http://lxr.free-electrons.com/source/mm/slab.c?v=3.18#L3481):  

```c++
    /**
     *  __do_kmalloc - allocate memory
     *  @size: how many bytes of memory are required.
     *  @flags: the type of memory to allocate (see kmalloc).
     *  @caller: function caller for debug tracking of the caller
     */
    static __always_inline void *__do_kmalloc(size_t size, gfp_t flags,
                                              unsigned long caller)
    {
            struct kmem_cache *cachep;
            void *ret;
    
            cachep = kmalloc_slab(size, flags);
            if (unlikely(ZERO_OR_NULL_PTR(cachep)))
                    return cachep;
            ret = slab_alloc(cachep, flags, caller);
    
            trace_kmalloc(caller, ret,
                          size, cachep->size, flags);
    
            return ret;
    }
```    

`trace_kmalloc` — это и есть tracepoint.  
  
Такие tracepoint’ы пишут вывод в отладочный кольцевой буфер, который можно посмотреть в /sys/kernel/debug/tracing/trace:  

```console
$ mount -t debugfs none /sys/kernel/debug
$ cd /sys/kernel/debug/tracing/
$ echo 1 > events/kmem/kmalloc/enable 
$ tail trace
bash-10921 [000] .... 1127940.937139: kmalloc: call_site=ffffffff8122f0f5 ptr=ffff8800aaecb900 bytes_req=48 bytes_alloc=64 gfp_flags=GFP_KERNEL
bash-10921 [000] .... 1127940.937139: kmalloc: call_site=ffffffff8122f084 ptr=ffff8800ca008800 bytes_req=2048 bytes_alloc=2048 gfp_flags=GFP_KERNEL|GFP_NOWARN|GFP_NORETRY
bash-10921 [000] .... 1127940.937139: kmalloc: call_site=ffffffff8122f084 ptr=ffff8800aaecbd80 bytes_req=64 bytes_alloc=64 gfp_flags=GFP_KERNEL|GFP_NOWARN|GFP_NORETRY
tail-11005 [001] .... 1127940.937451: kmalloc: call_site=ffffffff81219297 ptr=ffff8800aecf5f00 bytes_req=240 bytes_alloc=256 gfp_flags=GFP_KERNEL|GFP_ZERO
tail-11005 [000] .... 1127940.937518: kmalloc: call_site=ffffffff81267801 ptr=ffff880123e8bd80 bytes_req=128 bytes_alloc=128 gfp_flags=GFP_KERNEL
tail-11005 [000] .... 1127940.937519: kmalloc: call_site=ffffffff81267786 ptr=ffff880077faca00 bytes_req=504 bytes_alloc=512 gfp_flags=GFP_KERNEL
```
  
Заметьте, что traсepoint «kmem:kmalloc», как и все остальные, по умолчанию выключен, так что его надо включить, сказав 1 в его `enable` файл.  
  
Вы можете сами написать tracepoint для своего модуля ядра. Но, во-первых, это не так уж и просто, потому что tracepoint’ы — не самый удобный и понятный API: смотри примеры в [_samples/trace_events/_](http://lxr.free-electrons.com/source/samples/trace_events/?v=3.18)(вообще все эти tracepoint’ы — это чёрная магия C-макросов, понять которые если и сильно захочется, то не сразу получится). А во-вторых, скорее всего, они не заработают в вашем модуле, покуда у вас включен `CONFIG_MODULE_SIG` (почти всегда да) и нет закрытого ключа для подписи (он у вендора ядра вашего дистрибутива). Смотри душераздирающие подробности в lkml [[1]](https://lkml.org/lkml/2014/2/13/488), [[2]](https://lkml.org/lkml/2014/3/4/925). 

Короче говоря, tracepoint’ы простая и легковесная вещь, но пользоваться ей руками неудобно и не рекомендуется — используйте`ftrace`или`perf`.  
  
## kprobes

Если tracepoint’ы — это метки статического инструментирования, то `kprobes` — это механизм динамического инструментирования кода. С помощью kprobes вы можете прервать выполнение ядерного кода в _любом_ месте, вызвать свой обработчик, сделать в нём что хотите и вернуться обратно как ни в чём ни бывало.  
  
Как это делается: вы пишете свой модуль ядра, в котором регистрируете обработчик на определённый символ ядра (читай, функцию) или вообще любой адрес.  
  
Работает это всё следующим образом:  

*   Мы делаем свой модуль ядра, в котором пишем наш обработчик.
*   Мы регистрируем наш обработчик на некий адрес A, будь то просто адрес иликакая-нибудьфункция.
*   Подсистема_kprobe_копирует инструкции по адресу, А и заменяет их на CPU trap (`int 3` для x86).
*   Теперь, когда выполнение кода доходит до адреса A, генерируется исключение, по которому сохраняются регистры, а управление передаётся обработчику исключительной ситуации, коим в конце концов становится _kprobes_.
*   Подсистема _kprobes_ смотрит на адрес исключения, находит, кто был зарегистрирован по адресу, А и вызывает наш обработчик.
*   Когда наш обработчик заканчивается, регистры восстанавливаются, выполняются сохранённые инструкции, и выполнение продолжается дальше.

В ядре есть 3 вида kprobes:  

*   kprobes — «базовая» проба, которая позволяет прервать любое место ядра.
*   jprobes — jump probe, вставляется только в начало функции, но зато даёт удобный механизм доступа к аргументам прерываемой функции для нашего обработчика. Также работает не за счёт trap’ов, а через `setjmp/longjmp` (отсюда и название), то есть более легковесна.
*   kretprobes — return probe, вставляется перед выходом из функции и даёт удобный доступ к результату функции.

С помощью kprobes мы можем трассировать всё что угодно, включая код сторонних модулей. Давайте сделаем это для нашего miscdevice драйвера. Я хочу знать, чтокто-топытается писать в моё устройство, знать по какому отступу и сколько байт.  
В моём miscdevice драйвере функция выглядит так:  

```c++
ssize_t etn_write(struct file *filp, const char __user *buf, 
          size_t count, loff_t *f_pos)
```
  
Я написал [простой jprobe модуль](https://gist.github.com/dzeban/a19c711d6b6b1d72e594), который пишет в ядерный лог количество байт и смещение.  

```console
$ tail -F /var/log/kern.log
Jan  1 00:00:42 etn kernel: [   42.923717] ETN JPROBE: jprobe_init:46: Planted jprobe at bf00f7a8, handler addr bf071000
Jan  1 00:00:43 etn kernel: [   43.194840] ETN JPROBE: trace_etn_write:23: Writing 2 bytes at offset 4
Jan  1 00:00:43 etn kernel: [   43.201827] ETN JPROBE: trace_etn_write:23: Writing 2 bytes at offset 4
```
  
Короче, вещь мощная, однако пользоваться не шибко удобно: доступа к локальным переменным нет (только через отступ от `ebp`), нужно писать модуль ядра, отлаживать, загружатьи т.п. Есть доступные примеры в [_samples/kprobes_](http://lxr.free-electrons.com/source/samples/kprobes/?v=3.18). Но зачем всё это, если есть SystemTap? 

## Perf events
  
Сразу скажу, что не надо путать «perf events» и программу `perf` — про программу будет сказано отдельно.  
  
«Perf events» — это интерфейс доступа к счётчикам в PMU (Performance Monitoring Unit), который является частью CPU. Благодаря этим метрикам, вы можете с легкостью попросить ядро показать вам сколько было промахов в L1 кеше, независимо от того, какая у вас архитектура, будь то ARM или amd64. Правда, для вашего процессора должна быть поддержка в ядре:-) Относительно актуальную информацию по этому поводу можно найти [здесь](http://web.eece.maine.edu/~vweaver/projects/perf_events/support.html).  
  
Для доступа к этим счётчикам, а также к огромной куче другого добра, была написана программа`perf`. С её помощью можно посмотреть, какие железные события нам доступны.  
  
<details><summary><b>Пример для x86</b></summary>
```console
$ perf list pmu hw sw cache
  branch-instructions OR cpu/branch-instructions/    [Kernel PMU event]
  branch-misses OR cpu/branch-misses/                [Kernel PMU event]
  bus-cycles OR cpu/bus-cycles/                      [Kernel PMU event]
  cache-misses OR cpu/cache-misses/                  [Kernel PMU event]
  cache-references OR cpu/cache-references/          [Kernel PMU event]
  cpu-cycles OR cpu/cpu-cycles/                      [Kernel PMU event]
  instructions OR cpu/instructions/                  [Kernel PMU event]


  cpu-cycles OR cycles                               [Hardware event]
  instructions                                       [Hardware event]
  cache-references                                   [Hardware event]
  cache-misses                                       [Hardware event]
  branch-instructions OR branches                    [Hardware event]
  branch-misses                                      [Hardware event]
  bus-cycles                                         [Hardware event]
  ref-cycles                                         [Hardware event]

  cpu-clock                                          [Software event]
  task-clock                                         [Software event]
  page-faults OR faults                              [Software event]
  context-switches OR cs                             [Software event]
  cpu-migrations OR migrations                       [Software event]
  minor-faults                                       [Software event]
  major-faults                                       [Software event]
  alignment-faults                                   [Software event]
  emulation-faults                                   [Software event]
  dummy                                              [Software event]

  L1-dcache-loads                                    [Hardware cache event]
  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-stores                                   [Hardware cache event]
  L1-dcache-store-misses                             [Hardware cache event]
  L1-dcache-prefetches                               [Hardware cache event]
  L1-icache-loads                                    [Hardware cache event]
  L1-icache-load-misses                              [Hardware cache event]
  LLC-loads                                          [Hardware cache event]
  LLC-load-misses                                    [Hardware cache event]
  LLC-stores                                         [Hardware cache event]
  LLC-store-misses                                   [Hardware cache event]
  dTLB-loads                                         [Hardware cache event]
  dTLB-load-misses                                   [Hardware cache event]
  dTLB-stores                                        [Hardware cache event]
  dTLB-store-misses                                  [Hardware cache event]
  iTLB-loads                                         [Hardware cache event]
  iTLB-load-misses                                   [Hardware cache event]
  branch-loads                                       [Hardware cache event]
  branch-load-misses                                 [Hardware cache event]	
```
</details>

<details><summary><b>А вот что на ARM</b></summary>
```console
$ perf list pmu hw sw cache

  cpu-cycles OR cycles                               [Hardware event]
  instructions                                       [Hardware event]
  cache-references                                   [Hardware event]
  cache-misses                                       [Hardware event]
  branch-instructions OR branches                    [Hardware event]
  branch-misses                                      [Hardware event]
  stalled-cycles-frontend OR idle-cycles-frontend    [Hardware event]
  stalled-cycles-backend OR idle-cycles-backend      [Hardware event]
  ref-cycles                                         [Hardware event]

  cpu-clock                                          [Software event]
  task-clock                                         [Software event]
  page-faults OR faults                              [Software event]
  context-switches OR cs                             [Software event]
  cpu-migrations OR migrations                       [Software event]
  minor-faults                                       [Software event]
  major-faults                                       [Software event]
  alignment-faults                                   [Software event]
  emulation-faults                                   [Software event]
  dummy                                              [Software event]

  L1-dcache-loads                                    [Hardware cache event]
  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-stores                                   [Hardware cache event]
  L1-dcache-store-misses                             [Hardware cache event]
  L1-icache-load-misses                              [Hardware cache event]
  dTLB-load-misses                                   [Hardware cache event]
  dTLB-store-misses                                  [Hardware cache event]
  iTLB-load-misses                                   [Hardware cache event]
  branch-loads                                       [Hardware cache event]
  branch-load-misses                                 [Hardware cache event]
```
</details>

Видно, что x86 побогаче будет на такие вещи.  
  
Для доступа к «perf events» был сделан специальный системный вызов [`perf_event_open`](http://web.eece.maine.edu/~vweaver/projects/perf_events/perf_event_open.html), которому вы передаёте сам event и конфиг, в котором описываете, что вы хотите с этим событием делать. В ответ вы получаете файловый дескриптор, из которого можно читать данные, собранные `perf`’ом по событию.  
  
Поверх этого, `perf`предоставляет множество разных фич, вроде группировки событий, фильтрации, вывода в разные форматы, анализа собранных профилей и пр. Поэтому в `perf`сейчас пихают всё, что можно: от tracepoint’ов до [eBPF](https://lwn.net/Articles/643139/) и вплоть до того, что весь `ftrace` хотят сделать частью `perf` [[3]](http://thread.gmane.org/gmane.linux.kernel/1136520)[[4]](https://lkml.org/lkml/2013/10/16/15).  
  
Короче говоря, «perf_events» сами по себе мало интересны, а сам `perf` заслуживает отдельной статьи, поэтому для затравки покажу простой пример.  
  
Говорим:  

```console
$ perf timechart record apt-get update
...
$ perf timechart -i perf.data -o timechart.svg
```
  
И получаем вот такое чудо:  
![Perf timechart](/images/33939ef84fa44053a2c8ab5a20c3cd00.png) 
Perf timechart  
  
## Вывод

Таким образом, зная чуть больше про трассировку и профилирование в ядре, вы можете сильно облегчить жизнь себе и товарищам, особенно если научиться пользоваться настоящими инструментами как `ftrace`, `perf` и `SystemTap`, но об этом в другой раз.  
## Почитать  

*   [https://events.linuxfoundation.org/sites/events/files/slides/kernel_profiling_debugging_tools_0.pdf](https://events.linuxfoundation.org/sites/events/files/slides/kernel_profiling_debugging_tools_0.pdf)
*   [http://events.linuxfoundation.org/sites/events/files/lcjp13_zannoni.pdf](http://events.linuxfoundation.org/sites/events/files/lcjp13_zannoni.pdf)
*   _tracepoints_:
    *   [Documentation/trace/tracepoints.txt](http://lxr.free-electrons.com/source/Documentation/trace/tracepoints.txt?v=3.13)
    *   [http://lttng.org/files/thesis/desnoyers-dissertation-2009-12-v27.pdf](http://lttng.org/files/thesis/desnoyers-dissertation-2009-12-v27.pdf)
    *   [http://lwn.net/Articles/379903/](http://lwn.net/Articles/379903/)
    *   [http://lwn.net/Articles/381064/](http://lwn.net/Articles/381064/)
    *   [http://lwn.net/Articles/383362/](http://lwn.net/Articles/383362/)
*   _kprobes_:
    *   [Documentation/kprobes.txt](http://lxr.free-electrons.com/source/Documentation/kprobes.txt?v=3.13)
    *   [https://lwn.net/Articles/132196/](https://lwn.net/Articles/132196/)
*   _perf_events_:
    *   [http://web.eece.maine.edu/~vweaver/projects/perf_events/](http://web.eece.maine.edu/~vweaver/projects/perf_events/)
    *   [https://lwn.net/Articles/441209/](https://lwn.net/Articles/441209/)