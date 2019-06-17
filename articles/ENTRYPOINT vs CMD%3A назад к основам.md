# ENTRYPOINT vs CMD: назад к основам

Название `ENTRYPOINT` всегда меня смущало. Это название подразумевает, что каждый контейнер должен иметь определенную инструкцию `ENTRYPOINT`. Но после прочтения [официальной документации](https://docs.docker.com/engine/reference/builder/#entrypoint) я понял, что это не соответствует действительности.

  

## Факт 1: Требуется определить хотя бы одну инструкцию (`ENTRYPOINT`или`CMD`) (для запуска).

  

Если вы не определите ни одной из них, то получите сообщение об ошибке. Давайте попробуем запустить образ Alpine Linux, для которого не определены ни `ENTRYPOINT`, ни `CMD`.

  

```
$ docker run alpine
docker: Error response from daemon: No command specified.  
See 'docker run --help'.
```

  

## Факт 2: Если во время выполнения определена только одна из инструкций, то и `CMD` и `ENTRYPOINT` будут иметь одинаковый эффект.

  

```
$ cat Dockerfile 
FROM alpine  
ENTRYPOINT ls /usr  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
bin  
lib  
local  
sbin  
share  
```

  

Мы получим те же результаты, если будем использовать `CMD` вместо `ENTRYPOINT`.

  

```
$ cat Dockerfile 
FROM alpine  
CMD ls /usr  # Using CMD instead  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
bin  
lib  
local  
sbin  
share  
```

  

Хотя этот пример и показывает, что между `ENTRYPOINT` и `CMD` нет никакой разницы, её можно увидеть, сравнив метаданные контейнеров.

  

Например, первый файл **Dockerfile** (с определенной `ENTRYPOINT`):

  

```
$ docker inspect b52 | jq .[0].Config
{
  ...
  "Cmd": null,
  ...
  "Entrypoint": [
    "/bin/sh",
    "-c",
    "ls /"
  ],
  ...
}
```

  

## Факт 3: И для `CMD`, и для `ENTRYPOINT`существуют режимы _shell_ и _exec_.

  

Из[руководства](https://docs.docker.com/engine/reference/builder/#entrypoint):

  

> `ENTRYPOINT`имеет два режима выполнения:  
> 
> *   `ENTRYPOINT ["executable", "param1", "param2"]`(исполняемая форма, предпочтительно)
> *   `ENTRYPOINT command param1 param2`(форма оболочки)
> 
>   

До сих пор мы использовали режим _shell_, или оболочки. Это означает, что наша команда `ls -l` запускается внутри `/bin/sh -c`. Давайте попробуем оба режима и изучим запущенные процессы.

  

Режим _"shell"_:

  

```
$ cat Dockerfile
FROM alpine  
ENTRYPOINT ping www.google.com  # "shell" format  
```

  

```
$ docker build -t test .
```

  

```
$ docker run -d test
11718250a9a24331fda9a782788ba315322fa879db311e7f8fbbd9905068f701  
```

  

Затем изучим процессы:

  

```
$ docker exec 117 ps
PID   USER     TIME   COMMAND  
    1 root       0:00 /bin/sh -c ping www.google.com
    7 root       0:00 ping www.google.com
    8 root       0:00 ps
```

  

Обратите внимание, что процесс `sh -c` имеет PID, равный 1. Теперь то же самое, используя режим _"exec"_:

  

```
$ cat Dockerfile
FROM alpine  
ENTRYPOINT ["ping", "www.google.com"]  # "exec" format  
```

  

```
$ docker build -t test .
```

  

```
$ docker run -d test
1398bb37bb533f690402e47f84e43938897cbc69253ed86f0eadb6aee76db20d  
```

  

```
$ docker exec 139 ps
PID   USER     TIME   COMMAND  
    1 root       0:00 ping www.google.com
    7 root       0:00 ps
```

  

Мы видим, что при использовании режима _exec_ команда `ping www.google.com` работает с идентификатором процесса PID, равным 1, а процесс `sh -c` отсутствует. Имейте в виду, что приведенный выше пример работает точно так же, если использовать `CMD` вместо `ENTRYPOINT`.

  

## Факт 4: Режим_exec_является рекомендуемым.

  

Это связано с тем, что контейнеры задуманы так, чтобы содержать один процесс. Например, отправленные в контейнер сигналы перенаправляются процессу, запущенному внутри контейнера с идентификатором PID, равным 1. Очень познавательный опыт: чтобы проверить факт перенаправления, полезно запустить контейнер _ping_ и попытаться нажать _ctrl + c_ для остановки контейнера.

  

Контейнер, определенный с помощью режима _exec_, успешно завершает работу:

  

```
$ cat Dockerfile 
FROM alpine  
ENTRYPOINT ["ping", "www.google.com"]  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
PING www.google.com (172.217.7.164): 56 data bytes  
64 bytes from 172.217.7.164: seq=0 ttl=37 time=0.246 ms  
64 bytes from 172.217.7.164: seq=1 ttl=37 time=0.467 ms  
^C
--- www.google.com ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss  
round-trip min/avg/max = 0.246/0.344/0.467 ms  
$
```

  

При использовании режима _"shell"_ контейнер работает не так, как ожидалось.

  

```
$ cat Dockerfile 
FROM alpine  
ENTRYPOINT ping www.google.com  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
PING www.google.com (172.217.7.164): 56 data bytes  
64 bytes from 172.217.7.164: seq=0 ttl=37 time=0.124 ms  
^C^C^C^C64 bytes from 172.217.7.164: seq=4 ttl=37 time=0.334 ms
64 bytes from 172.217.7.164: seq=5 ttl=37 time=0.400 ms  
```

  

Помогите, я не могу выйти! Сигнал `SIGINT`, который был направлен процессу `sh`, не будет перенаправлен в подпроцесс `ping`, и оболочка не завершит работу. Если по какой-то причине вы действительно хотите использовать режим _shell_, выходом из ситуации будет использовать `exec` для замены процесса оболочки процессом `ping`.

  

```
$ cat Dockerfile
FROM alpine  
ENTRYPOINT exec ping www.google.com  
```

  

## Факт 5: Нет оболочки? Нет переменных окружения.

  

Проблема запуска НЕ в режиме оболочки заключается в том, что вы не можете воспользоваться преимуществами переменных среды (таких как `$PATH`) и прочими возможностями, которые предоставляет использование оболочки. В приведенном ниже файле **Dockerfile** присутствуют две проблемы:

  

```
$ cat Dockerfile 
FROM openjdk:8-jdk-alpine  
WORKDIR /data  
COPY *.jar /data  
CMD ["java", "-jar", "*.jar"]  # "exec" format  
```

  

Первая проблема: поскольку вы не можете воспользоваться переменной среды `$PATH`, нужно указать точное расположение исполняемого java-файла. Вторая проблема: символы подстановки интерпретируются самой оболочкой, поэтому строка `*.jar` не будет корректно обработана. После исправления этих проблем итоговый файл **Dockerfile** выглядит следующим образом:

  

```
FROM openjdk:8-jdk-alpine  
WORKDIR /data  
COPY *.jar /data  
CMD ["/usr/bin/java", "-jar", "spring.jar"]  
```

  

## Факт 6: Аргументы CMD присоединяются к концу инструкции `ENTRYPOINT`… иногда.

  

Вот тут-то и начинается путаница. В [руководстве](https://docs.docker.com/engine/reference/builder/#understand-how-cmd-and-entrypoint-interact "руководстве") есть таблица, цель которой – внести ясность в этот вопрос.

  

![Entrypointscreen](/images/68ac7b27a4ddf500276c5c1b04a47120.png)

  

Попытаюсь объяснить **на пальцах**.

  

### Факт 6a: Если вы используете режим _shell_ для `ENTRYPOINT`, `CMD` игнорируется.

  

```
$ cat Dockerfile 
FROM alpine  
ENTRYPOINT ls /usr  
CMD blah blah blah blah  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
bin  
lib  
local  
sbin  
share  
```

  

Строка `blah blah blah blah` была проигнорирована.

  

### FACT 6b: При использовании режима_exec_для `ENTRYPOINT` аргументы `CMD` добавляются в конце.

  

```
$ cat Dockerfile
FROM alpine  
ENTRYPOINT ["ls", "/usr"]  
CMD ["/var"]  
```

  

```
$ docker build -t test .
```

  

```
$ docker run test
/usr:
bin  
lib  
local  
sbin  
share

/var:
cache  
empty  
lib  
local  
lock  
log  
opt  
run  
spool  
tmp  
```

  

Аргумент `/var` был добавлен к нашей инструкции `ENTRYPOINT`, что позволило эффективно запустить команду `ls/usr/var`.

  

### Факт 6c: При использовании режима _exec_ для инструкции `ENTRYPOINT` необходимо использовать режим _exec_ и для инструкции `CMD`. Если этого не сделать, Docker попытается добавить `sh -c` в уже добавленные аргументы, что может привести к некоторым непредсказуемым результатам.

  

## Факт 7: Инструкции `ENTRYPOINT` и `CMD` могут быть переопределены с помощью флагов командной строки.

  

Флаг `--entrypoint` может быть использован, чтобы переопределить инструкцию`ENTRYPOINT`:

  

```
docker run --entrypoint [my_entrypoint] test  
```

  

Все, что следует после названия образа в команде `docker run`, переопределяет инструкцию `CMD`:

  

```
docker run test [command 1] [arg1] [arg2]  
```

  

Все вышеперечисленные факты справедливы, но имейте в виду, что разработчики имеют возможность переопределять флаги в команде `docker run`. Из этого следует, что ...

  

## Достаточно фактов… Что же делать мне?

  

Ok, если вы дочитали статью до этого места, то вот информация, в каких случаях использовать `ENTRYPOINT`, а в каких `CMD`.

  

Это решение я собираюсь оставить на усмотрение человека, создающего **Dockerfile**, который может быть использован другими разработчиками.

  

Используйте `ENTRYPOINT`, если вы не хотите, чтобы разработчики изменяли исполняемый файл, который запускается при запуске контейнера. Вы можете представлять, что ваш контейнер – _исполняемая оболочка_. Хорошей стратегией будет определить _стабильную_ комбинацию параметров и исполняемого файла как `ENTRYPOINT`. Для нее вы можете (не обязательно) указать аргументы`CMD`по умолчанию, доступные другим разработчикам для переопределения.

  

```
$ cat Dockerfile
FROM alpine  
ENTRYPOINT ["ping"]  
CMD ["www.google.com"]  
```

  

```
$ docker build -t test .
```

  

Запуск с параметрами _по умолчанию_:

  

```
$ docker run test
PING www.google.com (172.217.7.164): 56 data bytes  
64 bytes from 172.217.7.164: seq=0 ttl=37 time=0.306 ms
```

  

Переопределение CMD собственными параметрами:

  

```
$ docker run test www.yahoo.com
PING www.yahoo.com (98.139.183.24): 56 data bytes  
64 bytes from 98.139.183.24: seq=0 ttl=37 time=0.590 ms  
```

  

Используйте только `CMD`(без определения `ENTRYPOINT`), если требуется, чтобы разработчики могли легко переопределять исполняемый файл. Если точка входа определена, исполняемый файл все равно можно переопределить, используя флаг `--entrypoint`. Но для разработчиков будет гораздо удобнее добавлять желаемую команду в конце строки `docker run`.

  

```
$ cat Dockerfile
FROM alpine  
CMD ["ping", "www.google.com"]  
```

  

```
$ docker build -t test .
```

  

_Ping_– это хорошо, но давайте попробуем запустить контейнер с оболочкой вместо команды `ping`.

  

```
$ docker run -it test sh
/ # ps
PID   USER     TIME   COMMAND  
    1 root       0:00 sh
    7 root       0:00 ps
/ # 
```

  

Я предпочитаю по большей части этот метод, потому что он дает разработчикам свободу легко переопределять исполняемый файл оболочкой или другим исполняемым файлом.

  

## Очистка

  

После запуска команд на хосте осталась куча остановленных контейнеров. Очистите их следующей командой:

  

```
$ docker system prune
```

  

## Обратная связь

  

Буду рад услышать ваши мысли об этой статье ниже в комментариях. Кроме того, если вам известен более простой способ поиска в выдаче докера с помощью _jq_, чтобы можно было сделать что-то вроде `docker inspect [id] | jq * .config`, тоже напишите в комментариях.

  

### Джон Закконе

  

Капитан Докера и инженер по облачным технологиям в IBM. Специализируется на Agile, микросервисах, контейнерах, автоматизации, REST, DevOps.

  

### Ссылки:

  

1.  [ENTRYPOINT vs CMD: Back to Basics](http://www.johnzaccone.io/entrypoint-vs-cmd-back-to-basics/)

**********
[docker](/tags/docker.md)
