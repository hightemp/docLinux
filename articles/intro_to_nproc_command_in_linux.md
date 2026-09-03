# Введение в команду nproc в Linux

Источник: [Intro To 'nproc' Command In Linux](https://blog.robertelder.org/intro-to-nproc-command/)

Robert Elder · 15 июля 2023

Я использую команду `nproc`, чтобы узнать, сколько процессоров у моей машины:

```bash
nproc
```

## Типовой сценарий

На моей машине `nproc` выводит значение 8:

```text
8
```

Я могу посмотреть содержимое `/proc/cpuinfo`, чтобы узнать модель CPU, и сверить значение 8 с официальной документацией моего процессора:

```bash
cat /proc/cpuinfo | grep 'model name'
```

Как видно выше, мой CPU — 'i5-10300H', и [документация подтверждает](https://ark.intel.com/content/www/us/en/ark/products/201839/intel-core-i510300h-processor-8m-cache-up-to-4-50-ghz.html), что 8 — действительно число логических ядер моего компьютера. Однако число физических ядер CPU — 4.

## Опции и переменные окружения

Значение, возвращаемое `nproc`, может зависеть от двух переменных окружения:

```bash
OMP_NUM_THREADS=999 nproc
```

```text
999
```

```bash
OMP_THREAD_LIMIT=7 nproc
```

```text
7
```

А также от флага `all`:

```bash
OMP_THREAD_LIMIT=7 nproc --all
```

```text
8
```

и флага `ignore`:

```bash
OMP_THREAD_LIMIT=7 nproc --all --ignore=5
```

```text
3
```

В отличие от многих других команд, `nproc` не входит в [стандарт POSIX](https://ru.wikipedia.org/wiki/POSIX). В [реализации `nproc` в GNU coreutils](https://github.com/coreutils/gnulib/blob/752f97e9afb770ea3cb6017d0b8e52600b045d6a/lib/nproc.c) видно, что для каждой платформы, на которой может работать `nproc`, используется свой набор системных вызовов. Различные программные платформы или настройки BIOS могут влиять на возвращаемое значение. Более того, такие концепции, как [гипертрейдинг](https://ru.wikipedia.org/wiki/Hyper-threading), или функции энергосбережения ещё больше усложняют точный подсчёт ядер CPU.

И именно поэтому `nproc` — моя любимая команда Linux.

**********

[nproc](/tags/nproc.md)
[Linux](/tags/linux.md)