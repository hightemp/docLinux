# Куда делись файловые дескрипторы?

Источник: [Куда делись файловые дескрипторы?](https://firstvds.ru/blog/kuda_delis_faylovye_deskriptory)

В работе сервера можно отследить, какие выполняются процессы и количество используемых файловых дескрипторов. В основном процессы открывают файлы типа:

  * Используемые лог-файлы
  * Файлы устройств из /dev
  * UNIX-сокеты
  * Сетевые сокеты
  * Файлы библиотек /lib /lib64
  * Выполняющиеся процессы и другие программы

В этой заметке мы разберем, как подсчитать количество используемых в данный момент файловых дескрипторов на сервере с Linux.

## Как найти PID

PID - это идентификатор процесса (Process Identificator), который является уникальным в работающей системе. Для того, чтобы узнать какой идентификатор принадлежит работающему процессу, следует выполнить команду:

```text
[root@one ~]# ps -ax|grep proftpd
Warning: bad syntax, perhaps a bogus '-'? See /usr/share/doc/procps-3.2.8/FAQ
28017 ?        Ss     0:09 proftpd: (accepting connections)
```

Или такую команду:

```text
[root@one ~]# pidof proftpd
28017
```

## Получить список открытых файлов по PID

Используя команду lsof можно увидеть все открытые этим процессом файловые дескрипторы

```text
[root@one ~]# lsof -p 28017
COMMAND   PID   USER   FD   TYPE             DEVICE SIZE/OFF   NODE NAME
proftpd 28017 nobody  cwd    DIR              252,3     4096      2 /
proftpd 28017 nobody  rtd    DIR              252,3     4096      2 /
proftpd 28017 nobody  txt    REG              252,3   777368  20781 /usr/sbin/proftpd (deleted)
proftpd 28017 nobody  mem    REG              252,3   156936   3472 /lib64/ld-2.12.so
proftpd 28017 nobody  mem    REG              252,3    22536   6483 /lib64/libdl-2.12.so
proftpd 28017 nobody  mem    REG              252,3  1926760   6409 /lib64/libc-2.12.so
proftpd 28017 nobody  mem    REG              252,3   145896   3408 /lib64/libpthread-2.12.so
<...список сокращен...>
proftpd 28017 nobody    0u  IPv6             111496      0t0    TCP *:ftp (LISTEN)
proftpd 28017 nobody    1u  unix 0xffff880059934400      0t0 111497 socket
proftpd 28017 nobody    3u  unix 0xffff88005a19a700      0t0 111481 /var/run/proftpd/proftpd.sock
proftpd 28017 nobody    4u  unix 0xffff88005a23f800      0t0 111489 /var/run/proftpd/proftpd.sock
proftpd 28017 nobody    5r   REG              252,3     1464 139883 /etc/passwd
proftpd 28017 nobody    6r   REG              252,3      692 139881 /etc/group
```

Обратите внимание, что как и говорилось в первом абзаце, здесь есть как исполняемые файлы, так и сокет-файлы, а так же библиотеки и сетевые сокеты.

## Посчитать открытые файлы

Для того, чтобы посчитать все открытые файловые дескрипторы, выполните команду:

```text
[root@one fd]# lsof |wc -l
3070
```

если требуется посчитать для конкретного процесса, это делается так:

```text
[root@one fd]# lsof -p 28017 |wc -l
35
```

### Список файловых дескрипторов в памяти ядра

Выполнив команду, можно получить следующий вывод информации:

```text
[root@one fd]# sysctl fs.file-nr
fs.file-nr = 1056    0    147398
```

Где:

  1. 1056 - число выделенных дескрипторов
  2. 0 - число неиспользуемых выделенных дескрипторов
  3. 147398 - максимальное общесистемное количество дескрипторов. Оно зависит от размера дискового пространства сервера.

Держите свои серверы в порядке и не теряйте открытые файловые дескрипторы ;-)

#### Возможно, вам будет интересно

![](/images/c1fd9285cf49f06b73851fceb814fe60.png)

Изменение пароля root

[Читать](https://firstvds.ru/technology/izmenenie-parolya-root)

#### Было интересно?

__ Да __ Нет Неактуально Недостоверно Непонятно

#### Теги

  * [ Терминал ](/search?search_api_views_fulltext=Терминал&hashtags=Терминал)

[ __Назад к списку](/blog?tab=articles)

#### Другие статьи

  * Статья 31 августа 2026

[Лучшие нейросети для генерации кода и программирования](/blog/luchshie-neyroseti-dlya-koda-i-programmirovaniya)

  * Статья 6 августа 2026

[Анатомия дата-центра: как устроены ЦОДы изнутри](/blog/anatomiya-data-centra-kak-ustroeny-cody-iznutri)

  * Статья 4 августа 2026

[DDoS-атаки 2026: эволюция угрозы. Кто находится в зоне риска?](/blog/ddos-ataki-2026-evolyuciya-ugrozy-kto-nakhoditsya-v-zone-riska)

  * Статья 30 июля 2026

[Первый закон об ИИ в России: что изменится для разработчиков и пользователей](/blog/pervyy-zakon-ob-ii-v-rossii-chto-izmenitsya-dlya-razrabotchikov-i-polzovateley)

  * Статья 24 июля 2026

[10 ИИ-приложений и сервисов, чтобы залипнуть в свободное время ](/blog/10-ii-prilozheniy-i-servisov-chtoby-zalipnut-v-svobodnoe-vremya)

#### Сообщить об ошибке

##### Опишите проблему

если хотите, чтобы вам ответили

Отправить

__ ![](/images/79612b8929e0ddd94eb9cf872fd8f44f.png)

Скидка новым клиентам

Закажите сервер сегодня и получите скидку на первый месяц аренды!

**********

[файловые дескрипторы](/tags/failovye_deskriptory.md)
