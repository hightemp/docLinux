# Загадка Linux: linux-vdso.so.1

Источник: [Linux Mystery: linux-vdso.so.1](http://austinkeeley.com/2021/04/25/linux-mystery-vsdo.html)

25 апреля 2021

Каждый раз, когда я компилирую и компоную Linux-бинарник, я вижу динамически связанную библиотеку под названием `linux-vdso.so.1`.

```c
[austin@localhost]$ cat hello.c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Hello, World!\n");
    return 0;
}
[austin@localhost]$ gcc -o hello hello.c
[austin@localhost]$ ldd hello
	linux-vdso.so.1 (0x00007ffee39dd000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f91baaec000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f91bad03000)
```

Про libc и ld-linux я знаю, но кто такой этот linux-vdso? Есть man-страница, которая его описывает.

```text
The  "vDSO" (virtual dynamic shared object) is a small shared library that the
kernel automatically maps into the address space of all user-space applications.
Applications usually do not need to concern themselves with these details as the
vDSO is most commonly called by the C library.

...

Why  does  the  vDSO exist at all?  There are some system calls the kernel provides
that user-space code ends up using frequently, to the point that such calls can
dominate overall performance.  This is due both to the frequency of the call as
well as the context-switch overhead that results from exiting user space and
entering the kernel.

The rest of this documentation is geared toward the curious and/or C library writers
rather than general developers.  If you're trying to call the vDSO in your own
application rather than using the C library, you're most likely doing it wrong.
```

Хм. Занятно. Мы приносим функциональность ядра в пользовательское пространство в виде разделяемого объекта (shared object).

В man-странице далее объясняется, что выполнение системных вызовов — дорогое удовольствие, поскольку нужно делать переключение контекста (context switch) в ядро и обратно, а некоторые системные вызовы вполне можно было бы реализовать как функции пользовательского пространства, и это сэкономило бы нам кучу времени.

Мне это показалось подозрительным. Разве не в этом смысл системного вызова — чётко разделять код пользовательского пространства и код ядра? Какие системные вызовы я теперь тащу в своё пользовательское пространство?

На самом деле их всего четыре (на x86-64):

* `clock_gettime`
* `getcpu`
* `gettimeofday`
* `time`

Чтобы убедиться, я дампил содержимое памяти процесса в том месте, где находится vdso.

```text
[austin@localhost]$ gdb -q ./hello
Reading symbols from ./hello...
(No debugging symbols found in ./hello)
(gdb) b main
Breakpoint 1 at 0x1149
(gdb) r
Starting program: /home/austin/projects/elf-collection/hello

Breakpoint 1, 0x0000555555555149 in main ()
(gdb) info proc map
process 132181
Mapped address spaces:

          Start Addr           End Addr       Size     Offset objfile
      0x555555554000     0x555555555000     0x1000        0x0 /home/austin/projects/elf-collection/hello
      0x555555555000     0x555555556000     0x1000     0x1000 /home/austin/projects/elf-collection/hello
      0x555555556000     0x555555557000     0x1000     0x2000 /home/austin/projects/elf-collection/hello
      0x555555557000     0x555555558000     0x1000     0x2000 /home/austin/projects/elf-collection/hello
      0x555555558000     0x555555559000     0x1000     0x3000 /home/austin/projects/elf-collection/hello
      0x7ffff7db4000     0x7ffff7db6000     0x2000        0x0
      0x7ffff7db6000     0x7ffff7ddc000    0x26000        0x0 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7ddc000     0x7ffff7f49000   0x16d000    0x26000 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7f49000     0x7ffff7f95000    0x4c000   0x193000 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7f95000     0x7ffff7f96000     0x1000   0x1df000 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7f96000     0x7ffff7f99000     0x3000   0x1df000 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7f99000     0x7ffff7f9c000     0x3000   0x1e2000 /usr/lib/x86_64-linux-gnu/libc-2.32.so
      0x7ffff7f9c000     0x7ffff7fa2000     0x6000        0x0
      0x7ffff7fc8000     0x7ffff7fcc000     0x4000        0x0 [vvar]
      0x7ffff7fcc000     0x7ffff7fce000     0x2000        0x0 [vdso]
      0x7ffff7fce000     0x7ffff7fcf000     0x1000        0x0 /usr/lib/x86_64-linux-gnu/ld-2.32.so
      0x7ffff7fcf000     0x7ffff7ff3000    0x24000     0x1000 /usr/lib/x86_64-linux-gnu/ld-2.32.so
      0x7ffff7ff3000     0x7ffff7ffc000     0x9000    0x25000 /usr/lib/x86_64-linux-gnu/ld-2.32.so
      0x7ffff7ffc000     0x7ffff7ffd000     0x1000    0x2d000 /usr/lib/x86_64-linux-gnu/ld-2.32.so
      0x7ffff7ffd000     0x7ffff7fff000     0x2000    0x2e000 /usr/lib/x86_64-linux-gnu/ld-2.32.so
      0x7ffffffde000     0x7ffffffff000    0x21000        0x0 [stack]
  0xffffffffff600000 0xffffffffff601000     0x1000        0x0 [vsyscall]
(gdb) dump binary memory vdso.so 0x7ffff7fcc000     0x7ffff7fce000
(gdb) q
```

Это действительно просто ELF so-файл!

```text
[austin@localhost]$ file vdso.so
vdso.so: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=112feb4b14e301806a8eafdcdd804c88bfa191d8, stripped
```

И вот функции, как и ожидалось:

```text
[austin@localhost]$ objdump -T vdso.so

vdso.so:     file format elf64-x86-64

DYNAMIC SYMBOL TABLE:
0000000000000bc0  w   DF .text	0000000000000005  LINUX_2.6   clock_gettime
0000000000000b80 g    DF .text	0000000000000005  LINUX_2.6   __vdso_gettimeofday
0000000000000bd0  w   DF .text	0000000000000060  LINUX_2.6   clock_getres
0000000000000bd0 g    DF .text	0000000000000060  LINUX_2.6   __vdso_clock_getres
0000000000000b80  w   DF .text	0000000000000005  LINUX_2.6   gettimeofday
0000000000000b90 g    DF .text	0000000000000029  LINUX_2.6   __vdso_time
0000000000000b90  w   DF .text	0000000000000029  LINUX_2.6   time
0000000000000bc0 g    DF .text	0000000000000005  LINUX_2.6   __vdso_clock_gettime
0000000000000000 g    DO *ABS*	0000000000000000  LINUX_2.6   LINUX_2.6
0000000000000c30 g    DF .text	0000000000000025  LINUX_2.6   __vdso_getcpu
0000000000000c30  w   DF .text	0000000000000025  LINUX_2.6   getcpu
```

Кажется странным, что вывод `ldd` не показывает so-файл на диске, который динамически загружается, — но это приходит из ядра, а файлы на диске — это уже скорее забота user land.

Давайте убедимся, что мы не выполняем системный вызов, реально используя одну из этих функций vdso.

```c
[austin@localhost]$ cat hello-vdso.c
#include <stdio.h>
#include <sys/time.h>

int main(int argc, char *argv[]) {
    struct timeval t;
    gettimeofday(&t, NULL);
    printf("Seconds: %lu\n", t.tv_sec);
    return 0;
}
```

Мы можем использовать `strace`, чтобы увидеть, какие системные вызовы выполняются. В этом случае мы _не_ должны увидеть системный вызов `gettimeofday`.

```text
[austin@localhost]$ strace ./hello-vdso 2>&1 | grep "gettimeofday\|write"
write(1, "Seconds: 1619316657\n", 20Seconds: 1619316657
```

Должно быть, мы используем версию из VDSO. Следующий мой вопрос — можно ли заставить системный вызов всё-таки произойти. Я не смог найти опцию GNU-линковщика, чтобы отключить её. Отключить можно общесистемно с помощью различных опций ядра, но не «для отдельного приложения» на этапе линковки. Я также думал, что статическая линковка сработает (раз уж VDSO показывается в `ldd`), но даже это не помогло. Ядро/glibc действительно хотят убедиться, что я использую оптимизированную версию!

Мне удалось проделать грязный хак: статически слинковать программу, а затем с помощью hex-редактора испортить строку `__vdso_gettimeofday`, чтобы glibc думал, что версия VDSO никогда не загружалась.

```text
[austin@localhost]$ strace ./hello-vdso 2>&1 | grep "gettimeofday\|write"
gettimeofday({tv_sec=1619316899, tv_usec=828106}, NULL) = 0
write(1, "Seconds: 1619316899\n", 20Seconds: 1619316899
```

Это был довольно глупый эксперимент, но хороший способ узнать, как ядро и user land взаимодействуют способами, о которых большинство людей особо не задумывается.

**********

[vdso](/tags/vdso.md)
[kernel](/tags/kernel.md)
[linux](/tags/linux.md)