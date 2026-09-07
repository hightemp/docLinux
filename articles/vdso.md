# vDSO

Источник: [vDSO](https://en.wikipedia.org/wiki/VDSO)

**vDSO** (virtual dynamic shared object — виртуальный динамически подключаемый разделяемый объект) — механизм ядра, экспортирующий тщательно отобранный набор процедур [пространства ядра](https://ru.wikipedia.org/wiki/Пространство_ядра) в приложения [пользовательского пространства](https://ru.wikipedia.org/wiki/Пространство_пользователя), чтобы приложения могли вызывать эти процедуры ядра внутри собственного процесса — без накладных расходов на [переключение режима](https://en.wikipedia.org/wiki/Mode_switch_(computing)) с пользовательского на режим ядра, присущих вызову тех же процедур через интерфейс [системных вызовов](https://ru.wikipedia.org/wiki/Системный_вызов)[1][2].

vDSO использует стандартные механизмы [линковки](https://ru.wikipedia.org/wiki/Компоновщик) и [загрузки](https://ru.wikipedia.org/wiki/Загрузчик_исполняемых_файлов), то есть стандартный формат [ELF](https://ru.wikipedia.org/wiki/Executable_and_Linkable_Format) (Executable and Linkable Format)[3][4]. vDSO — область памяти, выделяемая в пользовательском пространстве, которая открывает доступ к части функциональности ядра. vDSO [выделяется динамически](https://ru.wikipedia.org/wiki/Динамическое_распределение_памяти), обеспечивает повышенную безопасность за счёт [рандомизации адресного пространства](https://ru.wikipedia.org/wiki/ASLR) и поддерживает более четырёх системных вызовов. Некоторые [стандартные библиотеки C](https://ru.wikipedia.org/wiki/Стандартная_библиотека_языка_C), как, например, [glibc](https://ru.wikipedia.org/wiki/Glibc), могут предоставлять ссылки vDSO так, что если ядро не поддерживает vDSO, выполняется обычный [системный вызов](https://ru.wikipedia.org/wiki/Syscall)[5]. vDSO помогает снизить накладные расходы вызова простых процедур ядра, а также может служить способом выбора оптимального метода системного вызова на некоторых [архитектурах](https://ru.wikipedia.org/wiki/Архитектура_компьютера), например [IA-32](https://ru.wikipedia.org/wiki/IA-32)[6]. Преимущество перед другими методами в том, что такие экспортируемые процедуры могут предоставлять корректную отладочную информацию [DWARF](https://ru.wikipedia.org/wiki/DWARF). Реализация обычно предполагает хуки в динамическом компоновщике для поиска vDSO.

vDSO был разработан, чтобы предоставить возможности **vsyscall**, преодолев его ограничения: небольшой объём [статически выделенной](https://en.wikipedia.org/wiki/Static_memory_allocation) памяти, допускающий лишь четыре системных вызова, и одинаковые адреса [двоичного интерфейса приложений](https://ru.wikipedia.org/wiki/Двоичный_интерфейс_приложений) (ABI) в каждом процессе, что компрометирует безопасность. Проблема безопасности смягчена [эмуляцией виртуального системного вызова](https://en.wikipedia.org/wiki/Sigreturn-oriented_programming#Vsyscall_emulation), но эмуляция вносит дополнительную задержку[5].

В [glibc](https://ru.wikipedia.org/wiki/Glibc) есть поддержка vDSO для `getrandom()`[7].

## Ссылки

  1. Enrico Perla; Massimiliano Oldani (16 декабря 2016). [_Kernel Hacking: Exploits verstehen, schreiben und abwehren_](https://books.google.com/books?id=9cZ2DwAAQBAJ&pg=PA466) (нем.). Franzis Verlag. С. 466–. [ISBN 978-3-645-20503-0](https://en.wikipedia.org/wiki/Special:BookSources/978-3-645-20503-0).
  2. ["vDSO — overview of the virtual ELF dynamic shared object"](https://web.archive.org/web/20160304114048/http://manpages.ubuntu.com/manpages/wily/man7/vdso.7.html). Canonical. Архив оригинала от 4 марта 2016. Проверено 10 декабря 2015.
  3. ["Creating a vDSO: the Colonel's Other Chicken"](http://www.linuxjournal.com/content/creating-vdso-colonels-other-chicken). Linuxjournal.com. Проверено 16 февраля 2015.
  4. Corbet, Jonathan (8 июня 2011). ["On vsyscalls and the vDSO"](https://lwn.net/Articles/446528/). Lwn.net. Проверено 16 февраля 2015.
  5. ["Community answer to question "What are vDSO and vsyscall?""](https://stackoverflow.com/q/19938324). Проверено 19 ноября 2016.
  6. Drysdale, David (16 июля 2014). ["Anatomy of a system call, part 2"](https://lwn.net/Articles/604515/). Lwn.net. Проверено 19 ноября 2018.
  7. ["sourceware.org Git — glibc.git/commit"](https://sourceware.org/git/?p=glibc.git;a=commit;h=461cab1de747f3842f27a5d24977d78d561d45f9). _sourceware.org_. Проверено 13 ноября 2024.

**********

[Linux](/tags/linux.md)
[память](/tags/memory.md)
[vDSO](/tags/vdso.md)