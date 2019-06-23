#  Systemd за пять минут

 Давайте выжмем из документации минимально необходимый набор информации для создания простых старт-стоп скриптов.   
  
 Systemd запускает сервисы описанные в его конфигурации.   
 Конфигурация состоит из множества файлов, которые по-модному называют юнитами.   
  
 Все эти юниты разложены в трех каталогах:   
  
 **/usr/lib/systemd/system/**   – юниты из установленных пакетов RPM — всякие nginx, apache, mysql и прочее   
 **/run/systemd/system/**   — юниты, созданные в рантайме — тоже, наверное, нужная штука   
 **/etc/systemd/system/**   — юниты, созданные системным администратором — а вот сюда мы и положим свой юнит.   
  
 Юнит представляет из себя текстовый файл с форматом, похожим на файлы .ini Microsoft Windows.   
  

> \[Название секции в квадратных скобках\]  
> имя\_переменной = значение

  
  
 Для создания простейшего юнита надо описать три секции: [Unit], [Service], [Install]   
  
 В секции Unit описываем, что это за юнит:   
 Названия переменных достаточно говорящие:   
  
 Описание юнита:   

> Description=MyUnit  

  
 Далее следует блок переменных, которые влияют на порядок загрузки сервисов:   
  
 Запускать юнит после какого-либо сервиса или группы сервисов (например network.target):   

> After=syslog.target  
> After=network.target  
> After=nginx.service  
> After=mysql.service

  
 Для запуска сервиса необходим запущенный сервис mysql:   

> Requires=mysql.service  

  
 Для запуска сервиса желателен запущенный сервис redis:   

> Wants=redis.service  

  
 В итоге переменная Wants получается чисто описательной.   
 Если сервис есть в Requires, но нет в After, то наш сервис будет запущен параллельно с требуемым сервисом, а не после успешной загрузки требуемого сервиса   
  
 В секции Service указываем какими командами и под каким пользователем надо запускать сервис:   
  
 Тип сервиса:   

> Type=simple  

 (по умолчанию): systemd предполагает, что служба будет запущена незамедлительно. Процесс при этом не должен разветвляться. Не используйте этот тип, если другие службы зависят от очередности при запуске данной службы.   
  

> Type=forking  

 systemd предполагает, что служба запускается однократно и процесс разветвляется с завершением родительского процесса. Данный тип используется для запуска классических демонов.   
  
 Также следует определить PIDFile=, чтобы systemd могла отслеживать основной процесс:   

> PIDFile=/work/www/myunit/shared/tmp/pids/service.pid  

  
 Рабочий каталог, он делается текущим перед запуском стартап команд:   

> WorkingDirectory=/work/www/myunit/current  

  
 Пользователь и группа, под которым надо стартовать сервис:   

> User=myunit  
> Group=myunit

  
  
 Переменные окружения:   

> Environment=RACK\_ENV=production  

  
 Запрет на убийство сервиса вследствие нехватки памяти и срабатывания механизма OOM:   
 -1000 полный запрет (такой у sshd стоит), -100 понизим вероятность.   

> OOMScoreAdjust=-100  

  
 Команды на старт/стоп и релоад сервиса   
  

> ExecStart=/usr/local/bin/bundle exec service -C /work/www/myunit/shared/config/service.rb --daemon  
> ExecStop=/usr/local/bin/bundle exec service -S /work/www/myunit/shared/tmp/pids/service.state stop  
> ExecReload=/usr/local/bin/bundle exec service -S /work/www/myunit/shared/tmp/pids/service.state restart  

  
 Тут есть тонкость — systemd настаивает, чтобы команда указывала на конкретный исполняемый файл. Надо указывать полный путь.   
  
 Таймаут в секундах, сколько ждать system отработки старт/стоп команд.   

> TimeoutSec=300  

  
  
 Попросим systemd автоматически рестартовать наш сервис, если он вдруг перестанет работать.   
 Контроль ведется по наличию процесса из PID файла   

> Restart=always  

  
  
 В секции [Install] опишем, в каком уровне запуска должен стартовать сервис   
  
 Уровень запуска:   

> WantedBy=multi-user.target  

  
 multi-user.target или runlevel3.target соответствует нашему привычному runlevel=3 «Многопользовательский режим без графики. Пользователи, как правило, входят в систему при помощи множества консолей или через сеть»   
  
 Вот и готов простейший стартап скрипт, он же unit для systemd:   
 myunit.service   
  

```
[Unit]
Description=MyUnit
After=syslog.target
After=network.target
After=nginx.service
After=mysql.service
Requires=mysql.service
Wants=redis.service

[Service]
Type=forking
PIDFile=/work/www/myunit/shared/tmp/pids/service.pid
WorkingDirectory=/work/www/myunit/current

User=myunit
Group=myunit

Environment=RACK_ENV=production

OOMScoreAdjust=-1000

ExecStart=/usr/local/bin/bundle exec service -C /work/www/myunit/shared/config/service.rb --daemon
ExecStop=/usr/local/bin/bundle exec service -S /work/www/myunit/shared/tmp/pids/service.state stop
ExecReload=/usr/local/bin/bundle exec service -S /work/www/myunit/shared/tmp/pids/service.state restart
TimeoutSec=300

[Install]
WantedBy=multi-user.target 

```

  
 Кладем этот файл в каталог /etc/systemd/system/   
  
 Смотрим его статус systemctl status myunit   
  

```
myunit.service - MyUnit
   Loaded: loaded (/etc/systemd/system/myunit.service; disabled)
   Active: inactive (dead)

```

  
 Видим, что он disabled — разрешаем его   
 **systemctl enable myunit  
systemctl -l status myunit**   
  
 Если нет никаких ошибок в юните — то вывод будет вот такой:   
  

```
myunit.service - MyUnit
   Loaded: loaded (/etc/systemd/system/myunit.service; enabled)
   Active: inactive (dead)

```

  
  
 Запускаем сервис    
 **systemctl start myunit**   
 Смотрим красивый статус:   
 **systemctl -l status myunit**   
 Если есть ошибки — читаем вывод в статусе, исправляем, не забываем после исправлений в юните перегружать демон systemd   
  
 **systemctl daemon-reload**   
 Теперь, после ознакомительного окунания в systemd можно, начинать самостоятельные заплывы.   
 Если вдруг появятся вопросы, рады будем ответить на ваши письма по адресу ask@centos-admin.ru

**********
[service](/tags/service.md)
