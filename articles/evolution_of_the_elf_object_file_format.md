# Эволюция формата объектных файлов ELF

Источник: [Evolution of the ELF object file format](https://maskray.me/blog/2024-05-26-evolution-of-elf-object-file-format)

Обновлено в сентябре 2025.

Формат объектных файлов ELF принят во многих UNIX-подобных операционных системах. Хотя я [ранее подробно разбирал](https://maskray.me/blog/exploring-object-file-formats) управляющие структуры ELF и его предшественников, само по себе интересным может быть прослеживание исторической эволюции ELF и его связи с System V ABI.

Формат состоит из generic-спецификации, спецификаций для конкретных процессоров и спецификаций для конкретных ОС. При поиске generic-спецификации часто всплывают три ключевых документа:

  * _Tool Interface Standard (TIS) Portable Formats Specification, version 1.2_ на <https://refspecs.linuxfoundation.org/>
  * [_System V Application Binary Interface - DRAFT - 10 June 2013_](https://www.sco.com/developers/gabi/latest/contents.html) на www.sco.com
  * _Oracle Solaris Linkers and Libraries Guide_

Спецификация TIS разбивает ELF на generic-спецификацию, спецификацию для конкретного процессора (x86) и спецификацию для конкретной ОС (System V Release 4). Однако она не обновлялась с 1995 года. Руководство по Solaris, хотя и хорошо написано, включает специфичные для Solaris расширения, неприменимые к Linux и *BSD. Это оставляет нам в первую очередь System V ABI, размещённый на www.sco.com, который посвящает главы 4 и 5 формату ELF.

Давайте проследим историю ELF, чтобы понять его связь с System V ABI.

## История

[Unix System Laboratories (USL)](https://en.wikipedia.org/wiki/Unix_System_Laboratories) создала ELF для своего System V Release 4 в конце 1980-х годов. USL также поддерживала System V Application Binary Interface, составной частью которого был ELF. Система динамических разделяемых библиотек была передана компанией Sun Microsystems из их [SunOS](https://en.wikipedia.org/wiki/SunOS) 4.x (в 1988 году SunOS 4.0 получила расширенный формат a.out с поддержкой динамических разделяемых библиотек).

USL задумывала ELF как открытый стандарт и публиковала документы о формате, например:

  * В трудах Летней конференции USENIX 1990: _ELF: An Object File to Mitigate Mischievous Misoneism_ Джеймса К. Арнольда (James Q. Arnold)
  * _UNIX System V Release 4 Programmer's Guide: ANSI C and Programming Support Tools_ (ISBN 0-13-933706-7), опубликовано в 1990 году
  * _System V Application Binary Interface (Standards)_ (ISBN 0-13-104670-5), опубликовано в 1993 году

В 1993 году комитет Tool Interface Standard (TIS) — консорциум лидеров отрасли — принял ELF и разработал «Tool Interface Standard (TIS) Portable Formats Specification». Версия 1.2 была выпущена в мае 1995 года.

ELF оказался очень влиятельным. В 1990-е многие Unix и Unix-подобные операционные системы, включая Solaris, IRIX, HP-UX, Linux и FreeBSD, перешли на ELF. В FAQ проекта 86open говорилось:

> Q18: Как добиться, чтобы один бинарник одинаково работал во всех этих разнородных системах?
>
> Большинство бинарных пакетов Unix-on-Intel уже во многом схожи. Почти все такие операционные системы используют «ELF»-упаковку бинарников; однако между различными ОС есть небольшие, но значимые различия, из-за которых ELF-бинарник каждой системы непригоден для использования на других.

### Меняющееся попечительство над System V ABI

Комитет Tool Interface Standard (TIS) фактически распался после 1995 года. Попечение над System V ABI, а следовательно и над generic-спецификацией ELF, прошло сложный путь, отражающий передачу активов Unix-программного обеспечения.

Между 1993 и 2011 годами активы Unix пережили несколько передач.

  * В 1993 году Novell [приобрела активы Unix](https://en.wikipedia.org/wiki/Unix_System_Laboratories#Acquisition_by_Novell), включая все авторские права, товарные знаки и лицензионные контракты.
  * В сентябре 1995 года Novell продала бизнес «разработки и продажи лицензий на Unix-бинарники» плюс «работу с лицензиатами исходного кода» компании The Santa Cruz Operation (иногда её называют «старой SCO»). Авторские права остались у Novell (вердикт по делу [SCO против Novell](https://en.wikipedia.org/wiki/SCO_Group,_Inc._v._Novell,_Inc.)).
  * В 2001 году The Santa Cruz Operation продала свои активы Unix-программного обеспечения компании Caldera Systems (позже переименованной в The SCO Group, Inc; иногда её называют «новой SCO» или «SCOX»).
  * В 2011 году Unix-активы The SCO Group были проданы компании UnXis (позже переименованной в Xinuos).

**Задача поддержания и обновления generic ABI переходила к этим последовательным владельцам Unix-активов**. The Santa Cruz Operation, а затем The SCO Group и Xinuos управляли обновлениями и расширениями ABI, включая спецификацию ELF.

В этом [коммите в binutils](https://sourceware.org/cgit/binutils-gdb/commit/?id=723b0f0d39ebe18c9f28e238c9ecc27931faffa7) в ноябре 2000 года говорилось, что за одобрением новых значений `e_machine` следует в конечном итоге обращаться к `registry@sco.com` (сейчас `registry@xinuos.com`).

Дэйв Проссер (Dave Prosser) [поддерживал](http://www.groklaw.net/article.php?story=20040130235310123) System V ABI в USL, затем в The Santa Cruz Operation, а затем в The SCO Group. Последним мейнтейнером в The SCO Group и UnXis/Xinuos был Джон Вулф (John Wolfe), который руководил обновлениями до своего [ухода из Xinuos](https://groups.google.com/g/generic-abi/c/IakWYdGABjQ) в 2015 году. **После этого generic ABI (включая спецификацию ELF) остался без поддержки**.

Последнее функциональное обновление на <https://www.sco.com/developers/gabi/latest/contents.html> было сделано в июне 2013 года — [для `SHF_COMPRESSED`](https://groups.google.com/g/generic-abi/c/9CUHDfWYeu4). С тех пор спецификация остаётся замороженной.

### «All rights reserved»?

Уведомления об авторских правах в документации на сайте SCO для System V ABI кажутся потенциально вводящими в заблуждение.

В сносках страниц <https://www.sco.com/developers/gabi/1998-04-29/contents.html> сегодня (и в 2003 году, по данным web.archive.org) указано:

> © 1997, 1998, 1998 The Santa Cruz Operation, Inc. All rights reserved.

В сносках страниц <https://www.sco.com/developers/gabi/latest/contents.html> указано:

> © 1997, 1998, 1999, 2000, 2001 The Santa Cruz Operation, Inc. All rights reserved. © 2002 Caldera International. All rights reserved. © 2003-2010 The SCO Group. All rights reserved. © 2011-2015 Xinuos Inc. All rights reserved.

Многократно повторяемая фраза «All rights reserved» может быть истолкована как намёк на исключительное владение самим форматом ELF. Это неточно: ELF — открытый стандарт, развитый благодаря сотрудничеству многих организаций и частных лиц. Роль The Santa Cruz Operation в эволюции System V ABI, судя по всему, была скорее ролью редактора, нежели новатора. После того как The Santa Cruz Operation продала свои активы Unix в 2001 году, спецификация в основном оставалась неизменной, с редкими точечными обновлениями.

Самый ранний доступный снимок в Wayback Machine датируется 2003 годом — временем, когда The SCO Group приняла владение и начала судебный процесс против IBM, утверждая, что успех Linux объясняется неправомерным использованием технологий SCO. К сожалению, более ранние снимки недоступны, чтобы дать более полный исторический контекст.

_Tool Interface Standard (TIS) Portable Formats Specification, version 1.2_ фактически [поместила спецификацию в общественное достояние](http://www.groklaw.net/article.php?story=20040722135616439):

> Комитет TIS предоставляет вам неисключительную, всемирную, безотлатную лицензию на использование информации, раскрытой в этой Спецификации, для того чтобы сделать ваше программное обеспечение совместимым с TIS; никакие иные лицензии, явные или подразумеваемые, настоящим не предоставляются и не предполагаются.

Дополнительное чтение:

  * [The SCO lawsuit, 20 years later](https://lwn.net/Articles/924577/)
  * [A Tall Tale About ELF - by Frank Sorenson, Dr Stupid and PJ](http://www.groklaw.net/article.php?story=20040722135616439)
  * [SCO shows more code](https://lwn.net/Articles/87556/)
  * [SCO's Summary Judgment Hearing Binder](https://www.sco.com/company/legal/update/website2.3.pdf)

### Google-группа generic-abi

Для обсуждения generic ABI существует нейтральная [Google-группа](https://groups.google.com/g/generic-abi), не аффилированная с The SCO Group/Xinuos. Вероятно, её владельцем является Hongjiu Lu. Группа служила платформой для сотрудничества поставщиков ОС и тулчейнов. В последние годы участие свелось в основном к представителям Oracle Solaris (только Ali Bahrami) и GNU-тулчейна.

Снижение активности может не казаться критичным, поскольку **значительные не-ОС-специфичные изменения формата ELF редки**.

## Эволюция generic ABI

Страница <https://www.sco.com/developers/gabi/latest/revision.html> описывает эволюцию ELF с 1998 по 2013 год. Все важные возможности были доступны уже к апрелю 2001 года:

  * Видимость символов
  * [Группы секций](https://maskray.me/blog/comdat-and-section-group)
  * `EI_OSABI` и `EI_ABIVERSION`
  * [`SHF_MERGE` и `SHF_STRINGS`](https://maskray.me/blog/why-isnt-ld.lld-faster#shf_merge-duplicate-elimination)
  * [`SHF_LINK_ORDER`](https://maskray.me/blog/metadata-sections-comdat-and-shf-link-order)

Однако **обсуждения этих конкретных возможностей, судя по всему, недоступны**. Дайте мне знать, если у вас есть о них какая-либо информация.

С апреля 2001 по июнь 2013 были лишь точечные обновления. `SHF_COMPRESSED` была добавлена в июне 2013 года.

Google-группа generic-abi **достигла консенсуса по предложениям**, которые не нашли отражения на сайте www.sco.com:

  * 2018: [формат относительных релокаций RELR](https://maskray.me/blog/relative-relocations-and-relr#relr-relative-relocation-format)
  * 2022: [`ELFCOMPRESS_ZSTD`](https://maskray.me/blog/zstd-compressed-debug-sections)

### Будущее в подвешенном состоянии

В апреле 2020 года Кэри Коутант (Cary Coutant) достиг [предварительной договорённости](https://groups.google.com/g/generic-abi/c/9OO5vhxb00Y) с Xinuos, но **будущее остаётся неопределённым**. Хотя некоторые константы (например, значения `e_machine` и `EI_OSABI`, `ELFCOMPRESS_ZSTD`) были определены, функциональных обновлений ABI не последовало.

Отсутствие централизованного, актуального репозитория спецификации усложняло ситуацию.

Пока в группе generic-abi были достигнуты некоторые разъяснения и консенсусы, доступ к последнему, окончательному тексту оставался проблемой.

Потенциальным решением могло бы стать **отделение спецификации ELF от более широкого System V ABI**, как это было сделано в прошлом со спецификацией TIS. Это создало бы выделенную и доступную спецификацию для ELF, независимую от более широких System V-спецификов, представляющих меньший общий интерес.

Несмотря на эту неопределённость, инновации в экосистеме ELF должны продолжаться. Такие усилия, как мои собственные по замене управляющих структур ELF для уменьшения размеров объектных файлов (например, [компактные релокации](https://maskray.me/blog/a-compact-section-header-table-for-elf)), всё же могут продвигаться вперёд. На практике консенсуса среди основных поставщиков тулчейнов (GNU и LLVM) может быть достаточно даже без формального одобрения со стороны generic ABI. Хотя согласование с Solaris было бы идеалом, и я постараюсь этого добиться, это не всегда может быть осуществимо из-за разных приоритетов.

FreeBSD, на которой основан OpenServer от Xinuos, использует тулчейн LLVM. Xinuos мог бы косвенно выиграть от моего активного участия в тулчейне LLVM.

В августе 2025 года Кэри Коутант опубликовал <https://gabi.xinuos.com/> (ELF Object File Format) и <https://github.com/xinuos/gabi>.

## Processor Supplement (psABI) System V ABI

Детали, специфичные для процессоров, в System V ABI находятся в документах psABI. Активно поддерживаемые psABI существуют для различных архитектур, включая [AArch32](https://maskray.me/blog/linker-notes-on-aarch32), [AArch64](https://maskray.me/blog/linker-notes-on-aarch64), LoongArch, [PPC64](https://maskray.me/blog/linker-notes-on-power-isa), RISC-V, [s390x](https://maskray.me/blog/toolchain-notes-on-z-architecture), [i386 и x86-64](https://maskray.me/blog/linker-notes-on-x86). (Эти ссылки ведут к моим заметкам.)

У многих архитектур psABI устаревшие или недоступны. Например:

  * ppc32: _Power Architecture® 32-bit Application Binary Interface Supplement 1.0 - Linux & Embedded_ был опубликован в 2011 году. [Мои заметки](https://maskray.me/blog/linker-notes-on-power-isa)
  * MIPS: самый свежий o32 ABI датируется февралём 1996 года, а n64 ABI недоступен. N32 ABI сопровождает снятый с производства компилятор MIPSpro: _MIPSpro N32 ABI Handbook_. [Мои заметки](https://maskray.me/blog/toolchain-notes-on-mips)

Заслуживающие внимания детали:

  * Архитектуры вроде Motorola 6800, имеющие 16-битные адресные пространства, используют формат ELFCLASS32.
  * Многие архитектуры никогда не были портированы ни на одну производную ОС System V, но их документы psABI всё равно используют имя «System V».
  * Некоторые поведенческие детали формально не документированы и могут быть найдены только в исходном коде проекта binutils.

## ABI для конкретных операционных систем

В System V ABI ABI для конкретных операционных систем (Operating System Specific ABI, OSABI) — это расширения, предоставляющие детали, специфичные для операционной системы, дополняющие generic ABI.

Например, _Oracle Solaris Linkers and Libraries Guide_ определяет OSABI для Solaris.

Термин OSABI расплывчат, и это может быть не один-единственный документ. Для Linux нам нужны следующие два документа:

  * [gABI supplement for program loading and dynamic linking on GNU](https://sourceware.org/gnu-gabi/)
  * <https://gitlab.com/x86-psABIs/Linux-ABI/>

Linux Standard Base (LSB) — родственный документ, целью которого является стандартизация системного интерфейса Linux.

До недавнего появления _gABI supplement for program loading and dynamic linking on GNU_ секция `SHT_GNU_HASH`, несмотря на широкое распространение, отсутствовала в какой-либо официальной документации.

Интересно, что многие расширения Linux ABI достаточно универсальны, чтобы их могли принять другие операционные системы вроде FreeBSD, что позволяет предположить, что отдельный документ OSABI для FreeBSD может не понадобиться.

**********

[elf](/tags/elf.md)
[linux](/tags/linux.md)
[unix](/tags/unix.md)