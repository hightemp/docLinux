# Рецепты для ELFов

Источник: [Рецепты для ELFов](https://habr.com/ru/companies/inforion/articles/460247/)

![image](/images/9b64fb7d3b66e654b2f76ccdb59e4b18.png)

На русском языке довольно мало информации про то, как работать с ELF-файлами (Executable and Linkable Format — основной формат исполняемых файлов Linux и многих Unix-систем). Не претендуем на полное покрытие всех возможных сценариев работы с эльфами, но надеемся, что информация будет полезна в виде справочника и сборника рецептов для программистов и реверс-инженеров.

Подразумевается, что читатель на базовом уровне знаком с форматом ELF (в противном случае рекомендуем цикл статей [Executable and Linkable Format 101](http://www.intezer.com/executable-linkable-format-101-part1-sections-segments/)).

Под катом будут перечислены инструменты для работы, описаны приемы для чтения метаинформации, модификации, проверки и ~~размножения~~ создания эльфов, а также приведены ссылки на полезные материалы.

> — Я тоже эльф… Синий в красный… Эльфы очень терпеливы… Синий в красный… А мы эльфы!.. Синий в красный… От магии одни беды…
>  (с) Маленькое королевство Бена и Холли

# Инструменты

В большинстве случаев примеры можно выполнить как на Linux, так и на Windows.

В рецептах мы будем использовать следующие инструменты:

  * утилиты из набора binutils (objcopy, objdump, readelf, strip);
  * фреймворк [radare2](https://www.radare.org/r/);
  * hex-редактор с поддержкой шаблонов файлов (в примерах показан [010Editor](https://www.sweetscape.com/010editor/), но можно использовать, например, свободный [Veles](https://codisec.com/veles/));
  * Python и библиотеку [LIEF](https://lief.quarkslab.com/);
  * другие утилиты (ссылки указаны в рецепте).

# Тестовые эльфы

В качестве «подопытного» будем использовать ELF-файл _simple_ из таска [nutcake's PieIsMyFav](https://crackmes.one/crackme/5c11e1f333c5d41e58e00579) на crackmes.one, но подойдёт любой представитель «эльфийского» семейства. Если готовый файл с требуемыми характеристиками не был найден в свободном доступе, то будет приведён способ создания такого эльфа.

«Свободных» эльфов можно также найти по ссылкам:

  * [Примеры эльфов для разных платформ](https://github.com/JonathanSalwan/binary-samples);
  * [Тестовые эльфы для radare2](https://github.com/radare/radare2-regressions/tree/master/bins/elf);
  * [Проект ElfHacks на Github](https://github.com/MaskRay/ElfHacks/) — подборка небольших эльфов с разными настройками;
  * [Crackme для Unix/Linux](https://crackmes.one) — но стоит учитывать, что тут могут попадаться хитрые образцы.

# Чтение, получение информации

## Тип файла, заголовок, секции

В зависимости от задачи интерес могут представлять:

  * тип файла (DYN — библиотека, EXEC — исполняемый, RELOC — линкуемый);
  * целевая архитектура (E_MACHINE — x86_64, x86, ARM и т.д.);
  * точка входа в приложение (Entry Point);
  * информация о секциях.

### 010Editor

HEX-редактор 010Editor предоставляет систему шаблонов. Для ELF-файлов шаблон называется, как ни странно, _ELF.bt_ и находится в категории _Executable_ (меню Templates — Executable).
Интерес может представлять, например, точка входа в исполняемый файл (entry point) (записана в заголовке файла).

![image](/images/9f19662b752e14948ad877d9b20b0fec.png)

### readelf

Утилиту _readelf_ можно считать стандартом де-факто для получения сведений об ELF-файле.

  * Прочитать заголовок файла:

```bash
    $ readelf -h simple
```

**Результат команды**

```text
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Shared object file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x1070
  Start of program headers:          64 (bytes into file)
  Start of section headers:          14800 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         11
  Size of section headers:           64 (bytes)
  Number of section headers:         30
  Section header string table index: 29
```

  * Прочитать информацию о сегментах и секциях:

```bash
    $ readelf -l -W simple
```

**Результат команды**

Для удобства чтения адреса приведены к 32-битному формату:

```text
Elf file type is DYN (Shared object file)
Entry point 0x1070
There are 11 program headers, starting at offset 64

Program Headers:
 Type         Offset   VirtAddr   PhysAddr   FileSiz  MemSiz   Flg Align
 PHDR         0x000040 0x00000040 0x00000040 0x000268 0x000268 R   0x8
 INTERP       0x0002a8 0x000002a8 0x000002a8 0x00001c 0x00001c R   0x1
     [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
 LOAD         0x000000 0x00000000 0x00000000 0x0005f8 0x0005f8 R   0x1000
 LOAD         0x001000 0x00001000 0x00001000 0x00026d 0x00026d R E 0x1000
 LOAD         0x002000 0x00002000 0x00002000 0x0001b8 0x0001b8 R   0x1000
 LOAD         0x002de8 0x00003de8 0x00003de8 0x000258 0x000260 RW  0x1000
 DYNAMIC      0x002df8 0x00003df8 0x00003df8 0x0001e0 0x0001e0 RW  0x8
 NOTE         0x0002c4 0x000002c4 0x000002c4 0x000044 0x000044 R   0x4
 GNU_EH_FRAME 0x002070 0x00002070 0x00002070 0x00003c 0x00003c R   0x4
 GNU_STACK    0x000000 0x00000000 0x00000000 0x000000 0x000000 RW  0x10
 GNU_RELRO    0x002de8 0x00003de8 0x00003de8 0x000218 0x000218 R   0x1

 Section to Segment mapping:
  Segment Sections...
   00
   01     .interp
   02     .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt
   03     .init .plt .plt.got .text .fini
   04     .rodata .eh_frame_hdr .eh_frame
   05     .init_array .fini_array .dynamic .got .got.plt .data .bss
   06     .dynamic
   07     .note.ABI-tag .note.gnu.build-id
   08     .eh_frame_hdr
   09
   10     .init_array .fini_array .dynamic .got
```

  * Прочитать информацию о секциях:

```bash
    $ readelf -S -W simple
```

**Результат команды**

Для удобства чтения адреса приведены к 32-битному формату:

```text
There are 30 section headers, starting at offset 0x39d0:

Section Headers:
  [Nr] Name              Type            Address  Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .interp           PROGBITS        000002a8 0002a8 00001c 00   A  0   0  1
  [ 2] .note.ABI-tag     NOTE            000002c4 0002c4 000020 00   A  0   0  4
  [ 3] .note.gnu.build-id NOTE            000002e4 0002e4 000024 00   A  0   0  4
  [ 4] .gnu.hash         GNU_HASH        00000308 000308 000024 00   A  5   0  8
  [ 5] .dynsym           DYNSYM          00000330 000330 0000d8 18   A  6   1  8
  [ 6] .dynstr           STRTAB          00000408 000408 0000a2 00   A  0   0  1
  [ 7] .gnu.version      VERSYM          000004aa 0004aa 000012 02   A  5   0  2
  [ 8] .gnu.version_r    VERNEED         000004c0 0004c0 000030 00   A  6   1  8
  [ 9] .rela.dyn         RELA            000004f0 0004f0 0000c0 18   A  5   0  8
  [10] .rela.plt         RELA            000005b0 0005b0 000048 18  AI  5  23  8
  [11] .init             PROGBITS        00001000 001000 000017 00  AX  0   0  4
  [12] .plt              PROGBITS        00001020 001020 000040 10  AX  0   0 16
  [13] .plt.got          PROGBITS        00001060 001060 000008 08  AX  0   0  8
  [14] .text             PROGBITS        00001070 001070 0001f2 00  AX  0   0 16
  [15] .fini             PROGBITS        00001264 001264 000009 00  AX  0   0  4
  [16] .rodata           PROGBITS        00002000 002000 000070 00   A  0   0  8
  [17] .eh_frame_hdr     PROGBITS        00002070 002070 00003c 00   A  0   0  4
  [18] .eh_frame         PROGBITS        000020b0 0020b0 000108 00   A  0   0  8
  [19] .init_array       INIT_ARRAY      00003de8 002de8 000008 08  WA  0   0  8
  [20] .fini_array       FINI_ARRAY      00003df0 002df0 000008 08  WA  0   0  8
  [21] .dynamic          DYNAMIC         00003df8 002df8 0001e0 10  WA  6   0  8
  [22] .got              PROGBITS        00003fd8 002fd8 000028 08  WA  0   0  8
  [23] .got.plt          PROGBITS        00004000 003000 000030 08  WA  0   0  8
  [24] .data             PROGBITS        00004030 003030 000010 00  WA  0   0  8
  [25] .bss              NOBITS          00004040 003040 000008 00  WA  0   0  1
  [26] .comment          PROGBITS        00000000 003040 00001c 01  MS  0   0  1
  [27] .symtab           SYMTAB          00000000 003060 000630 18     28  44  8
  [28] .strtab           STRTAB          00000000 003690 000232 00      0   0  1
  [29] .shstrtab         STRTAB          00000000 0038c2 000107 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), l (large)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```

  * Прочитать информацию о символах:

```bash
    $ readelf -s -W simple
```

**Результат команды**

Вывод сокращён для удобства чтения:

```text
Symbol table '.dynsym' contains 9 entries:
   Num:  Value        Size   Type    Bind    Vis      Ndx Name
     0: 00000000   0 NOTYPE  LOCAL  DEFAULT  UND
     1: 00000000   0 NOTYPE  WEAK   DEFAULT  UND _ITM_deregisterTMCloneTable
     2: 00000000   0 FUNC    GLOBAL DEFAULT  UND puts@GLIBC_2.2.5 (2)
     3: 00000000   0 FUNC    GLOBAL DEFAULT  UND printf@GLIBC_2.2.5 (2)
     4: 00000000   0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.2.5 (2)
     5: 00000000   0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
     6: 00000000   0 FUNC    GLOBAL DEFAULT  UND __isoc99_scanf@GLIBC_2.7 (3)
     7: 00000000   0 NOTYPE  WEAK   DEFAULT  UND _ITM_registerTMCloneTable
     8: 00000000   0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@GLIBC_2.2.5 (2)

Symbol table '.symtab' contains 66 entries:
   Num:  Value        Size   Type    Bind    Vis      Ndx Name
     0: 00000000   0 NOTYPE  LOCAL  DEFAULT  UND
     1: 000002a8   0 SECTION LOCAL  DEFAULT    1
     2: 000002c4   0 SECTION LOCAL  DEFAULT    2
     3: 000002e4   0 SECTION LOCAL  DEFAULT    3
     4: 00000308   0 SECTION LOCAL  DEFAULT    4
     5: 00000330   0 SECTION LOCAL  DEFAULT    5
     6: 00000408   0 SECTION LOCAL  DEFAULT    6
     7: 000004aa   0 SECTION LOCAL  DEFAULT    7
     ....
    26: 00000000   0 SECTION LOCAL  DEFAULT   26
    27: 00000000   0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
    28: 000010a0   0 FUNC    LOCAL  DEFAULT   14 deregister_tm_clones
    29: 000010d0   0 FUNC    LOCAL  DEFAULT   14 register_tm_clones
    30: 00001110   0 FUNC    LOCAL  DEFAULT   14 __do_global_dtors_aux
    31: 00004040   1 OBJECT  LOCAL  DEFAULT   25 completed.7389
     ....
```

Опция `-W` нужна для увеличения ширины консольного вывода (по умолчанию, 80 символов).

### LIEF

Прочитать заголовок и информацию о секциях можно с использованием кода на Python и библиотеки LIEF (предоставляет API не только для Python):

```python
import lief
```

```text
binary = lief.parse("simple.elf")
header = binary.header
```

```python
print("Entry point: %08x" % header.entrypoint)
print("Architecture: ", header.machine_type)
```

```python
for section in binary.sections:
    print("Section %s - size: %s bytes" % (section.name, section.size)
```

## Информация о компиляторе

Для получения информации о компиляторе и сборке следует смотреть секции `.comment` и `.note`.

### objdump

```bash
$ objdump -s --section .comment simple
```

**Результат команды**

```text
simple:     file format elf64-x86-64

Contents of section .comment:
 0000 4743433a 20284465 6269616e 20382e32  GCC: (Debian 8.2
 0010 2e302d39 2920382e 322e3000           .0-9) 8.2.0.
```

### readelf

```bash
$ readelf -p .comment simple
```

**Результат команды**

```bash
String dump of section '.comment':
  [     0]  GCC: (Debian 8.2.0-9) 8.2.0

$ readelf -n simple
```

**Результат команды**

```text
Displaying notes found at file offset 0x000002c4 with length 0x00000020:
  Owner                 Data size    Description
  GNU                  0x00000010    NT_GNU_ABI_TAG (ABI version tag)
    OS: Linux, ABI: 3.2.0

Displaying notes found at file offset 0x000002e4 with length 0x00000024:
  Owner                 Data size    Description
  GNU                  0x00000014    NT_GNU_BUILD_ID (unique build ID bitstring)
    Build ID: dae0509e4edb79719a65af37962b74e4cf2a8c2e
```

### LIEF

```python
import lief
binary = lief.parse("simple")
comment = binary.get_section(".comment")
print("Comment: ", bytes(comment.content))
```

## Я вычислю тебя по… RPATH

Эльфы могут сохранять пути для поиска динамически подключаемых библиотек. Чтобы не задавать системную переменную `LD_LIBRARY_PATH` перед запуском приложения, можно просто «вшить» этот путь в ELF-файл.

Для этого используется запись в секции `.dynamic` с типом `DT_RPATH` или `DT_RUNPATH` (см. главу [Directories Searched by the Runtime Linker](https://docs.oracle.com/cd/E26505_01/html/E26506/chapter6-63352.html#chapter3-10898) в документации).

**И будь осторожен, юный разработчик, не «спали» свою директорию проекта!**

### Как появляется RPATH?

Основная причина появления RPATH-записи в эльфе — опция `-rpath` линковщика для поиска динамической библиотеки. Примерно так:

```bash
$ gcc -L./lib -Wall -Wl,-rpath=/run/media/pablo/disk1/projects/cheat_sheets/ELF/lib/ -o test_rpath.elf bubble_main.c -lbubble
```

Такая команда создаст в секции `.dynamic` RPATH-запись со значением `/run/media/pablo/disk1/projects/cheat_sheets/ELF/lib/`.

### readelf

Посмотреть элементы из секции `.dynamic` (среди которых есть и RPATH) можно так:

```bash
$ readelf -d test_rpath.elf
```

**Результат команды**

Для удобства чтения результат команды сокращён:

```text
Dynamic section at offset 0x2dd8 contains 28 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libbubble.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x000000000000000f (RPATH)              Library rpath: [/run/media/pablo/disk1/projects/cheat_sheets/ELF/lib/]
 0x000000000000000c (INIT)               0x1000
 0x000000000000000d (FINI)               0x11c8
....
```

### LIEF

С помощью библиотеки LIEF также можно прочитать RPATH-запись в эльфе:

```python
import lief
from lief.ELF import DYNAMIC_TAGS
```

```text
elf = lief.parse("test_rpath.elf")
```

```python
if elf.has(DYNAMIC_TAGS.RPATH):
    rpath = next(filter(lambda x: x.tag == DYNAMIC_TAGS.RPATH, elf.dynamic_entries))
    for path in rpath.paths:
        print(path)
else:
    print("No RPATH in ELF")
```

[Почитать про секцию .dynamic](https://docs.oracle.com/cd/E26505_01/html/E26506/chapter6-42444.html)

## Проверка эльфа на безопасность

Скрипт проверки безопасности [checksec.sh](https://www.trapkit.de/tools/checksec.html) от исследователя Tobias Klein (автора книги [A Bug Hunter's Diary](https://nostarch.com/bughunter)) не обновлялся с 2011 года. Данный скрипт для ELF-файлов выполняет проверку наличия опций RelRO (Read Only Relocations), NX (Non-Executable Stack), Stack Canaries, PIE (Position Independent Executables) и для своей работы использует утилиту _readelf_.

### LIEF

Можно сделать свой аналог на ~~коленке~~ Python и LIEF (чуть короче прародителя и с дополнительной проверкой опции [separate-code](https://habr.com/ru/company/dsec/blog/433108/)):

```python
import lief
from lief.ELF import DYNAMIC_TAGS, SEGMENT_TYPES
```

```python
def filecheck(filename):
    binary = lief.parse(filename)
```

```python
    # check RELRO
    if binary.has(SEGMENT_TYPES.GNU_RELRO):
        print("+ Full RELRO") if binary.has(DYNAMIC_TAGS.BIND_NOW) else print("~ Partial RELRO")
    else:
        print("- No RELRO")
```

```python
    # check for stack canary support
    print("+ Canary found") if binary.has_symbol("__stack_chk_fail") else print("- No canary found")
```

```python
    # check for NX support (check X-flag for GNU_STACK-segment)
    print("+ NX enabled") if binary.has_nx else print("- NX disabled")
```

```python
    # check for PIE support
    print("+ PIE enabled") if binary.is_pie else print("- No PIE")
```

```python
    # check for rpath / run path
    print("+ RPATH") if binary.has(DYNAMIC_TAGS.RPATH) else print("- No RPATH")
    print("+ RUNPATH")if binary.has(DYNAMIC_TAGS.RUNPATH) else print("- No RUNPATH")
```

```python
    # check separate-code option
    if set(binary.get_section('.text').segments) == set(binary.get_section('.rodata').segments):
        print("- Not Separated Code Sections")
    else:
        print("+ Separated Code Sections")
```

```text
filecheck('test_rpath.elf')
```

### Radare2

Спасибо [dukebarman](https://habr.com/ru/users/dukebarman/) за дополнение по использованию Radare2 для вывода информации аналогично _checksec_ :

```text
> r2 -c i~pic,canary,nx,crypto,stripped,static,relocs test_stack_proteck
```

## «Сырой код» из эльфа (binary from ELF)

Бывают ситуации, когда «эльфийские одёжи» в виде ELF-структуры не нужны, а нужен только «голый» исполняемый код приложения.

### objcopy

Использование _objcopy_ вероятно знакомо тем, кто пишет прошивки:

```bash
$ objcopy -O binary -S -g simple.elf simple.bin
```

  * `-S` — для удаления символьной информации;
  * `-g` — для удаления отладочной информации.

### LIEF

Никакой магии. Просто взять содержимое загружаемых секций и слепить из них бинарь:

```python
import lief
from lief.ELF import SECTION_FLAGS, SECTION_TYPES
```

```text
binary = lief.parse("test")
end_addr = 0
data = []

for section in filter(lambda x: x.has(SECTION_FLAGS.ALLOC) and
                                x.type != SECTION_TYPES.NOBITS,
                      binary.sections):
    if 0 < end_addr < section.virtual_address:
        align_bytes = b'\x00' * (section.virtual_address - end_addr)
        data.append(align_bytes)

    data.append(bytes(section.content))
    end_addr = section.virtual_address + section.size

with open('test.lief.bin', 'wb') as f:
    for d_bytes in data:
        f.write(d_bytes)
```

## Mangled — demangled имена функций

В ELF-ах, созданных из С++ кода, имена функций декорированы (манглированы) для упрощения поиска соответствующей функции класса. Однако читать такие имена при анализе не очень удобно.

[Тестовый эльф](https://github.com/radare/radare2-regressions/blob/master/bins/elf/demangle-test-cpp)

### nm

Для представления имён в удобочитаемом виде можно использовать утилиту [nm](https://sourceware.org/binutils/docs/binutils/nm.html) из набора binutils:

```bash
# Тут имена функций выводятся в манглированном виде
$ nm -D demangle-test-cpp
     ...
      U _Unwind_Resume
      U _ZdlPv
      U _Znwm
      U _ZSt17__throw_bad_allocv
      U _ZSt20__throw_length_errorPKc

# Тут имена функций выводятся в читаемом виде
$ nm -D --demangle demangle-test-cpp
      ...
      U _Unwind_Resume
      U operator delete(void*)
      U operator new(unsigned long)
      U std::__throw_bad_alloc()
      U std::__throw_length_error(char const*)
```

### LIEF

Вывод имён символов в деманглированном виде с использованием библиотеки LIEF:

```python
import lief
binary = lief.parse("demangle-test-cpp")
for symb in binary.symbols:
    print(symb.name, symb.demangled_name)
```

# Сборка, запись, модификация эльфа

## Эльф без метаинформации

После того как приложение отлажено и выпускается в дикий мир, имеет смысл удалить метаинформацию:

  * отладочные секции — бесполезны в большинстве случаев;
  * имена переменных и функций — совершенно ни на что не влияют для конечного пользователя (чуть усложняет реверс);
  * таблица секций — совершенно не нужна для запуска приложения (её отсутсвие чуть усложнит реверс).

## Удаление символьной информации

Символьная информация — это имена объектов и функций. Без неё реверс приложения немного усложняется.

### strip

В самом простом случае можно воспользоваться утилитой [strip](https://www.sourceware.org/binutils/docs/binutils/strip.html) из набора binutils. Для удаления всей символьной информации достаточно выполнить команду:

  * для исполняемого файла:

```bash
    $ strip -s simple
```

  * для динамической библиотеки:

```bash
    $ strip --strip-unneeded libsimple.so
```

### sstrip

Для тщательного удаления символьной информации (в том числе ненужных нулевых байтов в конце файла) можно воспользоваться утилитой sstrip из набора [ELFkickers](https://github.com/BR903/ELFkickers). Для удаления всей символьной информации достаточно выполнить команду:

```bash
$ sstrip -z simple
```

### LIEF

C использованием библиотеки LIEF также можно сделать быстрый strip (удаляется таблица символов — секция `.symtab`):

```python
import lief
binary = lief.parse("simple")
binary.strip()
binary.write("simple.stripped")
```

## Удаление таблицы секций

Как упоминалось выше, наличие/отсутствие таблицы секций не оказывает влияния на работу приложения. Но при этом без таблицы секций реверс приложения становится чуть сложнее.
Воспользуемся библиотекой LIEF под Python и [примером удаления таблицы секций](https://github.com/lief-project/LIEF/blob/master/examples/python/elf_remove_section_table.py):

```python
import lief
binary = lief.parse("simple")
binary.header.numberof_sections = 0
binary.header.section_header_offset = 0
binary.write("simple.modified")
```

## Изменение и удаление RPATH

### chrpath, PatchELF

Для изменения RPATH под Linux можно воспользоваться утилитами _chrpath_ (доступна в большинстве дистрибутивов) или [PatchELF](https://nixos.org/patchelf.html).

  * Изменить RPATH:

```bash
    $ chrpath -r /opt/my-libs/lib:/foo/lib test_rpath.elf
```

или

```bash
    $ patchelf --set-rpath /opt/my-libs/lib:/foo/lib test_rpath.elf
```

  * Удалить RPATH:

```bash
    $ chrpath -d test_rpath.elf
```

или

```bash
    $ patchelf --shrink-rpath test_rpath.elf
```

### LIEF

Библиотека LIEF также позволяет как изменить, так и удалить RPATH-запись.

  * Изменить RPATH:

```python
    import lief
    binary  = lief.parse("test_rpath.elf")
    rpath = next(filter(lambda x: x.tag == lief.ELF.DYNAMIC_TAGS.RPATH, binary.dynamic_entries))
    rpath.paths = ["/opt/my-lib/here"]
    binary.write("test_rpath.patched")
```

  * Удалить RPATH:

```python
    import lief
    binary  = lief.parse("test_rpath.elf")
    binary.remove(lief.ELF.DYNAMIC_TAGS.RPATH)
    binary.write("test_rpath.patched")
```

## Обфускация символьной информации

Для усложнения реверса приложения можно сохранить символьную информацию, но запутать имена объектов. В качестве подопытного используем эльф _crackme01_32bit_ из [crackme01 by seveb](https://crackmes.one/crackme/5ab77f5e33c5d40ad448c78b).

Упрощенный вариант [примера](https://github.com/lief-project/LIEF/blob/master/examples/python/elf_symbol_obfuscation.py) из библиотеки LIEF может выглядеть так:

```python
import lief
```

```text
binary = lief.parse("crackme01_32bit")

for i, symb in enumerate(binary.static_symbols):
    symb.name = "zzz_%d" % i

binary.write("crackme01_32bit.obfuscated")
```

В результате получим:

```bash
$ readelf -s crackme01_32bit.obfuscated
...
Symbol table '.symtab' contains 78 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND zzz_0
     1: 08048154     0 SECTION LOCAL  DEFAULT    1 zzz_1
     2: 08048168     0 SECTION LOCAL  DEFAULT    2 zzz_2
     3: 08048188     0 SECTION LOCAL  DEFAULT    3 zzz_3
     4: 080481ac     0 SECTION LOCAL  DEFAULT    4 zzz_4
     5: 080481d0     0 SECTION LOCAL  DEFAULT    5 zzz_5
     6: 080482b0     0 SECTION LOCAL  DEFAULT    6 zzz_6
     7: 0804835a     0 SECTION LOCAL  DEFAULT    7 zzz_7
     8: 08048378     0 SECTION LOCAL  DEFAULT    8 zzz_8
     9: 080483b8     0 SECTION LOCAL  DEFAULT    9 zzz_9
    10: 080483c8     0 SECTION LOCAL  DEFAULT     10 zzz_10
...
```

## Подмена функций через PLT/GOT

Также известная как [ELF PLT INFECTION](http://phrack.org/issues/56/7.html).

Дабы не копипастить, просто оставим ссылки по теме:

  * [Перенаправление функций в разделяемых ELF-библиотеках](https://habr.com/ru/post/106107/)
  * [Infecting the plt/got with LIEF](https://lief.quarkslab.com/doc/latest/tutorials/05_elf_infect_plt_got.html)

## Изменить точку входа

Может быть полезно при создании патчей, установке хуков и прочей динамической инструментации, ну или для вызова скрытых функций. В качестве подопытного используем эльфа crackme01_32bit из [crackme01 by seveb](https://crackmes.one/crackme/5ab77f5e33c5d40ad448c78b)

### radare2

radare2 запускается в режиме записи (опция `-w`) — изменения будут внесены в оригинальный файл:

```bash
$ ./crackme01_32bit
Please enter the secret number: ^C

$ r2 -w -nn crackme01_32bit
[0x00000000]> .pf.elf_header.entry=0x0804860D
[0x00000000]> q

$ ./crackme01_32bit
Nope.
```

### LIEF

```python
import lief
```

```text
binary = lief.parse("crackme01_32bit")
header = binary.header
header.entrypoint = 0x0804860D
binary.write("crackme01_32bit.patched")
```

## Патчинг кода

В качестве простого подопытного возьмём крякми [novn91's crackmepal](https://crackmes.one/crackme/5ccecc7e33c5d4419da559b3). При запуске без параметров программка выводит:

```bash
$ ./crackmeMario
usage <password>
```

При запуске с параметром-произвольной строкой выдаётся:

```text
./crackmeMario qwerty
try again pal.
```

Сделаем патч, чтобы программа сразу при запуске выводила сообщение «good job! now keygen me!»

### radare2

radare2 умеет патчить любые форматы, которые сам поддерживает. При этом имеется возможность описывать патчи в текстовом формате:

```c
# Rapatch for https://crackmes.one/crackme/5ccecc7e33c5d4419da559b3
!echo Patching crackme
0x115D : jmp 0x1226
```

Применить такой патч можно командой:

```bash
$ r2 -P patch.txt crackmeMario
```

Почитать про патчинг кода через radare2:

  * [Binary Patching Using Radare2 by wolfshirtz](https://rayoflightz.github.io/linux/assembly/2019/03/26/Binary-patching-using-radare2.html)
  * [Radare2 Explorations. Tutorial 1 — Simple Patch](https://monosource.gitbooks.io/radare2-explorations/content/tut1/tut1_-_simple_patch.html)
  * [Ground Zero: Part 3-2 – Reverse Engineering – Patching Binaries with Radare2 – ARM64](https://scriptdotsh.com/index.php/2018/08/13/reverse-engineering-patching-binaries-with-radare2-arm-aarch64/)

### LIEF

LIEF позволяет патчить эльф (перезаписать байты) по указанному виртуальному адресу. Патч может быть в виде массива байт или в виде целочисленного значения:

```python
import lief
binary = lief.parse("crackmeMario")
binary.patch_address(0x115D, bytearray(b"\xe9\xc4\x00\x00\x00"))
binary.write("crackmeMario.patched")
```

После применения патча программа будет выводить:

```bash
$ ./crackmeMario.patched
good job! now keygen me!
```

## Добавить секцию в ELF

### objcopy

_objcopy_ позволяет добавить секцию, но эта секция не будет относиться ни к одному сегменту и не будет загружаться в ОЗУ при запуске приложения:

```bash
$ objcopy --add-section .testme=data.zip \
   --set-section-flags .testme=alloc,contents,load,readonly \
   --change-section-address .testme=0x08777777 \
   simple simple.patched.elf
```

### LIEF

Библиотека LIEF позволяет добавить новую секцию и соответствующий ей сегмент (флаг **`loaded=True`**) в имеющийся ELF:

```python
import lief
```

```text
binary  = lief.parse("simple")
data = bytearray(b"\xFF" * 16)

section = lief.ELF.Section(".testme", lief.ELF.SECTION_TYPES.PROGBITS)
section += lief.ELF.SECTION_FLAGS.EXECINSTR
section += lief.ELF.SECTION_FLAGS.ALLOC
section.content = data

binary.add(section, loaded=True)
binary.write("simple.testme.lief")
```

## Изменить секцию

### objcopy

_objcopy_ позволяет заменить содержимое секции данными из файла, а также изменить виртуальный адрес секции и флаги:

```bash
$ objcopy --update-section .testme=patch.bin \
    --change-section-address .testme=0x08999999
    simple simple.testme.elf
```

### LIEF

```python
import lief
```

```text
binary  = lief.parse("simple")
data = bytearray(b"\xFF" * 17)

section = binary.get_section(".text")
section.content = data

binary.write("simple.patched")
```

## Удалить секцию

### objcopy

_objcopy_ позволяет удалить определённую секцию по имени:

```bash
$ objcopy --remove-section .testme simple.testme.elf simple.no_testme.elf
```

### LIEF

Удаление секции с использованием библиотеки LIEF выглядит так:

```python
import lief
binary = lief.parse("simple.testme.elf")
binary.remove_section(".testme")
binary.write("simple.no_testme")
```

## Эльф-контейнер

Рецепт навеян статьёй [Гремлины и ELFийская магия: а что, если ELF-файл — это контейнер?](https://habr.com/ru/company/neobit/blog/332918/). Встречаются также man’ы про утилиту [elfwrap](https://docs.oracle.com/cd/E36784_01/html/E36870/elfwrap-1.html) родом из Solaris, которая позволяет создавать ELF-файл из произвольных данных, а формат ELF используется просто как контейнер.

Попробуем сделать то же самое на Python и LIEF.
К сожалению, на данный момент библиотека LIEF не умеет создавать эльф-файл c нуля, поэтому нужно ей помочь — создать пустой ELF-шаблон:

```bash
$ echo "" | gcc -m32 -fpic -o empty.o -c -xc -
$ gcc -m32 -shared -o libempty.so empty.o
```

Теперь можно использовать этот шаблон для наполнения данными:

```python
import lief
```

```text
binary = lief.parse("libempty.so")
filename = "crackme.zip"
data = open(filename, 'rb').read()

# Add section with zip-archive as content
section = lief.ELF.Section()
section.content = data
section.name = ".%s"%filename
binary.add(section, loaded=True)

# Add symbol as a reference to zip-archive
symb = lief.ELF.Symbol()
symb.type = lief.ELF.SYMBOL_TYPES.OBJECT
symb.binding = lief.ELF.SYMBOL_BINDINGS.GLOBAL
symb.size = len(data)
symb.name = filename
symb.value = section.virtual_address
binary.add_static_symbol(symb)

binary.write("libdata.crackme.container")
```

## Эльф «с прицепом»

ELF-формат не накладывает ограничений на данные, которые есть в файле, но не входят ни в один сегмент. Таким образом, можно создать исполняемый файл, у которого после ELF-структуры будет храниться _что-то_. Это _что-то_ не будет загружаться в ОЗУ при исполнении, но оно будет записано на диске, и в любой момент это _что-то_ можно с диска прочитать.

  * _IDA Pro не будет учитывать эти данные при анализе_

_Пример структуры файла «с прицепом»_
![image](/images/cee148406990828e85c5145ec842d7ea.png)

### radare2

Наличие «прицепа» можно установить, если сравнить реальный и вычисленный размер файла:

```bash
$ radare2 test.elf
[0x00001040]> ?v $s
0x40c1
[0x00001040]> iZ
14699
```

### readelf

_readelf_ не показывает информацию о наличии «прицепа», но можно вычислить вручную:

```bash
$ ls -l test.elf

# Размер файла 16577 байт

$ readelf -h test.elf
Start of section headers    e_shoff     14704
Size of section headers     e_shentsize 64
Number of section headers   e_shnum     29

# Размер ELF-структуры: e_shoff + ( e_shentsize * e_shnum ) = 16560
```

### LIEF

Библиотека LIEF позволяет как проверить наличие «прицепа», так и добавить его. С использованием LIEF всё выглядит достаточно лаконично:

```python
import lief
```

```text
binary  = lief.parse("test")
```

```python
# check if overlay exists
print('ELF has overlay data') if binary.has_overlay else print("No overlay data")
```

```text
# add overlay data to ELF
data = bytearray(b'\xFF'*17)
binary.overlay = data

binary.write('test.overlay')
```

## Эльф из пустоты (ELF from scratch)

На просторах интернета можно найти проекты по созданию ELF-файла «вручную» — без использования компилятора и линковщика под общим названием «ELF from scratch»:

  * [Проект на Github](https://github.com/statusfailed/elf-from-scratch)
  * Статья [Elf from scratch](https://www.conradk.com/codebase/2017/05/28/elf-from-scratch/)
  * Ветка [elf_from_scratch](https://github.com/lief-project/LIEF/tree/elf_from_scratch) в репозитории библиотеки LIEF

Знакомство с этими проектами благотворно влияет на впитывание в себя формата ELF.

## Самый маленький эльф

Интересные эксперименты с минимизацией размера эльфа описаны в статьях:

  * [A Whirlwind Tutorial on Creating Really Teensy ELF Executables for Linux](http://www.muppetlabs.com/~breadbox/software/tiny/teensy.html)
  * [A Whirlwind Tutorial on Creating Somewhat Teensy ELF Executables for Linux](http://www.muppetlabs.com/~breadbox/software/tiny/somewhat.html)
  * [Минималистичная программа в формате ELF](https://habr.com/ru/post/137706/)

Если кратко, загрузчик эльфа в ОС использует далеко не все поля заголовка и таблицы сегментов, при этом некоторый минимальный исполняемый код можно поместить прямо в структуру заголовка ELF’а (код взят из первой статьи):

```text
; tiny.asm

  BITS 32

     org     0x00010000
     db      0x7F, "ELF"             ; e_ident
     dd      1                                       ; p_type
     dd      0                                       ; p_offset
     dd      $$                                      ; p_vaddr
     dw      2                       ; e_type        ; p_paddr
     dw      3                       ; e_machine
     dd      _start                  ; e_version     ; p_filesz
     dd      _start                  ; e_entry       ; p_memsz
     dd      4                       ; e_phoff       ; p_flags
  _start:
     mov     bl, 42                  ; e_shoff       ; p_align
     xor     eax, eax
     inc     eax                     ; e_flags
     int     0x80
     db      0
     dw      0x34                    ; e_ehsize
     dw      0x20                    ; e_phentsize
     db      1                       ; e_phnum
                                     ; e_shentsize
                                     ; e_shnum
                                     ; e_shstrndx
  filesize      equ     $ - $$
```

Ассемблируем и получаем ELF размером… **45 байт** :

```bash
  $ nasm -f bin -o a.out tiny.asm
  $ chmod +x a.out
  $ ./a.out ; echo $?
  42
  $ wc -c a.out
       45 a.out
```

## Эльф по шаблону

Для создания эльфа с использованием библиотеки LIEF можно сделать следующие шаги (см. рецепт «Эльф-контейнер»):

  * взять простой ELF-файл в качестве шаблона;
  * заменить содержимое секций, добавить новые секции;
  * настроить необходимые параметры (точка входа, флаги).

# Вместо заключения

Дописывая статью, обнаружили, что получилось что-то вроде оды библиотеке LIEF. Но так не было запланировано — хотелось показать способы работы с ELF-файлами с использованием разных инструментов.

Наверняка есть или нужны сценарии, которые не были упомянуты здесь — напишите об этом в комментариях.

# Ссылки и литература

  * [Спецификация формата ELF](http://www.skyfree.org/linux/references/ELF_Format.pdf)
  * [Ещё спецификация формата в библиотеке Oracle](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-46512.html#scrolltoc)
  * [Работа с ELF’ами с использованием radare2](https://www.radare.org/doc/elf-tutorial)
  * [Документация библиотеки LIEF](https://lief.quarkslab.com/doc/latest/index.html)
  * [Примеры использования библиотеки LIEF](https://github.com/lief-project/LIEF/tree/master/examples)
  * Книга «PRACTICAL BINARY ANALYSIS», Dennis Andriesse
  * Книга «Learning Linux Binary Analysis», Ryan "elfmaster" O'Neill

**********

[Linux](/tags/linux.md)
[elf](/tags/elf.md)
