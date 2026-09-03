# Сигналы (signal)

Источник: [Сигналы (signal) — конспект HSE CAOS по POSIX-сигналам: `signal`, `sigaction`, `kill`, `raise`, `alarm`, `pause`, стандартные `SIG*` и ссылки на лекции.](https://github.com/blackav/hse-caos-2020/blob/master/18-signal/README.md)

  * [ Notifications ](/login?return_to=%2Fblackav%2Fhse-caos-2020) You must be signed in to change notification settings
  * [ Fork 39 ](/login?return_to=%2Fblackav%2Fhse-caos-2020)
  * [ Star  141 ](/login?return_to=%2Fblackav%2Fhse-caos-2020)

  * [ Code ](/blackav/hse-caos-2020)
  * [ Issues 0 ](/blackav/hse-caos-2020/issues)
  * [ Pull requests 0 ](/blackav/hse-caos-2020/pulls)
  * [ Actions ](/blackav/hse-caos-2020/actions)
  * [ Projects ](/blackav/hse-caos-2020/projects)
  * [ Security and quality 0 ](/blackav/hse-caos-2020/security)
  * [ Insights ](/blackav/hse-caos-2020/pulse)

Additional navigation options

  * [ Code  ](/blackav/hse-caos-2020)
  * [ Issues  ](/blackav/hse-caos-2020/issues)
  * [ Pull requests  ](/blackav/hse-caos-2020/pulls)
  * [ Actions  ](/blackav/hse-caos-2020/actions)
  * [ Projects  ](/blackav/hse-caos-2020/projects)
  * [ Security and quality  ](/blackav/hse-caos-2020/security)
  * [ Insights  ](/blackav/hse-caos-2020/pulse)

## FilesExpand file tree

master

## Breadcrumbs

  1. [hse-caos-2020](/blackav/hse-caos-2020/tree/master)
  2. /[18-signal](/blackav/hse-caos-2020/tree/master/18-signal)

/

# README.md

Copy path

Blame

More file actions

Blame

More file actions

## Latest commit

## History

[History](/blackav/hse-caos-2020/commits/master/18-signal/README.md)

History

101 lines (77 loc) · 6.54 KB

master

## Breadcrumbs

  1. [hse-caos-2020](/blackav/hse-caos-2020/tree/master)
  2. /[18-signal](/blackav/hse-caos-2020/tree/master/18-signal)

/

# README.md

Copy path

Top

## File metadata and controls

  * Preview

  * Code

  * Blame

101 lines (77 loc) · 6.54 KB

[Raw](https://github.com/blackav/hse-caos-2020/raw/refs/heads/master/18-signal/README.md)

Copy raw file

Download raw file

Outline

Edit and raw actions

# Сигналы (signal)

## Описание

Сигналы – это программные прерывания. Сигналы предоставляют возможность обработки асинхронных событий – например, когда пользователь вводит символ прерывания, чтобы остановить программу, или когда одна из программ в конвейере аварийно завершается. Прежде всего, каждый сигнал имеет собственное имя. Имена всех сигналов начинаются с последовательности SIG. Все имена сигналов определены как константы с положительными числовыми значениями (номера сигналов) в заголовочном файле <signal.h>. Ни один сигнал не имеет номера 0. Функция kill использует номер сигнала 0 в особых случаях. Стандарт POSIX.1 называет такой сигнал null signal(пустой сигнал). Сигналы могут порождаться:

  * Терминалом (Control-C – приводит к генерации сигнала прерывания (SIGINT));
  * Аппаратные ошибки (деление на 0, ошибка доступа к памяти и т.п);
  * Программным обеспечением (Примерами таких сигналов могут служить SIGURG(посылается, когда через сетевое соединение приходят экстренные (out-of-band) данные), SIGPIPE(посылается пишущемупроцессу, когда он пытается записать данные в канал после завершенияпроцесса, читающего из канала) и SIGALRM(посылается процессу по истечении установленного им таймера).)
  * Другими процессами

Сигналы - пример асинхронных событий. Сигнал может быть передан процессу в любой момент времени. В случае появления сигнала мы можем запросить ядро произвести одно из трех действий. Они называются действиями, связанными с сигналом.

  *     1. Игнорировать сигнал. Это действие возможно для большинства сигналов,но два сигнала, SIGKILLи SIGSTOP, никогда нельзя игнорировать.
  *     2. Перехватить сигнал. Для этого мы должны сообщить ядру адрес функции, которая будет вызываться всякий раз при обнаружении сигнала.В этой функции мы можем предусмотреть действия по обработке условия,породившего сигнал.
  *     3. Применить действие по умолчанию. Каждому сигналу поставлено в соответствие некоторое действие по умолчанию

  * SIGABRT Аварийное завершение (abort)
  * SIGALRM Истекло время таймера (alarm)
  * SIGBUS Аппаратная ошибка
  * SIGCHLD Изменение состояния дочернего процесса
  * SIGCONT Возобновить работу приостановленного процесса
  * SIGEMT Аппаратная ошибка
  * SIGFPE Арифметическая ошибка
  * SIGFREEZE Закрепление контрольной точки
  * SIGHUP Обрыв связи
  * SIGILL Недопустимая инструкция
  * SIGINT С терминала введен символ прерывания
  * SIGIO Асинхронный ввод-вывод
  * SIGIOT Аппаратная ошибка
  * SIGKILL Завершение
  * SIGPIPE Запись в канал, из которого никто не читает
  * SIGPOLL Событие опроса (poll)
  * SIGPROF Истекло время профилирующего таймера (setitimer)
  * SIGQUIT С терминала введен символ завершения
  * SIGSEGV Ошибка доступа к памяти

Полный список сигнало находится в man 7 signal

## Основные фукнции

```c
#include <signal.h>
void (*signal(int signo, void (*func)(int)))(int);
```

Возвращает предыдущую позицию сигнала в случае успеха, SIG_ERR – в случае ошибки

Не рекомендуется использовать `signal` для установки обработчика сигнала, отличного от `SIG_DFL` или `SIG_IGN`. Используйте `sigaction`.

```c
#include <signal.h>
```

```c
int sigaction(int signo, const struct sigaction *act, struct sigaction *oldact);
```

В структуру `oldact` если значение параметра не равно `NULL` возвращаются старые настройки обработки сигнала.

Структуру, адрес которой передается параметром `act`, можно заполнить следующим образом:

```c
struct sigaction sa = {}; // инициализируем нулями
sa.sa_flags = SA_RESTART; // restartable system calls
sa.sa_handler = func;     // обработчик сигнала
```

```c
#include <signal.h>
int kill(pid_t pid, int signo);
int raise(int signo);
```

Обе возвращают 0 в случае успеха, –1 в случае ошибки

```c
#include <unistd.h>
unsigned int alarm(unsigned int seconds);
```

Возвращает 0 или количество секунд до истечения периода времени, установленного ранее

```c
#include <unistd.h>
int pause(void);
```

Возвращает значение –1 с кодом ошибки EINTR в переменной errno

## Ссылки

  * [Развернутый конспект](/blackav/hse-caos-2020/blob/master/18-signal/sem-signals.pdf)
  * [Лекция 27](/blackav/hse-caos-2020/blob/master/00-lectures/27-signal1/27-signal1.pdf)
  * [Лекция 28](/blackav/hse-caos-2020/blob/master/00-lectures/28-signal2/28-signal2.pdf)
  * [Примеры лекции](/blackav/hse-caos-2020/blob/master/00-lectures/28-signal2)
  * [man 7 signal](http://ru.manpages.org/signal/7)

**********

[posix](/tags/posix.md)
