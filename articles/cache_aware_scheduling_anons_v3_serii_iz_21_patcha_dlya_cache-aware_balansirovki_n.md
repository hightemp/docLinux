# Cache Aware Scheduling: анонс v3-серии из 21 патча

Источник: [Cache Aware Scheduling — анонс v3 серии из 21 патча для cache-aware балансировки нагрузки в планировщике Linux: потоки одного процесса группируются в общем LLC-домене для снижения cache bouncing и cache misses; приведены результаты тестов на Intel Sapphire Rapids и AMD Genoa.](https://lwn.net/Articles/1058288/)

**From** : |  | Tim Chen <tim.c.chen-AT-linux.intel.com>
---|---|---
**To** : |  | Peter Zijlstra <peterz-AT-infradead.org>, Ingo Molnar <mingo-AT-redhat.com>, K Prateek Nayak <kprateek.nayak-AT-amd.com>, "Gautham R . Shenoy" <gautham.shenoy-AT-amd.com>, Vincent Guittot <vincent.guittot-AT-linaro.org>
**Subject** : |  | [PATCH v3 00/21] Cache Aware Scheduling
**Date** : |  | Tue, 10 Feb 2026 14:18:40 -0800
**Message-ID** : |  | <cover.1770760558.git.tim.c.chen@linux.intel.com>
**Cc** : |  | Tim Chen <tim.c.chen-AT-linux.intel.com>, Juri Lelli <juri.lelli-AT-redhat.com>, Dietmar Eggemann <dietmar.eggemann-AT-arm.com>, Steven Rostedt <rostedt-AT-goodmis.org>, Ben Segall <bsegall-AT-google.com>, Mel Gorman <mgorman-AT-suse.de>, Valentin Schneider <vschneid-AT-redhat.com>, Madadi Vineeth Reddy <vineethr-AT-linux.ibm.com>, Hillf Danton <hdanton-AT-sina.com>, Shrikanth Hegde <sshegde-AT-linux.ibm.com>, Jianyong Wu <jianyong.wu-AT-outlook.com>, Yangyu Chen <cyy-AT-cyyself.name>, Tingyin Duan <tingyin.duan-AT-gmail.com>, Vern Hao <vernhao-AT-tencent.com>, Vern Hao <haoxing990-AT-gmail.com>, Len Brown <len.brown-AT-intel.com>, Aubrey Li <aubrey.li-AT-intel.com>, Zhao Liu <zhao1.liu-AT-intel.com>, Chen Yu <yu.chen.surf-AT-gmail.com>, Chen Yu <yu.c.chen-AT-intel.com>, Adam Li <adamli-AT-os.amperecomputing.com>, Aaron Lu <ziqianlu-AT-bytedance.com>, Tim Chen <tim.c.chen-AT-linux.intel.com>, Josh Don <joshdon-AT-google.com>, Gavin Guo <gavinguo-AT-igalia.com>, Qais Yousef <qyousef-AT-layalina.io>, Libo Chen <libchen-AT-purestorage.com>, linux-kernel-AT-vger.kernel.org
**Archive-link** : |  | [Article](https://lwn.net/ml/all/cover.1770760558.git.tim.c.chen@linux.intel.com/)

Эта серия патчей вводит инфраструктуру для балансировки нагрузки с учётом кэша (cache-aware load balancing) с целью совместного размещения задач, разделяющих общие данные, в рамках одного домена кэша последнего уровня (Last Level Cache, LLC). Улучшая локальность кэша, планировщик может снизить количество миграций кэш-линий между ядрами (cache bouncing) и промахов кэша (cache misses), что в итоге повышает эффективность доступа к данным. Дизайн построен на основе первоначального прототипа Питера [1].

В этой начальной реализации потоки (threads) в рамках одного процесса рассматриваются как сущности, которые с высокой вероятностью разделяют данные. При балансировке нагрузки планировщик пытается, по мере возможности, объединять такие потоки в одном LLC-домене.

Большая часть замечаний, полученных на v2, была учтена. Обсуждалась идея группировки задач с использованием механизмов, отличных от принадлежности к процессу. Хотя мы согласны, что более гибкая группировка желательна, эта серия намеренно сосредоточена на том, чтобы сначала заложить базовую группировку на основе процессов; альтернативные механизмы группировки будут исследованы в последующей серии. В качестве шага в этом направлении статистика планирования с учётом кэша была вынесена из структуры mm в новую структуру sched_cache_stats. Благодарим за множество полезных отзывов на LPC 2025 и по v2 — мы хотели бы создать отдельную ветку обсуждения, чтобы обсудить возможные пользовательские интерфейсы.

Алгоритмы балансировки нагрузки в целом остались неизменными. Основные изменения в v3 таковы:

1. Планирование с учётом кэша пропускается после повторных неудач балансировки нагрузки (до cache_nice_tries попыток). Это позволяет избежать повторных попыток cache-aware-миграций, когда ни одна из перемещаемых задач не предпочитает LLC-домен назначения.

2. Самая загруженная очередь выполнения (runqueue) больше не сортируется для отбора задач, предпочитающих LLC-домен назначения. Эта сортировка была затратной, а эквивалентного поведения можно добиться, пропуская задачи, которые не предпочитают LLC-домен назначения, во время cache-aware-миграций.

3. Вычисление LLC ID теперь использует данные sched_domain_topology_level напрямую, что упрощает получение идентификаторов.

4. Учёт количества задач, предпочитающих каждый LLC, теперь ведётся в домене планирования нижнего уровня для каждого CPU. Это упрощает обработку изменения размера LLC и изменения числа LLC-доменов.

Результаты тестов:

Серия патчей была применена и протестирована на v6.19-rc3.
См.: <https://github.com/timcchen1298/linux/commits/cache_aware_v3>

Первая тестовая платформа — двухсокетный Intel Sapphire Rapids с 30 ядрами на сокет. Чередование DRAM (DRAM interleaving) включено в BIOS, так что фактически это один узел NUMA с двумя кэшами последнего уровня. С каждым кэшем последнего уровня связано 60 CPU.

Вторая тестовая платформа — AMD Genoa. В ней 4 узла (Node) и 32 CPU на узел. Каждый узел имеет 2 блока CCX, и в каждом CCX — 16 CPU.

hackbench/schbench/netperf/stream/stress-ng/chacha20 были запущены на обеих платформах.

[TL;DR]

Sapphire Rapids:
hackbench показывает значительное улучшение, когда число различных активных потоков ниже вместимости LLC. schbench показывает общее улучшение задержки пробуждения (wakeup latency). ChaCha20-xiangshan (симулятор RISC-V) показывает хорошее улучшение пропускной способности. Для netperf/stream/stress-ng по Hmean заметной разницы не наблюдалось.

Genoa:
Значительное улучшение в hackbench наблюдается, когда число активных потоков меньше числа CPU в пределах одного LLC. На v2 Аарон сообщал об улучшении hackbench/redis в недогруженной системе. ChaCha20-xiangshan показывает огромное улучшение пропускной способности. Phoronix протестировал v1 и показал хорошие улучшения более чем в 30 случаях [2]. Для netperf/stream/stress-ng по Hmean заметной разницы не наблюдалось.

Подробности:

Из-за ограничений на объём данные, не показавшие существенной разницы с базовым вариантом, не приводятся.

Sapphire Rapids:

[hackbench pipe]

```text
case                    load            baseline(std%)  compare%( std%)
threads-pipe-2          1-groups         1.00 (  3.19)  +29.06 (  3.31)*
threads-pipe-2          2-groups         1.00 (  9.61)  +19.19 (  0.55)*
threads-pipe-2          4-groups         1.00 (  6.69)  +15.02 (  1.34)*
threads-pipe-2          8-groups         1.00 (  1.83)  +25.59 (  1.46)*
threads-pipe-4          1-groups         1.00 (  3.41)  +28.63 (  1.17)*
threads-pipe-4          2-groups         1.00 ( 15.62)  +19.51 (  0.82)
threads-pipe-4          4-groups         1.00 (  0.19)  +27.05 (  0.74)*
threads-pipe-4          8-groups         1.00 (  4.32)   +5.64 (  3.18)
threads-pipe-8          1-groups         1.00 (  0.44)  +24.68 (  0.49)*
threads-pipe-8          2-groups         1.00 (  2.03)  +23.76 (  0.52)*
threads-pipe-8          4-groups         1.00 (  3.77)   +7.16 (  1.58)
threads-pipe-8          8-groups         1.00 (  4.53)   +6.88 (  2.36)
threads-pipe-16         1-groups         1.00 (  1.71)  +28.46 (  0.68)*
threads-pipe-16         2-groups         1.00 (  4.25)   -0.23 (  0.97)
threads-pipe-16         4-groups         1.00 (  0.64)   -0.95 (  3.74)
threads-pipe-16         8-groups         1.00 (  1.23)   +1.77 (  0.31)
```

Примечание: количество fd в hackbench по умолчанию изменено с 20 на различные значения, чтобы потоки помещались в один LLC, особенно на системах AMD. Например, для «threads-pipe-8, 2-groups» количество fd равно 8 и создаются 2 группы.

[schbench]

99-й перцентиль задержки пробуждения показывает общее улучшение, тогда как 99-й перцентиль задержки запросов демонстрирует некоторое увеличение вариативности между запусками (run-to-run variance). Логика планирования с учётом кэша, сканирующая все онлайн-CPU для поиска самого горячего LLC, может быть первопричиной возросшей задержки запросов: она задерживает возврат задачи в пользовательское пространство из-за затратной task_cache_work(). Эту проблему предполагается смягчить ограничением сканирования ограниченным набором узлов NUMA [3]; это исправление планируется интегрировать после того, как текущая версия будет доведена до надлежащего состояния.

```text
99th Wakeup Latencies	Base (mean±std)      Compare (mean±std)   Change
--------------------------------------------------------------------------------
thread = 2		13.33(1.15)          13.00(1.73)          +2.48%
thread = 4		12.33(1.53)          9.67(1.53)           +21.57%
thread = 8		10.00(0.00)          10.67(0.58)          -6.70%
thread = 16		10.00(1.00)          9.33(0.58)           +6.70%
thread = 32		10.33(0.58)          9.67(1.53)           +6.39%
thread = 64		10.33(0.58)          9.33(1.53)           +9.68%
thread = 128		12.67(0.58)          12.00(0.00)          +5.29%

run-to-run variance regress at 1 messager + 8 worker:
Request Latencies 99.0th  3981.33(260.16)    4877.33(1880.57)     -22.51%
```

[chacha20]

Время сокращено на 20%

Genoa:

[hackbench pipe]

Количество fd по умолчанию равно 20, что превышает число CPU в одном LLC. Поэтому fd был установлен равным 2, 4, 8 и 16 соответственно. Если исключить результаты с большой вариативностью между запусками, в недогруженной системе наблюдается улучшение на 20–50%:

```text
case                    load            baseline(std%)  compare%( std%)
threads-pipe-2          1-groups         1.00 (  4.04)  +47.22 (  4.77)*
threads-pipe-2          2-groups         1.00 (  5.04)  +33.79 (  8.92)*
threads-pipe-2          4-groups         1.00 (  5.82)   +5.93 (  7.97)
threads-pipe-2          8-groups         1.00 ( 16.15)   -4.11 (  6.85)
threads-pipe-4          1-groups         1.00 (  7.28)  +50.43 (  2.39)*
threads-pipe-4          2-groups         1.00 ( 10.77)   -4.31 (  7.71)
threads-pipe-4          4-groups         1.00 ( 11.16)   +8.12 ( 11.21)
threads-pipe-4          8-groups         1.00 ( 12.79)  -10.10 ( 12.92)
threads-pipe-8          1-groups         1.00 (  5.57)   -1.50 (  6.55)
threads-pipe-8          2-groups         1.00 ( 10.72)   +0.69 (  6.38)
threads-pipe-8          4-groups         1.00 (  7.04)  +19.70 (  5.58)*
threads-pipe-8          8-groups         1.00 (  7.11)  +27.46 (  2.34)*
threads-pipe-16         1-groups         1.00 (  2.86)  -12.82 (  8.97)
threads-pipe-16         2-groups         1.00 (  8.55)   +2.96 (  1.65)
threads-pipe-16         4-groups         1.00 (  5.12)  +20.49 (  5.33)*
threads-pipe-16         8-groups         1.00 (  3.23)   +9.06 (  2.87)
```

[chacha20]

```text
baseline:
Host time spent: 51432ms

sched_cache:
Host time spent: 28664ms
```

Время сокращено на 45%

[1] [https://lore.kernel.org/all/cover.1760206683.git.tim.c.chen@linux.intel.com/](https://lore.kernel.org/all/cover.1760206683.git.tim.c.chen@linux.intel.com/)
[2] [https://www.phoronix.com/review/cache-aware-scheduling-amd-turin](https://www.phoronix.com/review/cache-aware-scheduling-amd-turin)
[3] [https://lore.kernel.org/all/865b852e3fdef6561c9e0a5be9a94aec8a68cdea.1760206683.git.tim.c.chen@linux.intel.com/](https://lore.kernel.org/all/865b852e3fdef6561c9e0a5be9a94aec8a68cdea.1760206683.git.tim.c.chen@linux.intel.com/)

История изменений:

**Изменения в v3:**

1. Планирование с учётом кэша пропускается после повторных неудач балансировки нагрузки (до cache_nice_tries попыток). Это позволяет избежать повторных попыток cache-aware-миграций, когда ни одна из перемещаемых задач не предпочитает LLC-домен назначения.

2. Самая загруженная очередь выполнения больше не сортируется для отбора задач, предпочитающих LLC-домен назначения. Эта сортировка была затратной, а эквивалентного поведения можно добиться, пропуская задачи, которые не предпочитают LLC-домен назначения, во время cache-aware-миграций.

3. Учёт количества задач, предпочитающих каждый LLC, теперь ведётся в домене планирования нижнего уровня для каждого CPU. Это упрощает обработку изменения размера LLC и изменения числа LLC-доменов.

4. Остальные изменения относительно v2 подробно описаны в журнале изменений каждого патча.

**Изменения в v2:**

ссылка на v2: [https://lore.kernel.org/all/cover.1764801860.git.tim.c.chen@linux.intel.com/](https://lore.kernel.org/all/cover.1764801860.git.tim.c.chen@linux.intel.com/)

1. Согласование NUMA-балансировки и кэш-аффинности путём приоритизации NUMA-балансировки, когда их решения расходятся.

2. Динамическое изменение размера структур статистики для каждого LLC в зависимости от размера LLC.

3. Переход на непрерывное пространство LLC-ID, чтобы эти идентификаторы можно было напрямую использовать как индексы массива для статистики LLC.

4. Добавлены поясняющие комментарии.

5. Добавлены 3 отладочных патча (не предназначены для включения).

6. Прочие изменения, учитывающие отзывы на обзор серии патчей v1 (см. журналы изменений отдельных патчей).

**v1**

ссылка на v1: [https://lore.kernel.org/all/cover.1760206683.git.tim.c.chen@linux.intel.com/](https://lore.kernel.org/all/cover.1760206683.git.tim.c.chen@linux.intel.com/)

```text
Chen Yu (10):
  sched/cache: Record per LLC utilization to guide cache aware
    scheduling decisions
  sched/cache: Introduce helper functions to enforce LLC migration
    policy
  sched/cache: Make LLC id continuous
  sched/cache: Disable cache aware scheduling for processes with high
    thread counts
  sched/cache: Avoid cache-aware scheduling for memory-heavy processes
  sched/cache: Enable cache aware scheduling for multi LLCs NUMA node
  sched/cache: Allow the user space to turn on and off cache aware
    scheduling
  sched/cache: Add user control to adjust the aggressiveness of
    cache-aware scheduling
  -- DO NOT APPLY!!! -- sched/cache/debug: Display the per LLC occupancy
    for each process via proc fs
  -- DO NOT APPLY!!! -- sched/cache/debug: Add ftrace to track the load
    balance statistics

Peter Zijlstra (Intel) (1):
  sched/cache: Introduce infrastructure for cache-aware load balancing

Tim Chen (10):
  sched/cache: Assign preferred LLC ID to processes
  sched/cache: Track LLC-preferred tasks per runqueue
  sched/cache: Introduce per CPU's tasks LLC preference counter
  sched/cache: Calculate the percpu sd task LLC preference
  sched/cache: Count tasks prefering destination LLC in a sched group
  sched/cache: Check local_group only once in update_sg_lb_stats()
  sched/cache: Prioritize tasks preferring destination LLC during
    balancing
  sched/cache: Add migrate_llc_task migration type for cache-aware
    balancing
  sched/cache: Handle moving single tasks to/from their preferred LLC
  sched/cache: Respect LLC preference in task migration and detach
```

```text
 fs/proc/base.c                 |   31 +
 include/linux/cacheinfo.h      |   21 +-
 include/linux/mm_types.h       |   43 ++
 include/linux/sched.h          |   32 +
 include/linux/sched/topology.h |    8 +
 include/trace/events/sched.h   |   79 +++
 init/Kconfig                   |   11 +
 init/init_task.c               |    3 +
 kernel/fork.c                  |    6 +
 kernel/sched/core.c            |   11 +
 kernel/sched/debug.c           |   55 ++
 kernel/sched/fair.c            | 1088 +++++++++++++++++++++++++++++++-
 kernel/sched/sched.h           |   44 ++
 kernel/sched/topology.c        |  194 +++++-
 14 files changed, 1598 insertions(+), 28 deletions(-)
```

**********

[kernel](/tags/kernel.md)
[linux](/tags/linux.md)
[cpu](/tags/cpu.md)