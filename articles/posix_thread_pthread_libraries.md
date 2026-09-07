# Библиотеки потоков POSIX (pthread)

Источник: [POSIX thread (pthread) libraries](https://www.cs.cmu.edu/afs/cs/academic/class/15492-f07/www/pthreads.html)

Библиотеки потоков POSIX — это основанный на стандартах API потоков для C/C++. Он позволяет порождать новый конкурентный поток выполнения процесса. Наиболее эффективен на мультипроцессорных или многоядерных системах, где поток выполнения может быть запланирован на другой процессор, получая таким образом ускорение за счёт параллельной или распределённой обработки. Потоки требуют меньше накладных расходов, чем «форк» (forking) или порождение нового процесса, потому что система не инициализирует новое пространство виртуальной памяти и окружение для процесса. Хотя наибольшая эффективность достигается на мультипроцессорных системах, выигрыш есть и на однопроцессорных системах, которые используют задержки в вводе-выводе и других системных функциях, которые могут приостановить выполнение процесса. (Один поток может выполняться, пока другой ждёт ввода-вывода или какой-то другой системной задержки.) Технологии параллельного программирования, такие как MPI и PVM, используются в среде распределённых вычислений, тогда как потоки ограничены единственной компьютерной системой. Все потоки внутри процесса разделяют одно и то же адресное пространство. Поток порождается определением функции и её аргументов, которые будут обработаны в потоке. Цель использования библиотеки потоков POSIX в вашем ПО — заставить ПО выполняться быстрее.

## Основы потоков

- Операции с потоками включают создание потока, завершение, синхронизацию (join, блокировка), планирование, управление данными и взаимодействие процессов.
- Поток не ведёт список созданных потоков, а также не знает поток, который его создал.
- Все потоки внутри процесса разделяют одно и то же адресное пространство.
- Потоки в одном процессе разделяют:

```text
* Process instructions
* Most data
* open files (descriptors)
* signals and signal handlers
* current working directory
* User and group id
```

- Каждый поток имеет уникальные:

```text
* Thread ID
* set of registers, stack pointer
* stack for local variables, return addresses
* signal mask
* priority
* Return value: `errno`
```

- Функции pthread возвращают «0» при успехе.

## Создание и завершение потоков

Пример: `pthread1.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void *print_message_function( void *ptr );

main()
{
     pthread_t thread1, thread2;
     char *message1 = "Thread 1";
     char *message2 = "Thread 2";
     int  iret1, iret2;

    /* Create independent threads each of which will execute function */

     iret1 = pthread_create( &thread1, NULL, print_message_function, (void*) message1);
     iret2 = pthread_create( &thread2, NULL, print_message_function, (void*) message2);

     /* Wait till threads are complete before main continues. Unless we  */
     /* wait we run the risk of executing an exit which will terminate   */
     /* the process and all threads before the threads have completed.   */

     pthread_join( thread1, NULL);
     pthread_join( thread2, NULL);

     printf("Thread 1 returns: %d\n",iret1);
     printf("Thread 2 returns: %d\n",iret2);
     exit(0);
}

void *print_message_function( void *ptr )
{
     char *message;
     message = (char *) ptr;
     printf("%s \n", message);
}
```

Компиляция:

- Компилятор C: `cc -lpthread pthread1.c`
или
- Компилятор C++: `g++ -lpthread pthread1.c`

Запуск: `./a.out`
Результаты:

```text
Thread 1
Thread 2
Thread 1 returns: 0
Thread 2 returns: 0
```

Детали:

- В этом примере в каждом потоке используется одна и та же функция. Аргументы разные. Функции не обязаны совпадать.

- Потоки завершаются явным вызовом `pthread_exit`, выходом из функции через return или вызовом функции `exit`, который завершит процесс, включая все потоки.

- Вызов функции: `pthread_create`

```text
    int pthread_create(pthread_t * thread,
                           const pthread_attr_t * attr,
                           void * (*start_routine)(void *),
                           void *arg);
```

Аргументы:

```text
* `thread` - returns the thread id. (unsigned long int defined in bits/pthreadtypes.h)
* `attr` - Set to NULL if default thread attributes are used. (else define members of the struct `pthread_attr_t` defined in bits/pthreadtypes.h) Attributes include:
  * detached state (joinable? Default: PTHREAD_CREATE_JOINABLE. Other option: PTHREAD_CREATE_DETACHED)
  * scheduling policy (real-time? PTHREAD_INHERIT_SCHED,PTHREAD_EXPLICIT_SCHED,SCHED_OTHER)
  * scheduling parameter
  * inheritsched attribute (Default: PTHREAD_EXPLICIT_SCHED Inherit from parent thread: PTHREAD_INHERIT_SCHED)
  * scope (Kernel threads: PTHREAD_SCOPE_SYSTEM User threads: PTHREAD_SCOPE_PROCESS Pick one or the other not both.)
  * guard size
  * stack address (See unistd.h and bits/posix_opt.h _POSIX_THREAD_ATTR_STACKADDR)
  * stack size (default minimum PTHREAD_STACK_SIZE set in pthread.h),
* `void * (*start_routine)` - pointer to the function to be threaded. Function has a single argument: pointer to void.
* `*arg` - pointer to argument of function. To pass multiple arguments, send a pointer to a structure.
```

- Вызов функции: `pthread_exit`

```text
    void pthread_exit(void *retval);
```

Аргументы:

```text
* `retval` - Return value of thread.
```

Эта процедура убивает поток. Функция `pthread_exit` никогда не возвращается. Если поток не отсоединён (detached), идентификатор потока и возвращаемое значение могут быть рассмотрены из другого потока с помощью pthread_join.
Примечание: возвращаемый указатель `*retval` не должен иметь локальной области видимости, иначе он перестанет существовать после завершения потока.

- [Подводные камни C++]: приведённая выше примерная программа **скомпилируется** компиляторами GNU C **и** C++ `g++`. Следующее ниже представление указателя на функцию будет работать для C, но не для C++. Обратите внимание на тонкие различия и избегайте приведённого ниже подводного камня:

```text
    void print_message_function( void *ptr );
        ...
        ...
        iret1 = pthread_create( &thread1, NULL, (void*)&print_message_function, (void*) message1);
        ...
        ...
```

## Синхронизация потоков

Библиотека потоков предоставляет три механизма синхронизации:

- mutex (мьютексы) — блокировка взаимного исключения: блокирует другим потокам доступ к переменным. Это обеспечивает исключительный доступ потока к переменной или набору переменных.
- join (присоединения) — заставляют поток ждать завершения (terminated) других.
- условные переменные — тип данных `pthread_cond_t`

### Мьютексы

Мьютексы используются для предотвращения несогласованности данных из-за гонок (race conditions). Гонка часто возникает, когда двум или более потокам нужно выполнить операции над одной и той же областью памяти, но результаты вычислений зависят от порядка, в котором эти операции выполняются. Мьютексы используются для сериализации доступа к разделяемым ресурсам. Всякий раз, когда к глобальному ресурсу обращается более чем один поток, с ним должен быть связан мьютекс. Можно применить мьютекс для защиты сегмента памяти («критической области») от других потоков. Мьютексы можно применять только к потокам в одном процессе, и они не работают между процессами, как семафоры.

Пример потоковой функции:

Без мьютекса:

```c
int counter=0;

/* Function C */
void functionC()
{
   counter++

}
```

С мьютексом:

```c
/* Note scope of variable and mutex are the same */
pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
int counter=0;

/* Function C */
void functionC()
{
   pthread_mutex_lock( &mutex1 );
   counter++
   pthread_mutex_unlock( &mutex1 );
}
```

Возможная последовательность выполнения:

| Thread 1 | Thread 2 | Thread 1 | Thread 2 |
|---|---|---|---|
| counter = 0 | counter = 0 | counter = 0 | counter = 0 |
| counter = 1 | counter = 1 | counter = 1 | Thread 2 locked out. Thread 1 has exclusive use of variable `counter` |
| | | | counter = 2 |

Если операции загрузки и сохранения регистра для инкрементирования переменной `counter` произойдут с неудачным таймингом, теоретически возможно, что каждый поток инкрементирует и перезаписывает одну и ту же переменную одним и тем же значением. Другая возможность — поток два сначала инкрементирует `counter`, блокируя поток один до завершения, а затем поток один инкрементирует его до 2.

| Sequence | Thread 1 | Thread 2 |
|---|---|---|
| 1 | counter = 0 | counter=0 |
| 2 | Thread 1 locked out. Thread 2 has exclusive use of variable `counter` | counter = 1 |
| 3 | counter = 2 | |

Листинг кода: `mutex1.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void *functionC();
pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
int  counter = 0;

main()
{
   int rc1, rc2;
   pthread_t thread1, thread2;

   /* Create independent threads each of which will execute functionC */

   if( (rc1=pthread_create( &thread1, NULL, &functionC, NULL)) )
   {
      printf("Thread creation failed: %d\n", rc1);
   }

   if( (rc2=pthread_create( &thread2, NULL, &functionC, NULL)) )
   {
      printf("Thread creation failed: %d\n", rc2);
   }

   /* Wait till threads are complete before main continues. Unless we  */
   /* wait we run the risk of executing an exit which will terminate   */
   /* the process and all threads before the threads have completed.   */

   pthread_join( thread1, NULL);
   pthread_join( thread2, NULL);

   exit(0);
}

void *functionC()
{
   pthread_mutex_lock( &mutex1 );
   counter++;
   printf("Counter value: %d\n",counter);
   pthread_mutex_unlock( &mutex1 );
}
```

Компиляция: `cc -lpthread mutex1.c`
Запуск: `./a.out`
Результаты:

```text
Counter value: 1
Counter value: 2
```

Когда попытка захвата мьютекса выполняется против мьютекса, удерживаемого другим потоком, поток блокируется, пока мьютекс не будет освобождён. Когда поток завершается, мьютекс — нет, если его явно не разблокировать. По умолчанию ничего не происходит.

### Присоединения (Joins)

Join выполняется, когда нужно дождаться завершения потока. Вызывающая процедура может запустить несколько потоков, а затем дождаться их завершения, чтобы получить результаты. Дожидаются завершения потоков с помощью join.

Пример кода: `join1.c`

```c
#include <stdio.h>
#include <pthread.h>

#define NTHREADS 10
void *thread_function(void *);
pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
int  counter = 0;

main()
{
   pthread_t thread_id[NTHREADS];
   int i, j;

   for(i=0; i < NTHREADS; i++)
   {
      pthread_create( &thread_id[i], NULL, thread_function, NULL );
   }

   for(j=0; j < NTHREADS; j++)
   {
      pthread_join( thread_id[j], NULL);
   }

   /* Now that all threads are complete I can print the final result.     */
   /* Without the join I could be printing a value before all the threads */
   /* have been completed.                                                */

   printf("Final counter value: %d\n", counter);
}

void *thread_function(void *dummyPtr)
{
   printf("Thread number %ld\n", pthread_self());
   pthread_mutex_lock( &mutex1 );
   counter++;
   pthread_mutex_unlock( &mutex1 );
}
```

Компиляция: `cc -lpthread join1.c`
Запуск: `./a.out`
Результаты:

```text
Thread number 1026
Thread number 2051
Thread number 3076
Thread number 4101
Thread number 5126
Thread number 6151
Thread number 7176
Thread number 8201
Thread number 9226
Thread number 10251
Final counter value: 10
```

### Условные переменные

Условная переменная — это переменная типа `pthread_cond_t`, используемая с соответствующими функциями для ожидания и последующего продолжения процесса. Механизм условных переменных позволяет потокам приостановить выполнение и освободить процессор, пока некоторое условие не станет истинным. Условная переменная всегда должна быть связана с мьютексом, чтобы избежать гонки, создаваемой одним потоком, готовящимся ждать, и другим потоком, который может просигналить условие до того, как первый поток действительно начнёт на нём ждать, что приведёт к deadlock. Поток будет вечно ждать сигнал, который никогда не будет отправлен. Можно использовать любой мьютекс — явной связи между мьютексом и условной переменной нет.

Функции, используемые в сочетании с условной переменной:

- Создание/уничтожение:

```c
* pthread_cond_init
* pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
* pthread_cond_destroy
```

- Ожидание условия:

```c
* pthread_cond_wait
* pthread_cond_timedwait - place limit on how long it will block.
```

- Пробуждение потока по условию:

```c
* pthread_cond_signal
* pthread_cond_broadcast - wake up all threads blocked by the specified condition variable.
```

Пример кода: `cond1.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

pthread_mutex_t count_mutex     = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t condition_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  condition_cond  = PTHREAD_COND_INITIALIZER;

void *functionCount1();
void *functionCount2();
int  count = 0;
#define COUNT_DONE  10
#define COUNT_HALT1  3
#define COUNT_HALT2  6

main()
{
   pthread_t thread1, thread2;

   pthread_create( &thread1, NULL, &functionCount1, NULL);
   pthread_create( &thread2, NULL, &functionCount2, NULL);
   pthread_join( thread1, NULL);
   pthread_join( thread2, NULL);

   exit(0);
}

void *functionCount1()
{
   for(;;)
   {
      pthread_mutex_lock( &condition_mutex );
      while( count >= COUNT_HALT1 && count <= COUNT_HALT2 )
      {
         pthread_cond_wait( &condition_cond, &condition_mutex );
      }
      pthread_mutex_unlock( &condition_mutex );

      pthread_mutex_lock( &count_mutex );
      count++;
      printf("Counter value functionCount1: %d\n",count);
      pthread_mutex_unlock( &count_mutex );

      if(count >= COUNT_DONE) return(NULL);
    }
}

void *functionCount2()
{
    for(;;)
    {
       pthread_mutex_lock( &condition_mutex );
       if( count < COUNT_HALT1 || count > COUNT_HALT2 )
       {
          pthread_cond_signal( &condition_cond );
       }
       pthread_mutex_unlock( &condition_mutex );

       pthread_mutex_lock( &count_mutex );
       count++;
       printf("Counter value functionCount2: %d\n",count);
       pthread_mutex_unlock( &count_mutex );

       if(count >= COUNT_DONE) return(NULL);
    }

}
```

Компиляция: `cc -lpthread cond1.c`
Запуск: `./a.out`
Результаты:

```text
Counter value functionCount1: 1
Counter value functionCount1: 2
Counter value functionCount1: 3
Counter value functionCount2: 4
Counter value functionCount2: 5
Counter value functionCount2: 6
Counter value functionCount2: 7
Counter value functionCount1: 8
Counter value functionCount1: 9
Counter value functionCount1: 10
Counter value functionCount2: 11
```

Обратите внимание, что `functionCount1()` была приостановлена, пока count находился между значениями COUNT_HALT1 и COUNT_HALT2. Единственное, что здесь гарантируется, — что `functionCount2` будет инкрементировать счётчик, пока значение находится между COUNT_HALT1 и COUNT_HALT2. Всё остальное случайно.

Логические условия (операторы «if» и «while») должны быть выбраны так, чтобы гарантировать выполнение «signal», если «wait» когда-либо обрабатывается. Плохая логика программы также может привести к состоянию deadlock.

Примечание: В этом примере полно гонок, потому что count используется как условие и не может быть заблокирован в операторе while без вызова deadlock. Я поработаю над более чистым примером, но это пример условной переменной.

## Планирование потоков

Когда эта опция включена, каждый поток может иметь свои собственные свойства планирования. Атрибуты планирования могут быть заданы:

- при создании потока
- динамически, изменением атрибутов уже созданного потока
- определением влияния мьютекса на планирование потока при создании мьютекса
- динамическим изменением планирования потока во время операций синхронизации.

Библиотека потоков предоставляет значения по умолчанию, достаточные для большинства случаев.

## Подводные камни потоков

- Гонки (race conditions): хотя код может появляться на экране в том порядке, в котором вы хотите, чтобы он выполнялся, потоки планируются операционной системой и исполняются в случайном порядке. Нельзя предполагать, что потоки выполняются в порядке их создания. Они также могут выполняться с разной скоростью. Когда потоки выполняются (соревнуясь за завершение), они могут давать неожиданные результаты (гонка). Мьютексы и join должны использоваться для достижения предсказуемого порядка выполнения и результата.

- Потокобезопасный код: потоковые процедуры должны вызывать функции, которые являются «потокобезопасными» (thread safe). Это значит, что нет статических или глобальных переменных, которые другие потоки могут затереть или прочитать в предположении однопоточной работы. Если статические или глобальные переменные используются, то должны применяться мьютексы или функции должны быть переписаны, чтобы избежать использования этих переменных. В C локальные переменные динамически выделяются на стеке. Следовательно, любая функция, не использующая статических данных или других разделяемых ресурсов, потокобезопасна. Непотокобезопасные функции могут использоваться одновременно только одним потоком в программе, и уникальность потока должна быть обеспечена. Многие непереентерабельные функции возвращают указатель на статические данные. Этого можно избежать, возвращая динамически выделенные данные или используя хранилище, предоставленное вызывающим. Пример непотокобезопасной функции — `strtok`, которая к тому же не переентерабельна. «Потокобезопасная» версия — переентерабельная версия `strtok_r`.

- Deadlock мьютекса: это условие возникает, когда мьютекс применён, но затем не «разблокирован». Это вызывает бесконечную остановку выполнения программы. Это также может быть вызвано неудачным применением мьютексов или join. Будьте осторожны, применяя два или более мьютексов к участку кода. Если первый pthread_mutex_lock применён, а второй pthread_mutex_lock провалился из-за того, что другой поток применил мьютекс, первый мьютекс может в итоге заблокировать всем остальным потокам доступ к данным, включая поток, который держит второй мьютекс. Потоки могут бесконечно ждать освобождения ресурса, что вызывает deadlock. Лучше протестировать, а при неудаче освободить ресурсы и подождать перед повторной попыткой.

```c
    ...
        pthread_mutex_lock(&mutex_1);
        while ( pthread_mutex_trylock(&mutex_2) )  /* Test if already locked   */
        {
           pthread_mutex_unlock(&mutex_1);  /* Free resource to avoid deadlock */
           ...
           /* stall here   */
           ...
           pthread_mutex_lock(&mutex_1);
        }
        count++;
        pthread_mutex_unlock(&mutex_1);
        pthread_mutex_unlock(&mutex_2);
        ...
```

Порядок применения мьютексов также важен. Следующий сегмент кода иллюстрирует потенциал deadlock:

```c
    void *function1()
        {
           ...
           pthread_mutex_lock(&lock1);           /* - Execution step 1  */
           pthread_mutex_lock(&lock2);           /* - Execution step 3 DEADLOCK!!!  */
           ...
           ...
           pthread_mutex_lock(&lock2);
           pthread_mutex_lock(&lock1);
           ...
        }

        void *function2()
        {
           ...
           pthread_mutex_lock(&lock2);           /* - Execution step 2  */
           pthread_mutex_lock(&lock1);
           ...
           ...
           pthread_mutex_lock(&lock1);
           pthread_mutex_lock(&lock2);
           ...
        }

        main()
        {
           ...
           pthread_create(&thread1, NULL, function1, NULL);
           pthread_create(&thread2, NULL, function1, NULL);
           ...
        }
```

Если `function1` захватит первый мьютекс, а `function2` — второй, все ресурсы связаны и заблокированы.

- Deadlock условной переменной: логические условия (операторы «if» и «while») должны быть выбраны так, чтобы гарантировать выполнение «signal», если «wait» когда-либо обрабатывается.

## Отладка потоков

- **GDB:**

```text
* GDB: Stopping and starting multi-thread programs - http://sources.redhat.com/gdb/current/onlinedocs/gdb_6.html#SEC43
* GDB/MI: Threads commands - http://sources.redhat.com/gdb/current/onlinedocs/gdb_25.html#SEC581
```

- **DDD:**

```text
* Examining Threads - http://www.gnu.org/manual/ddd/html_mono/ddd.html#Threads
```

## Man-страницы по потокам

- [pthread_atfork](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_atfork) — регистрирует обработчики, вызываемые в момент fork(2)
- [pthread_attr_destroy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_destroy) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_getdetachstate](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_getdetachstate) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_getinheritsched](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_getinheritsched) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_getschedparam](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_getschedparam) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_getschedpolicy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_getschedpolicy) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_getscope](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_getscope) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_setdetachstate](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_setdetachstate) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_setinheritsched](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_setinheritsched) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_setschedparam](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_setschedparam) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_setschedpolicy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_setschedpolicy) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_attr_setscope](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_setscope) / [pthread_attr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_attr_init) — атрибуты создания потока
- [pthread_cancel](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cancel) — отмена потока
- [pthread_cleanup_pop](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_pop) / [pthread_cleanup_push](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_push) — установка и удаление обработчиков очистки
- [pthread_cleanup_pop_restore_np](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_pop_restore_np) / [pthread_cleanup_push](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_push) — установка и удаление обработчиков очистки
- [pthread_cleanup_push](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_push) — установка и удаление обработчиков очистки
- [pthread_cleanup_push_defer_np](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_push_defer_np) / [pthread_cleanup_push](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cleanup_push) — установка и удаление обработчиков очистки
- [pthread_condattr_destroy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_condattr_destroy) / [pthread_condattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_condattr_init) — атрибуты создания условия
- [pthread_condattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_condattr_init) — атрибуты создания условия
- [pthread_cond_broadcast](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_broadcast) / [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_cond_destroy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_destroy) / [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_cond_signal](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_signal) / [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_cond_timedwait](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_timedwait) / [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_cond_wait](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_wait) / [pthread_cond_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cond_init) — операции над условиями
- [pthread_create](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_create) — создать новый поток
- [pthread_detach](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_detach) — перевести работающий поток в отсоединённое состояние
- [pthread_equal](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_equal) — сравнить два идентификатора потока
- [pthread_exit](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_exit) — завершить вызывающий поток
- [pthread_getschedparam](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_getschedparam) / [pthread_setschedparam](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_setschedparam) — управление параметрами планирования потока
- [pthread_getspecific](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_getspecific) / [pthread_key_create](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_key_create) — управление специфичными для потока данными
- [pthread_join](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_join) — дождаться завершения другого потока
- [pthread_key_create](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_key_create) — управление специфичными для потока данными
- [pthread_key_delete](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_key_delete) / [pthread_key_create](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_key_create) — управление специфичными для потока данными
- [pthread_kill_other_threads_np](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_kill_other_threads_np) — завершить все потоки в программе, кроме вызывающего
- [pthread_kill](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_kill) / [pthread_sigmask](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_sigmask) — обработка сигналов в потоках
- [pthread_mutexattr_destroy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_destroy) / [pthread_mutexattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_init) — атрибуты создания мьютекса
- [pthread_mutexattr_getkind_np](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_getkind_np) / [pthread_mutexattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_init) — атрибуты создания мьютекса
- [pthread_mutexattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_init) — атрибуты создания мьютекса
- [pthread_mutexattr_setkind_np](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_setkind_np) / [pthread_mutexattr_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutexattr_init) — атрибуты создания мьютекса
- [pthread_mutex_destroy](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_destroy) / [pthread_mutex_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_init) — операции над мьютексами
- [pthread_mutex_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_init) — операции над мьютексами
- [pthread_mutex_lock](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_lock) / [pthread_mutex_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_init) — операции над мьютексами
- [pthread_mutex_trylock](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_trylock) / [pthread_mutex_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_init) — операции над мьютексами
- [pthread_mutex_unlock](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_unlock) / [pthread_mutex_init](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_mutex_init) — операции над мьютексами
- [pthread_once](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_once) — однократная инициализация
- [pthread_self](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_self) — вернуть идентификатор текущего потока
- [pthread_setcancelstate](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_setcancelstate) / [pthread_cancel](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cancel) — отмена потока
- [pthread_setcanceltype](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_setcanceltype) / [pthread_cancel](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cancel) — отмена потока
- [pthread_setschedparam](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_setschedparam) — управление параметрами планирования потока
- [pthread_setspecific](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_setspecific) / [pthread_key_create](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_key_create) — управление специфичными для потока данными
- [pthread_sigmask](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_sigmask) — обработка сигналов в потоках
- [pthread_testcancel](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_testcancel) / [pthread_cancel](http://node1.yo-linux.com/cgi-bin/man2html?cgi_command=pthread_cancel) — отмена потока

## Ссылки

- [Fundamentals Of Multithreading](http://www.systemlogic.net/articles/01/6/multithreading/print.php) — Paul Mazzucco
- [Native Posix Thread Library for Linux](http://people.redhat.com/drepper/nptl-design.pdf)
- [Introduction to Programming Threads](http://www.mit.edu/people/proven/IAP_2000/index.html)
- [Getting Started With POSIX Threads](http://dis.cs.umass.edu/%7Ewagner/threads_html/tutorial.html)
- [ITS: Introduction to Threads](http://www.uwo.ca/its/doc/courses/notes/hpc/pthreads.html)
- [GNU Portable Threads](http://www.gnu.org/software/pth/)
- [Introduction of threads for Solaris, Linux, and Windows](http://www.northco.net/chenke/project/project2.html)
- [Comparison of thread implementations](http://members.aol.com/drbutenhof/ThreadTable.html)
- [comp.programming.threads FAQ](http://www.serpentine.com/%7Ebos/threads-faq/)
- [An in-depth description of PMPthread internal queue functions.](http://www.humanfactor.com/pthreads/mit-pthreads-queues.html)
- [Examples](http://www.csce.uark.edu/%7Eaapon/courses/os/examples/)
- [Pthreads tutorial and examples of thread problems](http://www.cs.nmsu.edu/%7Ejcook/Tools/pthreads/pthreads.html) — by Andrae Muys
- [Valgrind KDE thread checker: Helgrind](http://valgrind.kde.org/tools.html)
- [Sun's Multithreaded Programming Guide](http://docs.sun.com/?q=%22Multithreaded+Programming+Guide%22&p=/doc/802-5938) — не Linux, но хороший справочник.
- [FSU Pthreads (POSIX Threads)](http://www.informatik.hu-berlin.de/%7Emueller/pthreads/)
- [Linux-mag.com: Concurrent Programming Topics](http://www.linux-mag.com/2001-04/compile_01.html) — семафоры, условные переменные
- [Linux-mag.com: The Fibers of Threads](http://www.linux-mag.com/2001-05/compile_01.html) — обсуждение того, как работают потоки в Linux
- Независимые от платформы потоки:

```text
* Gnome GLib 2.0 threads - http://developer.gnome.org/doc/API/2.0/glib/glib-Threads.html - Thread abstraction; including mutexes, conditions and thread private data. example: http://developer.gnome.org/doc/API/2.0/gdk/gdk-Threads.html
* OmniORB (CORBA) Thread Library - http://omniorb.sourceforge.net/omni40/omnithread.html
* zThreads - http://zthread.sourceforge.net/
```

- **Классы потоков C++:**

```text
* GNU: Common C++ - http://www.gnu.org/software/commoncpp/ - support for threading, sockets, file access, daemons, persistence, serial I/O, XML parsing and system services
* ACE: Adaptive Communication Environment - http://www.cs.wustl.edu/%7Eschmidt/ACE.html - C++ interface
  * ACE programmers guide: pdf (see page 29 for threads) - http://www.cs.wustl.edu/%7Eschmidt/PDF/ACE-tutorial.pdf
  * Thread management examples using ACE - http://www.cs.wustl.edu/%7Eschmidt/ACE_wrappers/docs/tutorials/Chap_4/ex01.html
* Hood - http://www.cs.utexas.edu/users/hood/ - A C++ Threads Library for Multiprogrammed Multiprocessors
* C++ Thread classes - http://threads.sourceforge.net/ - sourceforge
* QpThread - http://lin.fsid.cvut.cz/%7Ekra/index.html#QpThread
```

Группы новостей:

- comp.programming.threads
- comp.unix.solaris

## Книги

- **Pthreads Programming: A POSIX Standard for Better Multiprocessing**
  Брэдфорд Николс, Дик Баттлар, Жаклин Пру Фаррелл
  ISBN #1-56592-115-1, O'Reilly

- **Programming with POSIX(R) Threads**
  Дэвид Р. Бутенхоф
  ISBN #0201633922, Addison Wesley Pub. Co.

- **C++ Network Programming Volume 1**
  Дуглас К. Шмидт, Стивен Д. Хьюстон
  ISBN #0201604647, Addison Wesley Pub. Co. Рассматривает открытый фреймворк ACE (ADAPTIVE Communication Environment) в части потоков и других тем.

**********

[posix](/tags/posix.md)
[threads](/tags/threads.md)
[linux](/tags/linux.md)