# Systemd и контейнеры: знакомство с systemd-nspawn

Источник: [Systemd и контейнеры: знакомство с systemd-nspawn](https://habr.com/ru/companies/selectel/articles/271957/)

![PR-1505-3](/images/b6acc68d96fada5d6730a6b41476f2ae.png)

Контейнеризация сегодня — одна из самых актуальныx тем. Количество публикаций о таких популярных инструментах, как LXC или Docker, исчисляется тысячами, если не десятками тысяч.
В этой статье бы хотели мы обсудить ещё одно решение, о котором публикаций на русском языке пока что мало. Речь идёт о [systemd-nspawn](http://www.freedesktop.org/software/systemd/man/systemd-nspawn.html) — инструменте для создания изолированных сред, который является одним из компонентов systemd. А закрепление systemd в качестве стандарта в мире Linux — уже свершившийся факт. В свете этого факта есть все основания полагать, что в ближайшее время сфера применения systemd-nspawn существенно расширится, и познакомиться с этим инструментом поближе стоит уже сейчас.

##  Systemd-nspawn: общая информация

Название systemd-nspawn представляет собой сокращение от namespaces spawn. Уже из этого названия следует, что systemd-nspawn управляет только изоляцией процессов, но при этом не может изолировать ресурсы (однако это можно сделать средствами самого systemd, о чём ещё пойдёт речь ниже).

С помощью systemd-nspawn можно создать полностью изолированое окружение, в котором автоматически будут смонтированы псевдофайловые системы /proc и /sys, а также созданы изолированный loopback-интерфейс и отдельное пространство имён для идентификаторов процессов (PID), внутри которого можно запускать ОС, основанную на ядре Linux.

Cпециального репозитория образов, как в Docker, в systemd-nspawn не существует. Для создания и загрузки образов можно использовать любые сторонние инструменты. Поддерживаются форматы tar, raw, qcow2 и dkr (dkr — это образы для Docker; в документации к systemd-nspawn об этом в явной форме нигде не написано, а её авторы старательно избегают самого слова Docker). Работа с образами осуществляется на базе файловой системы [BTRFS](https://btrfs.wiki.kernel.org/).

## Запускаем в контейнере Debian

Знакомство с systemd-nspawn начнём с простого, но показательного практического примера. На сервере под управлением OC Fedora мы создадим изолированное окружение, в котором будет запущен ОС Debian. Все примеры команд ниже приводятся для Fedora 22 c systemd 219-й версии; в других дистрибутивах Linux и других версиях systemd команды могут отличаться.

Начнём с установки необходимых зависимостей:

```text
sudo dnf install debootstrap bridge-utils
```

Затем создадим файловую систему для будущего контейнера:

```text
sudo debootstrap --arch=amd64 jessie /var/lib/machines/container1/
```

По завершении всех подготовительных работ можно приступать к запуску контейнера:

```text
sudo systemd-nspawn -D /var/lib/machines/container1/ --machine test_container
```

На консоли появится приглашение гостевой операционной системы:

```text
root@test_container
```

Установим для неё root-пароль:

```text
passwd
Enter new UNIX password:
Retype new UNIX password:
passwd: password updated successfully
```

Выйдем из контейнера, нажав комбинацию клавиш Ctrl+]]], а затем выполним следующую команду:

```text
sudo systemd-nspawn -D /var/lib/machines/container1/ --machine test_container  -b
```

В ней присутствует флаг -b (или −−boot), который указывает, что при запуске экземпляра операционной системы в контейнере нужно выполнить init с запуском всех демонов.Этот флаг можно использовать только в случае, если в контейнере будет запущена система с поддержкой systemd.В противном случае загрузка системы не гарантируется.

По завершении всех указанных операций система предложит ввести логин и пароль.
Итак, полноценная ОС в изолированном окружении запущена. Теперь нужно настроить для неё сеть, Выйдем из контейнера и создадим мост, через который он будет соединятся с интерфейсом на основном хосте:

```text
sudo brctl addbr cont-bridge
```

Назначим для этого моста IP-адрес:

```text
ip a a [IP-адрес] dev cont-bridge
```

