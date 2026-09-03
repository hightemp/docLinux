# Как работает clock_gettime

Источник: [How does clock_gettime work](https://linuxmogeb.blogspot.com/2013/10/how-does-clockgettime-work.html)

29 октября 2013

clock_gettime — функция, которая, как следует из названия, возвращает время. На архитектурах x86 у clock_gettime есть реализация в VDSO. VDSO — сегмент разделяемой памяти между ядром и каждым пользовательским приложением. Он позволяет ядру экспортировать функции в userspace так, чтобы процессы пользовательского пространства могли использовать их без накладных расходов на системный вызов.

clock_gettime() принимает два аргумента: первый — идентификатор требуемых часов, второй — указатель на переменную struct timespec, в которую будут записаны значения. struct timespec — просто структура с двумя полями: tv_sec для секунд и tv_nsec для наносекунд:

```c
struct timespec {
    __kernel_time_t tv_sec;     /* секунды */
    long    tv_nsec;    /* наносекунды */
};
```

Примечание: основной фокус этой заметки — идентификаторы часов CLOCK_MONOTONIC и CLOCK_REALTIME, поскольку именно эти часы использует трассировщик LTTng для простановки временных меток на записываемые события.

## CLOCK_REALTIME и CLOCK_MONOTONIC

clock_gettime() возвращает время относительно определённой точки отсчёта — некоего события в прошлом. Главное различие между CLOCK_MONOTONIC и CLOCK_REALTIME в Linux — именно эта точка отсчёта.

CLOCK_REALTIME даёт «реальное время» — то есть настенное время, как на часах на вашей руке. Точка отсчёта — эпоха, определяемая как 1 января 1970 года. Если вызвать:

```c
clock_gettime(CLOCK_REALTIME, &ts);
```

в момент написания этой заметки, будут возвращены следующие значения:

```text
ts.tv_sec = 1383065479, ts.tv_nsec = 750367192.
```

Если перевести количество секунд в годы (поделив на 3600, затем на 24, затем на 365.25), получим 43.82. Это значит, что с эпохи до момента вызова clock_gettime(CLOCK_REALTIME, &ts) прошло 43.82 года. Это также значит, что если я вручную изменю часы (или дату) системы, это отразится на значении, возвращаемом clock_gettime(CLOCK_REALTIME, &ts). То же верно для изменений времени со стороны NTP. Таким образом, время часов CLOCK_REALTIME не монотонно: оно не обязательно возрастает и может прыгать вперёд и назад.

Это подводит нас ко второму идентификатору — CLOCK_MONOTONIC. Эти часы, как можно догадаться, обновляются строго монотонно. Другими словами, последовательные чтения этих часов безусловно дают возрастающие значения; эти часы не могут вернуться назад во времени, даже если я изменю системные часы. Точка отсчёта — время загрузки системы. Заметим, что это особенность Linux, а не всех POSIX-систем. clock_gettime(CLOCK_MONOTONIC, &ts) возвращает время, прошедшее с загрузки системы. Если вызвать:

```c
clock_gettime(CLOCK_MONOTONIC, &ts);
```

я получу следующие значения:

```text
ts.tv_sec = 103941, ts.tv_nsec = 959414826
```

то есть моя Linux-система загрузилась 103941/3600 = 28.8 часов назад. Понятно, почему такая точка отсчёта гарантирует монотонность: прошедшее с загрузки время не зависит от настенных часов. Если я изменю системные часы, значение CLOCK_MONOTONIC всё так же будет относительно времени загрузки, которое не изменилось.

Итак, CLOCK_MONOTONIC лучше подходит для упорядочивания событий в рамках сессии, тогда как CLOCK_REALTIME — когда нужно абсолютное время. LTTng использует монотонные часы для простановки меток на события в трассировке. Однако поскольку настенное время полезнее, LTTng сохраняет разницу между CLOCK_REALTIME и CLOCK_MONOTONIC в начале трассировки в файл метаданных. Когда трассировка завершена, преобразование от времени загрузки к абсолютному выполняется прибавлением этого значения ко всем записанным меткам.

## Реализация VDSO

Теперь посмотрим на исходный код реализации clock_gettime() в VDSO в файле arch/x86/vdso/vclock_gettime.c из дерева исходников ядра:

```c
notrace int __vdso_clock_gettime(clockid_t clock, struct timespec *ts)
{
    int ret = VCLOCK_NONE;

    switch (clock) {
    case CLOCK_REALTIME:
        ret = do_realtime(ts);
        break;
    case CLOCK_MONOTONIC:
        ret = do_monotonic(ts);
        break;
    case CLOCK_REALTIME_COARSE:
        return do_realtime_coarse(ts);
    case CLOCK_MONOTONIC_COARSE:
        return do_monotonic_coarse(ts);
    }

    if (ret == VCLOCK_NONE)
        return vdso_fallback_gettime(clock, ts);
    return 0;
}
```

Этот код просто вызывает функцию времени, соответствующую запрошенному идентификатору часов. Предположим, мы запросили CLOCK_MONOTONIC — взглянем на функцию do_monotonic() из того же файла:

```c
notrace static int do_monotonic(struct timespec *ts)
{
    unsigned long seq;
    u64 ns;
    int mode;

    ts->tv_nsec = 0;
    do {
        seq = read_seqcount_begin(&gtod->seq);
        mode = gtod->clock.vclock_mode;
        ts->tv_sec = gtod->monotonic_time_sec;
        ns = gtod->monotonic_time_snsec;
        ns += vgetsns(&mode);
        ns >>= gtod->clock.shift;
    } while (unlikely(read_seqcount_retry(&gtod->seq, seq)));
    timespec_add_ns(ts, ns);

    return mode;
}
```

Как видно, всё, что делает эта функция, — «заполняет» структуру ts, переданную параметром, текущими значениями tv_sec и tv_nsec. Цикл do-while — просто схема синхронизации, которую пока можно игнорировать.

ts->tv_sec устанавливается из gtod->monotonic_time_sec, а ts->tv_nsec — из gtod->monotonic_time_snsec плюс значения, возвращённого vgetsns(), для более высокой точности. gtod — просто структура, заменяющая фактические значения, хранящиеся в ядре и недоступные процессам userspace. Поэтому значения в gtod нужно регулярно обновлять. Это обновление происходит в update_vsyscall(struct timekeeper *tk) из файла arch/x86/kernel/vsyscall_64.c:

```c
void update_vsyscall(struct timekeeper *tk)
{
    struct vsyscall_gtod_data *vdata = &vsyscall_gtod_data;

    write_seqcount_begin(&vdata->seq);

    /* copy vsyscall data */
    [...]

    vdata->monotonic_time_sec = tk->xtime_sec      // (1)
              + tk->wall_to_monotonic.tv_sec;
    vdata->monotonic_time_snsec = tk->xtime_nsec   // (2)
              + (tk->wall_to_monotonic.tv_nsec
                << tk->shift);
    while (vdata->monotonic_time_snsec >=
          (((u64)NSEC_PER_SEC) << tk->shift)) {
        vdata->monotonic_time_snsec -=
          ((u64)NSEC_PER_SEC) << tk->shift;
        vdata->monotonic_time_sec++;
    }

    [...]

    write_seqcount_end(&vdata->seq);
}
```

В (1) устанавливается monotonic_time_sec, в (2) — monotonic_time_snsec. Это и есть значения, «экспортируемые» в userland через структуру vsyscall_gtod_data. Немного покопавшись в исходниках ядра, можно понять, как и когда обновляется эта структура.

В зависимости от частоты «тиков» (см. CONFIG_HZ):

```text
Hardware timer interrupt (generated by the Programmable Interrupt Timer - PIT)
-> tick_periodic();
  -> do_timer(1);
    -> update_wall_time();
      -> timekeeping_update(tk, false);
        -> update_vsyscall(tk);
```

Или (на «безтиковых» ядрах — см. CONFIG_NO_HZ):

```text
smp_apic_timer_interrupt()
  -> irq_enter()
    -> tick_check_idle()
      -> tick_check_nohz()
        -> tick_nohz_update_jiffies()
          -> tick_do_update_jiffies64()
            -> do_timer(ticks) // ex: ticks = 1344
              -> update_wall_time();
                -> timekeeping_update(tk, false);
                  -> update_vsyscall(tk);
```

Подводя итог: clock_gettime() возвращает значения, регулярно обновляемые, плюс интерполяцию для большей точности наносекунд. Как часто обновляются эти значения? Просто при прерываниях таймера.

**********

[vDSO](/tags/vdso.md)
[время](/tags/time.md)
[ядро](/tags/kernel.md)
[Linux](/tags/linux.md)