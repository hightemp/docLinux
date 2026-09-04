# ASLR в деталях

Источник: [ASLR In Depth — практический урок о `randomize_va_space`, отображениях `/proc/<pid>/maps` и влиянии PIE на рандомизацию 32- и 64-битных ELF-файлов](https://deepwiki.com/nnamon/linux-exploitation-course/4.5-aslr-in-depth)

Эта страница документирует Урок 8 курса: исследование того, как рандомизация раскладки адресного пространства (Address Space Layout Randomization, ASLR) влияет на запущенные процессы и как позиционно-независимые исполняемые файлы (Position Independent Executables, PIE) взаимодействуют с ASLR. В уроке используются четыре диагностических бинарника, делающие рандомизацию адресов непосредственно наблюдаемой.

Данная страница посвящена пониманию поведения ASLR, а не его обходу. Техники обхода, которые строятся на этом знании, описаны в [Bypassing ASLR/NX with Ret2PLT](/nnamon/linux-exploitation-course/4.6-bypassing-aslrnx-with-ret2plt) и [Bypassing ASLR/NX with GOT Overwrite](/nnamon/linux-exploitation-course/4.7-bypassing-aslrnx-with-got-overwrite). О предпосылках существования ASLR и NX см. [Linux Binary Protections](/nnamon/linux-exploitation-course/4.2-linux-binary-protections).

Соответствующие исходные файлы:

  * [lessons/8_aslr/Makefile](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/Makefile)
  * [lessons/8_aslr/build/1_reveal_addresses](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/build/1_reveal_addresses)
  * [lessons/8_aslr/lessonplan.md](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1)

---

## Параметр ядра `randomize_va_space`

ASLR управляется параметром ядра, доступным через виртуальную файловую систему `procfs` по пути `/proc/sys/kernel/randomize_va_space`.

Значение| Эффект
---|---
`0`| ASLR выключен. Все сегменты (стек, куча, библиотеки, исполняемый файл) загружаются по фиксированным адресам при каждом запуске.
`1`| Частичный ASLR. Стек, VDSO и разделяемые библиотеки рандомизируются; куча — нет.
`2`| Полный ASLR. Стек, куча, разделяемые библиотеки и (если PIE) сам исполняемый файл — всё рандомизируется.

Упражнения урока используют значения `0` и `2`:

```bash
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space   # disable
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space   # full ASLR
```

[lessons/8_aslr/lessonplan.md33-36](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L33-L36)

---

## Четыре диагностических бинарника

Все четыре бинарника компилируются из одного файла исходного кода `src/1_reveal_addresses.c`, но с разными флагами компилятора. `Makefile` определяет, как собирается каждый из них:

[lessons/8_aslr/Makefile1-8](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/Makefile#L1-L8)

Бинарник| Архитектура| PIE| Флаги компилятора
---|---|---|---
`1_reveal_addresses`| i386 (32-бит)| Без PIE| `-m32 -ldl`
`2_reveal_addresses64`| x86-64 (64-бит)| Без PIE| `-ldl`
`3_reveal_addresses_pie`| i386 (32-бит)| PIE включён| `-m32 -ldl -pie`
`4_reveal_addresses64_pie`| x86-64 (64-бит)| PIE включён| `-ldl -pie -fPIC`

Ключевые флаги компиляции, управляющие PIE:

  * **Без PIE**: никаких особых флагов. Линковщик назначает фиксированные виртуальные адреса сегментам исполняемого файла на этапе линковки.
  * **`-pie`**: указывает линковщику создать позиционно-независимый исполняемый файл.
  * **`-fPIC`**: указывает GCC генерировать позиционно-независимый код (требуется для 64-битных PIE-сборок).

### Что печатает каждый бинарник

Каждый бинарник во время выполнения делает следующее (из [lessons/8_aslr/lessonplan.md7-25](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L7-L25)):

  1. Вызывает `getpid()`, чтобы получить свой собственный PID.
  2. Запускает `cat /proc/<pid>/maps` через `system()`, выводя полную раскладку памяти.
  3. Использует `dlsym(RTLD_NEXT, "system")`, чтобы напечатать адрес `system` в libc во время выполнения.

Это даёт прямое, читаемое человеком представление того, куда каждый сегмент фактически отображён при каждом запуске.

---

## PIE против не-PIE: концепция

**Диаграмма: раскладка адресов PIE vs Non-PIE**

Источники: [lessons/8_aslr/lessonplan.md176-179](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L176-L179) [lessons/8_aslr/Makefile1-8](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/Makefile#L1-L8)

**Ключевое различие:**

  * В **не-PIE** бинарнике собственные сегменты text/data исполняемого файла находятся по адресам, зафиксированным на этапе линковки (например, `0x08048000` для 32-битного бинарника). Включение ASLR рандомизирует библиотеки и стек, но _не_ исполняемый файл.
  * В **PIE** бинарнике динамический линковщик обращается с исполняемым файлом как с разделяемым объектом и помещает его по случайному базовому адресу. При уровне ASLR 2 каждая область, включая сам исполняемый файл, рандомизируется при каждом запуске.

---

## Наблюдаемое поведение: ASLR выключен

При `randomize_va_space=0` повторные запуски любого из бинарников показывают одни и те же адреса каждый раз.

Пример из `1_reveal_addresses` (32-бит, без PIE), [lessons/8_aslr/lessonplan.md42-84](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L42-L84):

Область| Фиксированный адрес (ASLR выключен)
---|---
Сегмент text исполняемого файла| `0x08048000`
Куча| `0x0804b000`
`libc-2.23.so` (text)| `0xf7e10000`
Стек| `0xfffdd000`
`system` в libc| `0xf7e4ada0`

Пример из `4_reveal_addresses64_pie` (64-бит, PIE), [lessons/8_aslr/lessonplan.md87-133](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L87-L133):

Область| Фиксированный адрес (ASLR выключен)
---|---
Сегмент text исполняемого файла| `0x555555554000`
Куча| `0x555555756000`
`libc-2.23.so` (text)| `0x7ffff780a000`
Стек| `0x7ffffffde000`
`system` в libc| `0x7ffff784f390`

Даже при включённом PIE адреса детерминированы, когда ASLR выключен. Адрес загрузки PIE `0x555555554000` — это фиксированное значение по умолчанию, выбираемое динамическим линковщиком в отсутствие рандомизации.

---

## Наблюдаемое поведение: ASLR включен (`randomize_va_space=2`)

**Диаграмма: что рандомизирует ASLR в зависимости от PIE**

Источники: [lessons/8_aslr/lessonplan.md135-179](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L135-L179)

При включённом ASLR:

  * **Не-PIE бинарники** (`1_reveal_addresses`, `2_reveal_addresses64`): собственные сегменты исполняемого файла остаются по своим фиксированным адресам линковки. Рандомизируются только библиотеки, стек и куча. Атакующий, знающий, что бинарник не-PIE, всё ещё имеет надёжные адреса ROP-гаджетов внутри исполняемого файла.
  * **PIE бинарники** (`3_reveal_addresses_pie`, `4_reveal_addresses64_pie`): каждая область, включая сам исполняемый файл, рандомизируется. Печатаемый адрес `system` меняется при каждом вызове.

---

## Определение статуса PIE с помощью `checksec`

`checksec` (из pwntools/peda) читает метаданные ELF, чтобы сообщить, был ли бинарник скомпилирован с PIE. В уроке показан вывод `checksec` для всех четырёх бинарников:

[lessons/8_aslr/lessonplan.md148-174](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L148-L174)

**Диаграмма: соответствие вывода checksec файлам бинарников**

Источники: [lessons/8_aslr/lessonplan.md148-174](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L148-L174)

Сводка результатов `checksec`:

Бинарник| Архитектура| PIE| NX| Стек-канарейка
---|---|---|---|---
`1_reveal_addresses`| i386-32-little| **No PIE**| Включён| Canary found
`2_reveal_addresses64`| amd64-64-little| **No PIE**| Включён| Canary found
`3_reveal_addresses_pie`| i386-32-little| **PIE enabled**| Включён| Canary found
`4_reveal_addresses64_pie`| amd64-64-little| **PIE enabled**| Включён| Canary found

Во всех четырёх бинарниках включены NX и стек-канарейки. Единственное различие в наборе — архитектура (32 или 64 бита) и статус PIE.

---

## Как ASLR влияет на стратегию эксплойта

Наблюдения из этого урока напрямую определяют стратегии обхода, рассматриваемые в последующих уроках:

Сценарий| Адреса исполняемого файла предсказуемы?| Адреса библиотек предсказуемы?| Подход
---|---|---|---
ASLR выключен, не-PIE| Да| Да| Прямой ret2libc (Урок 7)
ASLR включен, не-PIE| **Да**| Нет| Ret2PLT (Урок 9), перезапись GOT (Урок 10)
ASLR включен, PIE| Нет| Нет| Требуется утечка памяти (Урок 12, 13)

Ключевое наблюдение: даже при полностью включённом ASLR (`randomize_va_space=2`) собственная секция кода **не-PIE** бинарника (а значит, и его заглушки PLT и ROP-гаджеты) находится по фиксированному, известному адресу. Это фундамент техники Ret2PLT, описанной в [Bypassing ASLR/NX with Ret2PLT](/nnamon/linux-exploitation-course/4.6-bypassing-aslrnx-with-ret2plt).

Источники: [lessons/8_aslr/lessonplan.md1-179](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/lessonplan.md?plain=1#L1-L179) [lessons/8_aslr/Makefile1-8](https://github.com/nnamon/linux-exploitation-course/blob/6b8ca7bf/lessons/8_aslr/Makefile#L1-L8)

**********

[память](/tags/memory.md)
[linux](/tags/linux.md)
[ядро](/tags/kernel.md)