После этого выполним команду:

```text
sudo systemd-nspawn -D /var/lib/machines/container1/ --machine test_container --network-bridge=cont-bridge -b
```

Для настройки сети можно также воспользоваться опцией −−network-ipvlan, которая свяжет контейнер с указанным интерфейсом на основном хосте с помощью ipvlan:

```text
sudo systemd-nspawn -D /var/lib/machines/container1/ --machine test_container -b --network-ipvlan=[сетевой интерфейс]
```

## Запускаем контейнер как службу

С помощью systemd можно настроить автоматический запуск контейнеров при загрузке системы. Для этого добавим в директорию /etc/systemd/system вот такой конфигурационный файл:

```text
[Unit]

Description=Test Container

[Service]

LimitNOFILE=100000
ExecStart=/usr/bin/systemd-nspawn --machine=test_container --directory=/var/lib/machines/container1/ -b --network-ipvlan=[сетевой интерфейс]
Restart=always

[Install]

Also=dbus.service
```

Прокомментируем приведённый фрагмент. В cекции [Description] мы просто указываем имя контейнера. В секции [Service] мы сначала задаём лимит на количество открытых файлов в контейнере (LimitNOFILE), затем указываем команду на запуск контейнера с необходимыми опциями (ExecStart). Указание Restart=always означает, что контейнер нужно перезапустить в случае «падения». В секции [Install] указывается дополнительный юнит, который должен быть добавлен в автозапуск на хосте (в нашем случае это система межпроцесcного взаимодействия D-Bus).

Сохраним изменения в конфигурационном файле и выполним команду:

```text
sudo systecmctl start test_container
```

Запускать контейнер как службу можно и другим, более простым способом. В systemd имеется заготовка конфигурационного файла для автоматического запуска контейнеров, помещённых в директорию /var/lib/machines. Активировать запуск на базе этой заготовки можно с помощью следующих команд:

```text
sudo systemctl enable machine.target
mv ~/test_container /var/lib/machines/test_container
sudo systemctl enable systemd-nspawn@test_container.service
```

## Управление контейнерами: утилита machinectl

Контейнерами можно управляться с помощью утилиты machinectl. Кратко рассмотрим её основные опции.

Вывести список всех имеющихся в системе контейнеров:

```text
sudo machinectl list
```

Просмотреть информацию о статусе контейнера:

```text
sudo machinectl status test_container
```

Войти в контейнер:

```text
sudo machinectl login test_container
```

Перезагрузить контейнер:

```text
sudo machinectl reboot test_container
```

Остановить контейнер:

```text
sudo machinectl poweroff test_container
```

