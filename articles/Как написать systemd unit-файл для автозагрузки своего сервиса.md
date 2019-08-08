# Как написать systemd unit-файл для автозагрузки своего сервиса

Здесь покажу как писать инитники для автозапуска какого-либо демона в системе с systemd.

Systemd оперирует unit-файлами в качестве конфигурационных файлов. Это как .conf-файл для upstart или init-скрипты для initd. Unit-файлы также могут описывать и другие системные сущности, но в данном случае они нас интересуют как конфиг для автостарта сервиса. В Ubuntu 16.04 они лежат в `/etc/systemd/` . Напишем свой unit-файл.

Допустим у нас есть программа, которую мы хотим запускать как демон. Вот [здесь](https://4te.me/post/telegram-bot-golang/) я писал как создать telegram-бота. У меня получился исполняемый файл, который запускается и висит ждет сообщений. Теперь хочу чтобы он как демон стартовал при загрузке системы.

Создаем такой файл:

```INI
[Unit]
Description=TelegramBotMonitoring
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/telegram-site-monitoring -telegrambottoken 397______:___________WRDsIU -chatid -14____640
Restart=always

[Install]
WantedBy=multi-user.target

```

и кладем его в `/etc/systemd/system/telegram-bot.service` 

Конфиг похож на обычный ini-файл:

*    `After` \- запускать этот юнит после определенных демонов или целей (цель - это набор юнитов). Здесь указан `network.target` , это значит, что демон запустится после того как поднимутся сетевые интерфейсы.
    
*    `Type` \- тип того, как запускается демон. Чаще всего используется `simple` , `forking` или `one-shot` . `simple` \- демон запускается и начинает ожидать на консоле и не отфоркивается. `forking` \- демон запускается, потом форкается и завершает родительский процесс. Многие программы именно так и запускаются, чтобы перейти в background режим. Например, nginx запускается по такой схеме. `one-shot` \- используется для запуска скриптов которые запускаются, отрабатывают и завершаются. В моем случае это не скрипт и программа не форкается , поэтому тип - `simple` 
    
*    `ExecStart` \- команда для запуска демона.
    
*    `Restart` \- рестартовать демон, если он завершится/упадет. При `always` systemd будет перезапускать демон независимо от того почему он завершился. Можно указать `on-failure` , тогда будет перезапускаться если демон вышел с ненулевым кодом возврата или был завершен по сигналу (kill DAEMONPID)
    
*    `WantedBy` \- говорим, что запускать этот демон когда система грузится в multi-user режиме
    

Далее делаем релоад systemd:

```console
# systemctl daemon-reload

```

И добавляем созданный юнит в автозагрузку:

```console
# systemctl enable telegram-bot.service
Created symlink from /etc/systemd/system/multi-user.target.wants/telegram-bot.service to /etc/systemd/system/telegram-bot.service.```

```

Все. Сервис добавлен в автозагрузку, но еще не запущен. Запустим:

```console
# systemctl start telegram-bot

```

Запустился:

```console
# systemctl status telegram-bot
● telegram.service - TelegramBotMonitoring
   Loaded: loaded (/etc/systemd/system/telegram-bot.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2017-07-13 17:10:19 MSK; 5s ago
 Main PID: 1825 (telegram-site-m)
    Tasks: 4
   Memory: 4.4M
      CPU: 39ms
   CGroup: /system.slice/telegram-bot.service
           └─1825 /usr/local/bin/telegram-site-monitoring -telegrambottoken 3972____:__________Gi03WRDsIU -chatid -14____40

Jul 13 17:10:19 ubuntu systemd[1]: Started TelegramBotMonitoring.
Jul 13 17:10:19 ubuntu telegram-site-monitoring[1825]: 2017/07/13 17:10:19 {}
Jul 13 17:10:19 ubuntu telegram-site-monitoring[1825]: 2017/07/13 17:10:19 Authorized on account
Jul 13 17:10:19 ubuntu telegram-site-monitoring[1825]: 2017/07/13 17:10:19 Config file: config.json
Jul 13 17:10:19 ubuntu telegram-site-monitoring[1825]: 2017/07/13 17:10:19 ChatID: 
Jul 13 17:10:19 ubuntu telegram-site-monitoring[1825]: 2017/07/13 17:10:19 Starting monitoring thread

```

Шпаргалка с коммандами для управления демонами systemd - [https://4te.me/post/shpargalka-systemd/](https://4te.me/post/shpargalka-systemd/)

**********
[service](/tags/service.md)
[unit](/tags/unit.md)
[systemd](/tags/systemd.md)
