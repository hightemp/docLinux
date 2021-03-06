# Создание службы Linux с помощью systemd

При написании веб-приложений мне часто приходится выгружать сложные вычислительные задачи в асинхронный рабочий сценарий, планировать задачи на потом или даже писать демон, который прослушивает сокет для прямой связи с клиентами.

В то время как иногда могут быть более эффективные инструменты для работы - всегда рассматривайте сначала использование существующего программного обеспечения, например, сервер очереди задач - написание собственной службы может дать вам уровень гибкости, который вы никогда не получите, когда связаны ограничениями стороннего программного обеспечения.

Круто то, что создать службу Linux довольно легко: используйте свой любимый язык программирования для написания долго работающей программы и превратите ее в службу с помощью systemd.

### Программа

Давайте создадим небольшой сервер с использованием PHP. Я вижу, как твои брови поднимаются, но это работает на удивление хорошо. Мы прослушаем UDP-порт 10000 и вернем любое сообщение, полученное с помощью преобразования [ROT13](https://en.wikipedia.org/wiki/ROT13):

```php
<?php

$sock = socket\_create(AF\_INET, SOCK\_DGRAM, SOL\_UDP);
socket\_bind($sock, '0.0.0.0', 10000);

for (;;) {
    socket\_recvfrom($sock, $message, 1024, 0, $ip, $port);
    $reply = str\_rot13($message);
    socket\_sendto($sock, $reply, strlen($reply), 0, $ip, $port);
}
```

Давайте начнем это:

```
$ php server.php
```

И проверить это в другом терминале:

```
$ nc -u 127.0.0.1 10000  
Hello, world!  
Uryyb, jbeyq!
```

Круто, все работает. Теперь мы хотим, чтобы этот сценарий выполнялся постоянно, перезапускался в случае сбоя (неожиданного выхода) и даже выживал после перезапуска сервера. Вот где systemd вступает в игру.

### Превращение в сервис

Давайте создадим файл с именем `/etc/systemd/system/rot13.service`:

```
[Unit]  
Description=ROT13 demo service  
After=network.target  
StartLimitIntervalSec=0

[Service]  
Type=simple  
Restart=always  
RestartSec=1  
User=centos  
ExecStart=/usr/bin/env php /path/to/server.php  
  
[Install]  
WantedBy=multi-user.target
```

Вам необходимо:

* установите действительное имя пользователя после `User=`
* установите правильный путь к вашему сценарию в `ExecStart=`

Вот и все. Теперь мы можем запустить сервис:

```
$ systemctl start rot13
```

И автоматически заставить его запускаться при загрузке:

```
$ systemctl enable rot13
```

### Идти дальше

Теперь, когда ваш сервис (надеюсь) работает, может быть важно немного углубиться в параметры конфигурации и убедиться, что он всегда будет работать так, как вы ожидаете.

#### Начиная в правильном порядке

Возможно, вы задавались вопросом, что сделала директива `After=`. Это просто означает, что ваш сервис должен быть запущен после того, как сеть готова. Если ваша программа ожидает, что сервер MySQL запущен и работает, вы должны добавить:

```
After=mysqld.service
```

#### Перезапуск при выходе

По умолчанию systemd не перезапускает ваш сервис, если программа по какой-либо причине завершает работу. Обычно это не то, что вам нужно для службы, которая должна быть всегда доступна, поэтому мы советуем ей всегда перезапускаться при выходе:

```
Restart=always
```

Вы также можете использовать `on-fault` только для перезапуска, если состояние выхода не равно` 0`.

По умолчанию systemd пытается перезапустить через 100 мс. Вы можете указать количество секунд ожидания перед попыткой перезапуска, используя:

```
RestartSec=1
```

#### Как избежать ловушки: предел начала

Я лично попадал в это не раз. По умолчанию, когда вы настраиваете `Restart=always`, как мы это делали, **systemd прекращает перезапуск службы, если она не запускается более 5 раз в течение 10 секунд **. Навсегда.

За это отвечают две `[Unit]` конфигурации [опции](https://www.freedesktop.org/software/systemd/man/systemd.unit.html#StartLimitIntervalSec=):

```
StartLimitBurst=5
StartLimitIntervalSec=10
```

Директива `RestartSec` также влияет на результат: если вы установите перезапуск через 3 секунды, то вы не сможете достичь 5 неудачных попыток в течение 10 секунд.

**Простое исправление, которое всегда работает, - установить `StartLimitIntervalSec=0`. ** Таким образом, systemd будет пытаться перезапустить ваш сервис навсегда.

Хорошей идеей будет установить `RestartSec` как минимум на 1 секунду, чтобы избежать чрезмерной нагрузки на сервер, когда что-то пойдет не так.

В качестве альтернативы вы можете оставить настройки по умолчанию и попросить systemd перезапустить ваш сервер, если достигнут предел запуска, используя `StartLimitAction=reboot`.

### Это действительно так?

Вот и все, что нужно для создания службы Linux с помощью systemd: написание небольшого файла конфигурации, который ссылается на вашу давно работающую программу.

В течение нескольких лет Systemd была стандартной системой инициализации в RHEL / CentOS, Fedora, Ubuntu, Debian и других, поэтому есть вероятность, что ваш сервер готов к размещению ваших доморощенных сервисов!

**********
[systemd](/tags/systemd.md)