Последняя команда cработает, если в контейнере установлена ОС, совместимая с systemd. Для операционных систем, использующих sysvinit, нужно воспользоваться опцией terminate.
Мы рассказали лишь о самых базовых возможностях утилиты machinectl; с подробной инструкцией по её использованию можно ознакомиться, например, [здесь](http://www.freedesktop.org/software/systemd/man/machinectl.html).

## Загрузка образов

Выше мы уже говорили, что с помощью systemd-nspawn можно запускать образами любых других форматов. Есть, однако, одно важное условие: работа с образами возможна только на базе файловой системы BTRFS, которую нужно примонтировать к директории /var/lib/machines:

```text
sudo dnf install btrfs-progs
mkfs.btrs /dev/sdb
mount /dev/sdb /var/lib/machines
mount | grep btrfs

dev/sdb on /var/lib/machines type btrfs (rw,relatime,seclabel,space_cache)
```

Если нет свободного диска, BTRFS можно сделать и в файле.
В более новых версиях systemd возможность загрузки образов поддерживается «из коробки», и монтировать BTRFS не нужно.

Попробуем загрузить образ Docker:

```c
sudo machinectl pull-dkr --verify=no library/redis --dkr-index-url=https://index.docker.io
```

Запуск контейнера на базе загруженного образа осуществляется просто:

```text
sudo systemd-nspawn --machine redis
```

## Просмотр логов контейнера

Информация обо всех событиях, происходящих внутри контейнеров, записывается в логи. Настройки логгирования можно устанавливать непосредственно при создании контейнера с помощью опции
−−link-journal, например:

```text
sudo systemd-nspawn -D /var/lib/machines/container1/ --machine test_container -b --link-journal=host
```

Приведённая команда указывает, что логи контейнера будут храниться с на основном хосте в директории /var/log/journal/machine-id. Если же выставить опцию −−link-journal=guest, то вся логи будут храниться в контейнере в директории /var/log/journal/machine-id, а на основном хосте будет создана символическиая ссылка в директории c аналогичным адресом. Опция −−link-journal будет работать только в случае, если в контейнере будет запущена система с systemd. В противном случае корректное логгирование не гарантируется.

Просмотреть информацию о запусках и остановках контейнера можно с помощью утилиты journalctl, о которой мы уже писали [одной из предыдущих публикаций](http://habrahabr.ru/company/selectel/blog/264731/):

```text
 journalctl -u test_container.service
```

В journalctl предусмотрена возможность просмотра логов событий внутри контейнера.
Для этого используется опция -M (приводим лишь небольшой фрагмент вывода):

```text
journalctl -M test_container

Sep 18 11:50:21 octavia.localdomain systemd-journal[16]: Runtime journal is using 8.0M (max allowed 197.6M, trying to leave 296.4M free of 1.9G available <E2><86><92>  current limit 197.6M).
Sep 18 11:50:21 octavia.localdomain systemd-journal[16]: Runtime journal is using 8.0M (max allowed 197.6M, trying to leave 296.4M free of 1.9G available <E2><86><92> current limit 197.6M).
Sep 18 11:50:21 octavia.localdomain systemd-journal[16]: Journal started
Sep 18 11:50:21 octavia.localdomain systemd[1]: Starting Slices.
Sep 18 11:50:21 octavia.localdomain systemd[1]: Reached target Slices.
Sep 18 11:50:21 octavia.localdomain systemd[1]: Starting Remount Root and Kernel File Systems...
Sep 18 11:50:21 octavia.localdomain systemd[1]: Started Remount Root and Kernel File Systems.
Sep 18 11:50:21 octavia.localdomain systemd[1]: Started Various fixups to make systemd work better on Debian.
```

## Выделение ресурсов

Основные особенности systemd-nspawn мы рассмотрели. Остался один важный момент: выделение контейнерам ресурсов. Как уже отмечалось выше, systemd-nspawn ресурсы не изолирует. Ограничить потребление ресурсов для контейнера можно с помощью systemctl, например:

```text
sudo systemctl set-property [имя контейнера] CPUShares=200 CPUQuota=30% MemoryLimit=500M
```

Ограничения ресурсов для контейнера можно прописать и в юнит-файле, в секции [Slice].

## Заключение

Systemd-nspawn — инструмент интересный и перспективный. В числе его несомненных плюсов стоит выделить:

  * тесную интеграцию с другими компонентами systemd;
  * возможность работы с образами в разных форматах;
  * отсутствие необходимости устанавливать какие-либо дополнительные пакеты или накладывать патчи на ядро.

Конечно, говорить о полноценном использовании systemd-nspawn в продакшне пока что рано: инструмент пока что находится в «сыром» состоянии и подходит только для тестирования и экспериментов. Однако по мере дальнейшего распространения systemd стоит ждать и усовершенствования systemd-nspawn.

Естественно, что в рамках обзорной статьи невозможно рассказать абсолютно обо всём. В комментариях приветствуются любые вопросы, замечания и дополнения.
Если мы упустили какие-то детали или не рассказали о каких-то интересных возможностях systemd-nspawn — напишите, и мы обязательно дополним наш обзор.
А если кто-то из вас пользуется systemd-nspawn, приглашаем поделиться опытом.

Читателей, которые по тем или иным причинам не могут оставлять комментарии здесь, [приглашаем в наш блог](https://blog.selectel.ru/systemd-i-kontejnery-znakomstvo-s-systemd-nspawn/).

**********

[systemd](/tags/systemd.md)
[systemd-nspawn](/tags/systemd_nspawn.md)
