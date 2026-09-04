# Linux cgroup с нуля

Источник: [Linux cgroup from first principles](https://fzakaria.com/2025/05/26/linux-cgroup-from-first-principles)

26 мая 2025 · 6 мин чтения

Проведя добрую часть двух недель за изучением концепции cgroup (control group, групп управления) в Linux, я решил, что лучше записать это для следующего отважного исследователя. 🦸

> [Микросайт Facebook про cgroup2](https://facebookmicrosites.github.io/cgroup2/docs/overview.html) — тоже замечательный ресурс. Настоятельно рекомендую его прочитать 🤓.

Давайте погрузимся и изучим _cgroup_, в частности _cgroup v2_.

Между реализациями cgroup v2 и v1 есть различия. Однако v2 была представлена в ядре Linux 4.5 в 2016 году. Она включала гораздо более простой дизайн, поэтому для упрощения этого руководства мы будем считать её единственной версией [[ref]](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/diff/Documentation/cgroup-v2.txt?id=v4.5&id2=v4.4).

> Кстати, что мне нравится в Linux, так это философия дизайна Unix — _«всё является файлом»_. Она пронизывает всё в Linux, особенно то, как взаимодействовать с различными подсистемами ядра.
>
> Хотя инструменты и библиотеки более высокого уровня часто абстрагируют эти прямые манипуляции с файлами, если вы можете делать `read` и `write` в файл — вы можете общаться с ядром! 📜

Группы управления Linux — это своего рода контейнер, в который можно помещать процессы и применять разнообразные ограничения на выделение ресурсов, такие как: память, CPU и пропускная способность сети.

Мы будем использовать следующую виртуальную машину NixOS для сборки и запуска этого руководства, если хотите повторять за мной.

vm.nix

```nix
let
  # release-24.11
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/5ef6c425980847c78a80d759abc476e941a9bf42.tar.gz";
  nixos = import "${nixpkgs}/nixos" {
    configuration = {
      modulesPath,
      pkgs,
      ...
    }: {
      imports = [
        (modulesPath + "/virtualisation/qemu-vm.nix")
      ];

      virtualisation = {
        graphics = false;
      };

      users.users.alice = {
        isNormalUser = true;
        extraGroups = ["wheel"];
        packages = with pkgs; [
          file
          libcgroup
          vim
          (pkgs.runCommandCC "throttled"{
              src = pkgs.writeText "throttled.c" ''
              #include <stdio.h>
              #include <stdlib.h>
              #include <unistd.h>
              #include <time.h>

              static long long now_ns() {
                  struct timespec ts;
                  clock_gettime(CLOCK_MONOTONIC, &ts);
                  return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
              }

              int main() {
                  long long last = now_ns();
                  int count = 0;

                  while (1) {
                      count++;
                      if (count % 1000000 == 0) {
                          long long current = now_ns();
                          long long delta_ms = (current - last) / 1000000;
                          printf("Delta: %lld ms\n", delta_ms);
                          fflush(stdout);
                          last = current;
                      }
                  }
                  return 0;
              }
              '';
            } ''
              mkdir -p $out/bin
              $CC -o $out/bin/throttled $src
            '')
          (pkgs.runCommandCC "hog" {
              src = pkgs.writeText "hog.c" ''
                #include <stdlib.h>
                #include <stdio.h>
                #include <unistd.h>
                #include <string.h>

                int main() {
                    while (1) {
                        char *mem = malloc(1024 * 1024);
                        if (!mem) {
                            perror("malloc");
                            break;
                        }
                        memset(mem, 1, 1024 * 1024);
                        printf("1 MB allocated\n");
                        fflush(stdout);
                        sleep(1);
                    }
                    return 0;
                }
              '';
            } ''
              mkdir -p $out/bin
              $CC -o $out/bin/hog $src
            '')
        ];
        initialPassword = "";
      };
      security.sudo.wheelNeedsPassword = false;
      services.getty.autologinUser = "alice";

      system.stateVersion = "24.11";
    };
  };
in
  nixos.vm
```

Хотя один `cgroup` может накладывать несколько ограничений на ресурсы, мы будем делать это по одному за раз для простоты.

Все `cgroup` живут внутри специального каталога `/sys/fs/cgroup`, который называется _корневой cgroup_ (root cgroup).

Вы можете посмотреть текущий cgroup своей оболочки входа в систему, заглянув в `/proc/self/cgroup`

Возвращаемое значение — это то, что нужно добавить к корню.

```text
> cat /proc/self/cgroup
0::/user.slice/user-1000.slice/session-5.scope

> file /sys/fs/cgroup/user.slice/user-1000.slice/session-5.scope
/sys/fs/cgroup/user.slice/user-1000.slice/session-5.scope: directory
```

> Если вас смущают _slice_ и _scope_ в этом пути — просто игнорируйте 🤔. Это концепции `systemd`, помогающие организовать cgroup.

Давайте создадим простую иерархию, которую мы хотим, в учебных целях.

На практике вы, скорее всего, будете создавать эти группы, чтобы моделировать бизнес-домен или различные процессы, которые хотите сгруппировать вместе, а не контроллеры, которые хотите выразить.

```text
/sys/fs/cgroup
└── demo/
    ├── cpu-limited/
    ├── memory-limited/
    └── network-limited/
```

Поскольку «всё является файлом» — мантра нашего Linux API, давайте просто сделаем `mkdir` для групп.

```bash
sudo mkdir /sys/fs/cgroup/demo
sudo chown -R $USER /sys/fs/cgroup/demo
mkdir /sys/fs/cgroup/demo/cpu-limited
mkdir /sys/fs/cgroup/demo/memory-limited
mkdir /sys/fs/cgroup/demo/network-limited
```

Если мы заглянем внутрь одного cgroup, то увидим кучу виртуальных файлов.

```text
ls -1 /sys/fs/cgroup/demo | head
cgroup.controllers
cgroup.events
cgroup.freeze
cgroup.kill
cgroup.max.depth
cgroup.max.descendants
cgroup.subtree_control
...
memory.low
memory.max
memory.min
memory.numa_stat
memory.oom.group
memory.peak
...
network-limited
pids.current
pids.events
pids.max
pids.peak
```

Некоторые из этих файлов помогают задавать значения различных контроллеров, например `memory.max`, который задаёт абсолютный совокупный максимум памяти, которую могут выделить все процессы, привязанные к этому cgroup или любому из его потомков.

Другие файлы дают вам живую учётную информацию или события, например `memory.current` или `memory.events`.

Все файлы, начинающиеся с `cgroup`, помогают настроить cgroup и включить/выключить различные контроллеры.

`cgroup.controllers`

```text
This file will list all the active controllers enabled on this cgroup.
```

`cgroup.subtree_control`

```text
This file lists the controllers that are enabled and available to the descendants.
```

Изначально наш `cgroup.subtree_control` для `/sys/fs/cgroup/demo` пуст. Это значит, что если вы посмотрите на любой дочерний cgroup, например `/sys/fs/cgroup/demo/cpu-limited`, в нём будет отсутствовать куча файлов.

```text
> cat /sys/fs/cgroup/demo/cgroup.subtree_control
# empty
> cat /sys/fs/cgroup/demo/cpu-limited/cgroup.controllers
# empty
```

Давайте включим различные контроллеры.

```text
> echo "+memory +io +cpu" > /sys/fs/cgroup/demo/cgroup.subtree_control

> cat /sys/fs/cgroup/demo/cgroup.subtree_control
cpu io memory

> cat /sys/fs/cgroup/demo/cpu-limited/cgroup.controllers
cpu io memory
```

Мы можем изменить cgroup процесса, записав его _pid_ в файл `cgroup.procs`.

```text
> sleep infinity &
1055
> echo 1055 | sudo tee /sys/fs/cgroup/demo/memory-limited/cgroup.procs
1055
>  ps -o cgroup 1055
CGROUP
0::/demo/memory-limited
```

Почему пришлось использовать `sudo`, хотя ранее вы сделали `chown`? 🤔

Когда я запустил `sleep`, он находился в том же cgroup, что и моя оболочка входа. Процессам разрешено перемещать в другие cgroup процессы других сторон, только если у них есть право записи для общего предка между ними. Единственный общий предок между ними — это `/sys/fs/cgroup`, и у нашего пользователя нет права записи на него.

Почему бы не записать _pid_ в `/sys/fs/cgroup/demo` вместо дочерней группы?

Существует _«ограничение отсутствия внутренних процессов»_ (no internal process constraint), которое гласит, что cgroup может иметь либо дочерние cgroup, либо процессы, **но не то и другое одновременно** (за исключением корня).

Давайте напишем небольшую программу на C, бесконечно пожирающую память.

hog.c

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    while (1) {
        char *mem = malloc(1024 * 1024);
        if (!mem) {
            perror("malloc");
            break;
        }
        memset(mem, 1, 1024 * 1024);
        printf("1 MB allocated\n");
        fflush(stdout);
        sleep(1);
    }
    return 0;
}
```

> 😲 Наша программа должна обязательно делать `memset` в 1, а не в 0. Я обнаружил, что либо компилятор, либо ядро имеет оптимизации для страниц, заполненных нулями, и новой памяти на самом деле не выделялось.

Мы ограничим процессы в нашей группе `demo/memory-limited` до 5 МиБ.

```text
> echo "5242880" > /sys/fs/cgroup/demo/memory-limited/memory.max

> cat /sys/fs/cgroup/demo/memory-limited/memory.max
5242880
```

Теперь запустим `hog` в cgroup. Мы будем использовать инструмент `cgexec`, который берёт на себя порождение процесса в нужном cgroup — это избавляет нас от необходимости записывать себя в файл `cgroup.procs`.

```text
> sudo cgexec -g memory:demo/memory-limited hog
1 MB allocated
1 MB allocated
1 MB allocated
1 MB allocated
[  128.648590] Memory cgroup out of memory: Killed process 895 (hog)
total-vm:7716kB, anon-rss:4992kB, file-rss:1024kB,
shmem-rss:0kB, UID:0 pgtables:48kB oom_score_adj:0
Killed
```

Мы только что применили наше первое ограничение ресурсов 😊.

Давайте сделаем ещё один интересный пример. Ограничим программу, чтобы она работала на CPU только 10% времени.

Это может быть очень полезно, если вы хотите воспроизвести, каковы эффекты работы на перегруженной (oversubscribed) машине.

Напишем простую программу, которая выполняет некоторую _нагрузочную работу_ и выводит временные дельты каждые 1000000 итераций.

throttled.c

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

static long long now_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

int main() {
    long long last = now_ns();
    int count = 0;

    while (1) {
        count++;
        if (count % 1000000 == 0) {
            long long current = now_ns();
            long long delta_ms = (current - last) / 1000000;
            printf("Delta: %lld ms\n", delta_ms);
            fflush(stdout);
            last = current;
        }
    }
    return 0;
}
```

Если бы мы запустили эту программу обычным образом, мы могли бы увидеть следующее:

```text
> throttled  | head
Delta: 0 ms
Delta: 1 ms
Delta: 0 ms
Delta: 0 ms
Delta: 0 ms
Delta: 1 ms
Delta: 0 ms
Delta: 1 ms
Delta: 0 ms
Delta: 0 ms
```

Теперь применим ограничение CPU, говорящее, что в пределах 100 мс (100000 мкс) процессы внутри cgroup могут использовать только 1 мс (1000 мкс) — выделение 1% CPU.

```text
> echo "1000 100000" > /sys/fs/cgroup/demo/cpu-limited/cpu.max

> cat /sys/fs/cgroup/demo/cpu-limited/cpu.max
1000 100000
```

Давайте снова используем `cgexec` с нашей программой `throttled` и посмотрим на разницу.

```text
> sudo cgexec -g cpu:demo/cpu-limited throttled
Delta: 0 ms
Delta: 5 ms
Delta: 99 ms
Delta: 0 ms
Delta: 99 ms
Delta: 99 ms
Delta: 99 ms
Delta: 100 ms
Delta: 99 ms
Delta: 199 ms
Delta: 0 ms
```

Отлично — теперь у нас есть способ легко ограничивать задачи, которые могут неоправданно прожорливы к CPU 😈.

Хотя мы применяли эти ограничения к одиночным процессам, та же концепция применима и к нескольким процессам. Установленные значения действуют для всех потомков дерева в конкретном cgroup.

Группы управления — превосходный способ обеспечить дополнительный слой изоляции рабочей нагрузки от остальной системы, а также отличную ручку для тестирования производительности в патологических условиях.

Хотя поначалу они кажутся пугающими, элегантность философии _«всё является файлом»_ делает их на удивление доступными, как только начинаешь экспериментировать.

Мы также получили пользу, игнорируя сложность, которую systemd часто добавляет сверху — иногда приятно работать с сырыми файлами и понимать основы 🙃.

Одно улучшение, которое я хотел бы видеть: когда вы сталкиваетесь с недопустимым условием — например, нарушением ограничения _«без внутренних процессов»_ — вы остаётесь с расплывчатой ошибкой файлового ввода-вывода (например, _Device or resource busy_). Было бы замечательно, если бы ядро могло предлагать более полезные сообщения об ошибках или подсказки в `dmesg` 💡.

**********

[cgroup](/tags/cgroup.md)
[linux](/tags/linux.md)
[kernel](/tags/kernel.md)