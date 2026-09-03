# Развертывание Zabbix 4.4 с nginx, php-fpm и MySQL Percona в Docker

Источник: [Развертывание Zabbix 4.4 с nginx, php-fpm и MySQL Percona в Docker](https://it-lux.ru/развертывание-zabbix-4-с-nginx-php-fpm-и-mysql-в-docker/)

Вышла новая версия Zabbix 5.0, рекомендуется производить установку Zabbix по данной [статье](https://it-lux.ru/zabbix-5-0-%d1%83%d1%81%d1%82%d0%b0%d0%bd%d0%be%d0%b2%d0%ba%d0%b0-%d0%b2-docker-%d1%81-postgresql-%d0%b8-timescaledb/)

В данной заметке будет рассмотрена быстрая установка Zabbix 4.4.8 в контейнере и его последующая небольшая настройка.

Вообще, есть готовые образы 3 в 1: сам Zabbix, веб-сервер и БД. Но я решил использовать всё по отдельности для более гибкого управления в будущем.

Итого понадобится 3 контейнера:

  * Сервер: Zabbix server
  * Фронт: nginx + php-fpm
  * БД: MySQL Percona

Nginx выбран как популярный и современный веб-сервер на замену apache, а php-fpm -- как быстрый и легковесный обработчик php.

Установка простая для тех, кто знаком со всеми технологиями. Тем не менее, буду расписывать пошагово.

Предположим, что Docker уже установлен на сервере. Для удобства и разграничения, я создал отдельную сеть для использования её в будущих контейнерах:

```text
docker network create --subnet=10.6.0.0/24 --driver=bridge zabbix-net
```

После создания сеть должна появиться в списке:

```text
[root@dc ~]# docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
6099e52a26b2        bridge              bridge              local
a6b8eae2ae56        host                host                local
92b885e99d1f        none                null                local
e6da2c1df745        zabbix-net          bridge              local
```

Контейнеры, созданные в рамках данной сети, смогу видеть друг друга, **в том числе по имени, которое передаётся через ключ --name**. Проверить это можно позднее, создав контейнеры и проверить пинг из одного контейнера в другой по имени.

Далее с Dockerhub стягиваются образы с явным указанием версий:

```text
docker pull zabbix/zabbix-server-mysql:centos-4.4.8
docker pull zabbix/zabbix-web-nginx-mysql:centos-4.4.8
docker pull percona:5.7.29-centos
```

Содержание

  1. MySQL
  2. Zabbix-server
  3. Front (nginx & php-fpm)
  4. Примечания

#### MySQL

Начнём с настройки и запуска контейнера с MySQL. Предварительно опять же для удобства будут созданы директории для хранения конфигов и данных БД:

```text
container_name=zab-mysql

mkdir -p /storage/${container_name}/data && mkdir /storage/${container_name}/config
```

В директорию /storage/${container_name}/config необходимо положить файл с конфигом для будущей БД.

Обращаю внимание, что файл должен быть с именем **my.cnf** , MySQL по-умолчанию ищет конфиг по путям /etc/my.cnf /etc/mysql/my.cnf ~/.my.cnf, проверить можно командой

```text
/usr/sbin/mysqld --verbose --help | grep -A 1 "Default options"
```

Так вот, определившись с именем, рисуем минимально рабочий конфиг:

```text
cat > /storage/zab-mysql/config/my.cnf << EOF
[client]
port            = 3306
socket          = /var/lib/mysql/mysql.sock
default-character-set=utf8

[mysqld]
user            = mysql
port            = 3306
socket          = /var/lib/mysql/mysql.sock

skip-external-locking

max_allowed_packet          = 16M
key_buffer_size             = 16M
innodb_buffer_pool_size     = 512M
innodb_file_per_table       = 1
innodb_flush_method         = O_DIRECT
innodb_flush_log_at_trx_commit  = 0

max_connections             = 132
event_scheduler             = 1

# Character

character-set-server = utf8
collation-server = utf8_general_ci
init_connect="SET collation_connection = utf8_general_ci"

log_error=/var/log/mysql/mysql_error.log
EOF
```

В конфиге необходимо **указать пользователя mysql** , кодировку и представления utf8 и utf8_general_ci соответственно, чтобы в дальнейшем не возникало проблем (в том числе при секционировании таблиц). Также сразу на перспективу указывается event_scheduler = 1 для запуска планировщика процедур.

Для оптимальной производительности конфиг надо править уже под конкретную нагрузку.

И непосредственно сам запуск контейнера с указанием всех логинов и паролей к базе Zabbix:

```text
container_name=zab-mysql
docker run --user root --name ${container_name} -h ${container_name} -t --network=zabbix-net -e TZ='Europe/Moscow' -e MYSQL_DATABASE="zabbix" -e MYSQL_USER="zabbix" -e MYSQL_PASSWORD="zabbix" -e MYSQL_ROOT_PASSWORD="root" -v /storage/${container_name}/data:/var/lib/mysql -v /storage/${container_name}/config:/etc/mysql -d percona:5.7.29-centos --character-set-server=utf8 --collation-server=utf8_general_ci
```

Первоначально стоит обратить на параметр **-- user** **mysql**(он также прописан в конфиге my.cnf). Если не выставить корректные права на директорию /storage/${container_name}/data для пользователя внутри контейнера с MySQL Percona, то он не запустится, выдав в логе ошибку **mysqld: Can 't create/write to file '/var/lib/mysql/is_writable' (Errcode: 13 -- Permission denied)**. Связано это с особенностями Dockerfile, на основе которого собирается образ Percona: подразумевается, что внутри контейнера процесс будет запущен от имени пользователя mysql, а потому директория /storage/zab-mysql/data должна иметь владельца с тем же UID, что и пользователь mysql **в контейнере** -- по умолчанию это 1001:10001, но лучше уточнить, посмотрев исходники Dockerfile. Можно создать отдельного пользователя mysql в системе, назначить его владельцем монтируемой директории и запустить контейнер -- так правильнее всего. Главное, не запускать контейнер от имени суперпользователя, т.е. root.

Также обращаю внимание на параметр TZ, который задает корректную временную зону, чтобы время в контейнере и БД не отличалось от системного.

Пароль берётся из переменной при запуске контейнера, т.е. **root**. В продакшн, конечно же, лучше установить что-то посерьезней.

#### Zabbix-server

Для данного контейнера директории под хранение конфига не нужны: при старте контейнера нужно указать разрешённые переменные, т.к. в образе «зашиты» исходные параметры и переопределить их можно через список переменных (подробнее смотреть на Docker Hub).

Далее запускается контейнер с zabbix server: переменной присваивается новое значение и происходит запуск с указанием данным уже запущенного контейнера с MySQL:

```text
container_name=zab-server
docker run --name ${container_name} -h ${container_name} --network=zabbix-net -e ZBX_TIMEOUT=10 -e TZ="Europe/Moscow" -e DB_SERVER_HOST="zab-mysql" -e MYSQL_USER="zabbix" -e MYSQL_PASSWORD="zabbix" -d zabbix/zabbix-server-mysql:centos-4.4.8
```

После запуска можно проверить, что всё успешно завелось, для этого надо открыть логи и наблюдать, как создается база zabbix, нужно будет немного подождать:

```text
docker logs zab-server
```

Хочу обратить внимание, что вручную **не нужно** производить наполнение базы из файла /usr/share/doc/zabbix-server-mysql/create.sql.gz, как обычно это делается при классической установке.

#### Front (nginx & php-fpm)

И осталось запустить фронт с nginx и php-fpm:

```text
container_name=zab-front
```

Отличительной особенностью тут является то, что **Nginx внутри контейнера слушает порты 8080 и 8443** , а не классические 80 и 443, что по началу может вызвать недоумение, почему веб-интерфейс не открывается.

```text
docker run --name ${container_name} -h ${container_name} --network=zabbix-net -e DB_SERVER_HOST="zab-mysql" -e MYSQL_USER="zabbix" -e MYSQL_PASSWORD="zabbix" -e ZBX_SERVER_HOST="zab-server" -e PHP_TZ="Europe/Moscow" -p 80:8080 -p 443:8443 -d zabbix/zabbix-web-nginx-mysql:centos-4.4.8
```

Из команды выше можно заметить, что здесь пробрасываются порты на докер-хост -- 80 и 443, непосредственно уже для доступа из браузера.

На этом всё, можно проверять доступ с логином и паролем по дефолту -- Admin/zabbix

#### Примечания

  * После развёртывания, стоит сразу озаботиться вопросом [партиционирования ](http://it-lux.ru/mysql-%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D1%86%D0%B8%D0%BE%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86-zabbix/)БД, т.к. с объемом исторических данных база сильно разрастётся и нужно будет с этим что-то делать.

  * Для того, чтобы в дальнейшем не было проблем с кодировками и представлениями, лучше привести сразу всё к одному виду. По идее, в конфиге итак уже всё прописано, но на всякий случай лучше проверить:

```bash
mysql> SHOW VARIABLES LIKE '%collation%';
+----------------------+-----------------+
| Variable_name        | Value           |
+----------------------+-----------------+
| collation_connection | utf8_general_ci |
| collation_database   | utf8_general_ci |
| collation_server     | utf8_general_ci |
+----------------------+-----------------+
3 rows in set (0.08 sec)

mysql> SHOW VARIABLES LIKE '%character%';
+--------------------------+-------------------------------------+
| Variable_name            | Value                               |
+--------------------------+-------------------------------------+
| character_set_client     | utf8                                |
| character_set_connection | utf8                                |
| character_set_database   | utf8                                |
| character_set_filesystem | binary                              |
| character_set_results    | utf8                                |
| character_set_server     | utf8                                |
| character_set_system     | utf8                                |
| character_sets_dir       | /usr/share/percona-server/charsets/ |
+--------------------------+-------------------------------------+
8 rows in set (0.00 sec)
```

  * Также не стоит забывать про автоматический бэкап БД.

2 1 684 просмотров [docker](https://it-lux.ru/tag/docker/) [MySQL](https://it-lux.ru/tag/mysql/) [zabbix](https://it-lux.ru/tag/zabbix/)

Понравилась статья? Поделиться с друзьями:

Вам также может быть интересно

[Kubernetes 0 2 595 просмотров](https://it-lux.ru/oidc-%d0%b0%d0%b2%d1%82%d0%be%d1%80%d0%b8%d0%b7%d0%b0%d1%86%d0%b8%d1%8f-%d0%b2-kubernetes-oauth2-proxy-%d0%b4%d0%bb%d1%8f-%d0%bd%d0%b5%d1%81%d0%ba%d0%be%d0%bb%d1%8c%d0%ba%d0%b8%d1%85-%d0%bf%d1%80/)

[OIDC авторизация в Kubernetes: oauth2-proxy для нескольких приложений](https://it-lux.ru/oidc-%d0%b0%d0%b2%d1%82%d0%be%d1%80%d0%b8%d0%b7%d0%b0%d1%86%d0%b8%d1%8f-%d0%b2-kubernetes-oauth2-proxy-%d0%b4%d0%bb%d1%8f-%d0%bd%d0%b5%d1%81%d0%ba%d0%be%d0%bb%d1%8c%d0%ba%d0%b8%d1%85-%d0%bf%d1%80/)

Настройка SSO в oauth2-proxy и nginx ingress для работы с несколькими приложениями на разных

[Kubernetes 0 2 151 просмотров](https://it-lux.ru/argocd-%d0%b4%d0%b5%d0%bf%d0%bb%d0%be%d0%b9-%d0%b2-%d0%bd%d0%b5%d1%81%d0%ba%d0%be%d0%bb%d1%8c%d0%ba%d0%be-%d0%ba%d0%bb%d0%b0%d1%81%d1%82%d0%b5%d1%80%d0%be%d0%b2-%d1%87%d0%b5%d1%80%d0%b5%d0%b7-applica/)

[ArgoCD: деплой в несколько кластеров через ApplicationSet](https://it-lux.ru/argocd-%d0%b4%d0%b5%d0%bf%d0%bb%d0%be%d0%b9-%d0%b2-%d0%bd%d0%b5%d1%81%d0%ba%d0%be%d0%bb%d1%8c%d0%ba%d0%be-%d0%ba%d0%bb%d0%b0%d1%81%d1%82%d0%b5%d1%80%d0%be%d0%b2-%d1%87%d0%b5%d1%80%d0%b5%d0%b7-applica/)

Про деплой в несколько кластеров через один applicationset

[Администрирование 0 2 211 просмотров](https://it-lux.ru/argocd-1-12-x-%d0%be%d1%88%d0%b8%d0%b1%d0%ba%d0%b0-%d0%b4%d0%be%d1%81%d1%82%d1%83%d0%bf%d0%b0-%d0%ba-%d0%bf%d1%80%d0%b8%d0%b2%d0%b0%d1%82%d0%bd%d0%be%d0%bc%d1%83-%d1%80%d0%b5%d0%bf%d0%be%d0%b7%d0%b8/)

[ArgoCD 2.12.x: Ошибка доступа к приватному репозиторию в ApplicationSet](https://it-lux.ru/argocd-1-12-x-%d0%be%d1%88%d0%b8%d0%b1%d0%ba%d0%b0-%d0%b4%d0%be%d1%81%d1%82%d1%83%d0%bf%d0%b0-%d0%ba-%d0%bf%d1%80%d0%b8%d0%b2%d0%b0%d1%82%d0%bd%d0%be%d0%bc%d1%83-%d1%80%d0%b5%d0%bf%d0%be%d0%b7%d0%b8/)

Решение проблемы с авторизацией в приватном репозизитории через argocd в applicationset

[Администрирование 1 3 065 просмотров](https://it-lux.ru/health-%d0%b4%d0%b0%d1%88%d0%b1%d0%be%d1%80%d0%b4-%d0%b2-grafana-%d0%b4%d0%bb%d1%8f-nginx-ingress-controller/)

[Health-дашборд в grafana для nginx ingress controller](https://it-lux.ru/health-%d0%b4%d0%b0%d1%88%d0%b1%d0%be%d1%80%d0%b4-%d0%b2-grafana-%d0%b4%d0%bb%d1%8f-nginx-ingress-controller/)

Health-дашборд в grafana для nginx ingress controller

[Kubernetes 0 2 713 просмотров](https://it-lux.ru/vector-%d0%be%d1%82%d0%bf%d1%80%d0%b0%d0%b2%d0%ba%d0%b0-%d0%bb%d0%be%d0%b3%d0%be%d0%b2-%d0%b2-yandex-sqs-aws-sqs/)

[Vector: отправка логов в Yandex SQS (AWS SQS)](https://it-lux.ru/vector-%d0%be%d1%82%d0%bf%d1%80%d0%b0%d0%b2%d0%ba%d0%b0-%d0%bb%d0%be%d0%b3%d0%be%d0%b2-%d0%b2-yandex-sqs-aws-sqs/)

Краткая заметка по настройке vector по передаче сообщений от k8s в yandex SQS

[Администрирование 0 4 215 просмотров](https://it-lux.ru/java-spring-boot-%d0%bf%d0%be%d0%b4%d0%ba%d0%bb%d1%8e%d1%87%d0%b5%d0%bd%d0%b8%d0%b5-%d0%b2-kafka-%d1%87%d0%b5%d1%80%d0%b5%d0%b7-tls/)

[Java Spring Boot: подключение в Kafka через TLS](https://it-lux.ru/java-spring-boot-%d0%bf%d0%be%d0%b4%d0%ba%d0%bb%d1%8e%d1%87%d0%b5%d0%bd%d0%b8%d0%b5-%d0%b2-kafka-%d1%87%d0%b5%d1%80%d0%b5%d0%b7-tls/)

Пример подключения к Kafka из приложения на Java Spring Boot через mTLS

Комментарии: 2

  1.

Алексей 26.06.2019 в 20:43

Спасибо за статью.

А почему вы в настройках сервера используете один collation-server
collation-server = utf8_unicode_ci
init_connect=»SET collation_connection = utf8_unicode_ci»

а при запуске контейнера уже другой collation-server?
--collation-server=utf8_bin

  2.

admin (автор) 27.06.2019 в 09:03

Спасибо за замечание. Это, конечно же, недочёт, и collation должен быть как в конфиге -- utf8_unicode_ci. Но по идее если параметр при старте контейнера не переопределяет значения (см. через show global) из конфига, то всё не так и критично. Недочёт исправил.

Комментарии закрыты.

**********

[мониторинг](/tags/monitoring.md)
