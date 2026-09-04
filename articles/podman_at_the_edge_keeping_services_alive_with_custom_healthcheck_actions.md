# Podman на edge: поддержание жизни сервисов с помощью пользовательских действий healthcheck

Источник: [Podman at the edge: Keeping services alive with custom healthcheck actions](https://www.redhat.com/en/blog/podman-edge-healthcheck)

Valentin Rothberg, Matthew Heon, Preethi Thomas · 17 ноября 2022 · 12 мин

Podman хорошо известен своей тесной [интеграцией с systemd](https://www.redhat.com/sysadmin/improved-systemd-podman). Запуск контейнеризованных рабочих нагрузок под управлением systemd — простой, но мощный способ добиться надёжных и нерушимых развёртываний. Интеграция с systemd дополнительно закладывает фундамент для более продвинутых возможностей Podman, таких как [автообновления и откат](https://www.redhat.com/sysadmin/podman-auto-updates-rollbacks) или запуск [рабочих нагрузок Kubernetes в systemd](https://www.redhat.com/sysadmin/kubernetes-workloads-podman-systemd). Эта интеграция позволяет systemd управлять зависимостями сервисов, отслеживать жизненный цикл и состояние служб, а также, при необходимости, перезапускать службы в случае сбоя.

Такие надёжные, самовосстанавливающиеся и самообновляющиеся развёртывания критически важны для [edge-развёртываний](https://www.redhat.com/en/topics/edge-computing?intcmp=701f20000012ngPAAQ), где распределённые и частично отключённые узлы порой должны работать автономно. Мы рады представить новую возможность — пользовательские действия health-check — в Podman v4.3. Эта функция ещё больше расширяет возможности Podman в сценариях периферийных вычислений (edge computing).

Podman уже некоторое время поддерживает healthcheck'и для выявления деградировавших [контейнеров](https://www.redhat.com/en/topics/containers?intcmp=701f20000012ngPAAQ), но способа автоматически исправлять их не было. Действия healthcheck позволяют пользователям настроить, как Podman отреагирует, когда контейнер станет нездоровым (unhealthy). Например, нездоровый контейнер можно перезапустить автоматически. В этой статье рассматривается, как работают healthcheck'и и как настраивать такие пользовательские действия.

## Что такое healthcheck'и?

Как следует из названия, healthcheck'и используются для проверки здоровья рабочей нагрузки внутри контейнера. Если healthcheck проходит успешно, контейнер помечается как «healthy»; в противном случае — как «unhealthy». Healthcheck можно сравнить с запуском `podman exec` и анализом кода выхода.

Представьте, что у вас в контейнере работает база данных. Правильный healthcheck проверяет, запущена ли база данных и функционирует ли она корректно. Healthcheck может, например, выполнить ряд запросов к базе данных и провести дополнительные тесты, специфичные для рабочей нагрузки. Если healthcheck завершается с нулевым кодом выхода, контейнер «healthy».

Healthcheck'и можно задавать при сборке образа с помощью [инструкции HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck) в Dockerfile или при создании контейнера из командной строки. Статус healthcheck отражается при инспекции контейнеров через `podman inspect` или при выводе списка контейнеров через `podman ps`, что чрезвычайно полезно для мониторинга здоровья контейнеров.

До выпуска Podman v4.3 мониторинг был всем, что можно было делать с healthcheck'ами. Не было способа отреагировать, когда контейнер становился нездоровым. Поэтому внешним инструментам приходилось опрашивать состояния здоровья контейнеров, чтобы, например, перезапускать нездоровые контейнеры.

## Задание пользовательских действий healthcheck

Начиная с Podman v4.3 можно указывать пользовательские действия healthcheck, которые будут выполняться, когда контейнер становится нездоровым. Таких действий четыре:

* **restart**: Podman перезапускает контейнер.
* **stop**: Podman останавливает контейнер.
* **kill**: Podman убивает контейнер.
* **none**: Podman ничего не делает. Используется по умолчанию.

Действие «kill» хорошо интегрируется с systemd. Когда контейнер Podman работает внутри systemd-юнита, контейнер может использовать встроенные политики перезапуска systemd. В случае сбоя — например, когда контейнер завершается с ненулевым кодом выхода — systemd обнаруживает, что контейнер упал, и автоматически перезапускает весь сервис, включая контейнер. Аналогично, установка действия on-failure для healthcheck в «kill» присвоит упавшему контейнеру ненулевой код выхода, и systemd перезапустит весь сервис. Действие «stop» может вести себя иначе, поскольку контейнер при остановке может завершиться чисто, без сбоя.

Опция «restart» можно использовать вне systemd — она поможет поддерживать контейнер живым и здоровым. Действие «none» установлено по умолчанию для сохранения обратной совместимости с предыдущими версиями Podman. Эти действия задаются с помощью нового флага командной строки `--health-on-failure`.

Чтобы собрать всё воедино, рассмотрим следующий пример.

Сначала создайте образ контейнера с healthcheck. Для сборки образа начните с создания временного каталога, скрипта для запуска healthcheck и скрипта, служащего точкой входа, который будет ждать получения SIGTERM и завершаться:

```bash
$ export TEMPDIR=$(mktemp -d)
$ cat >${TEMPDIR}/healthcheck <<EOF
#!/bin/sh

if test -e /uh-oh; then
     	exit 1
    else
     	exit 0
    fi
    EOF

 $ cat >${TEMPDIR}/entrypoint <<EOF
#!/bin/sh

trap 'echo Received SIGTERM, finishing; exit' SIGTERM; echo WAITING; while :; do sleep 0.1; done
EOF
```

Теперь создайте Dockerfile и скопируйте два скрипта в образ.

```bash
$ cat >${TEMPDIR}/Dockerfile <<EOF
FROM registry.access.redhat.com/ubi9:latest

COPY healthcheck /healthcheck
COPY entrypoint  /entrypoint

RUN  chmod 755 /healthcheck /entrypoint
CMD ["/entrypoint"]
EOF

$ podman build -t health-check-actions ${TEMPDIR}
```

Далее используйте образ `health-check-actions`, чтобы создать контейнер с действием по умолчанию «none»:

```bash
$ podman run --replace -d --name test-container --health-cmd /healthcheck --health-on-failure=none --health-retries=1 health-check-actions

$ podman healthcheck run test-container

$ podman ps
CONTAINER ID  IMAGE                              	COMMAND  	CREATED     	STATUS                   	PORTS   	NAMES
90bb778b1a7d  localhost/health-check-actions:latest  /entrypoint  34 seconds ago  Up 34 seconds ago (healthy)          	test-container
```

Контейнер запущен и находится в здоровом состоянии. Теперь вызовите сбой healthcheck, создав файл `/uh-oh` в корневой файловой системе контейнера. Healthcheck теперь будет падать, но контейнер продолжит работать, так как никакое действие выполняться не будет.

```bash
$ podman exec test-container touch /uh-oh
$ podman healthcheck run test-container
unhealthy
$ podman ps
CONTAINER ID  IMAGE                              	COMMAND  	CREATED     	STATUS                     	PORTS   	NAMES
65e61ad28632  localhost/health-check-actions:latest  /entrypoint  20 seconds ago  Up 20 seconds ago (unhealthy)          	test-container
```

Пересоздайте контейнер с действием «kill». В этом случае Podman должен убить контейнер, как только тот станет нездоровым.

```bash
$ podman run --replace -d --name test-container --health-cmd /healthcheck --health-on-failure=kill --health-retries=1 health-check-actions

$ podman ps
CONTAINER ID  IMAGE                              	COMMAND  	CREATED    	STATUS                  	PORTS   	NAMES
157aa6af4ee3  localhost/health-check-actions:latest  /entrypoint  7 seconds ago  Up 7 seconds ago (healthy)          	test-container

$ podman exec test-container touch /uh-oh
unhealthy

$ podman ps -a
CONTAINER ID  IMAGE                              	COMMAND  	CREATED     	STATUS                              	PORTS   	NAMES
157aa6af4ee3  localhost/health-check-actions:latest  /entrypoint  37 seconds ago  Exited (137) 9 seconds ago (unhealthy)          	test-container
```

Обратите внимание, что контейнер завершился с кодом 137. Сочетание действия on-failure «kill» с [запуском Podman под systemd](https://www.redhat.com/sysadmin/improved-systemd-podman) отлично работает для достижения нерушимых самовосстанавливающихся рабочих нагрузок. systemd автоматически перезапустит контейнер, чтобы вернуть рабочую нагрузку в здоровое состояние.

## Подводя итог

Возможность следить за здоровьем контейнеров критически важна, когда у вас контейнеризованные сервисы работают в продакшене. Ещё важнее это, когда сервисы находятся в удалённых местах или на критических системах.

Тесная интеграция Podman с systemd закладывает основу для многих сценариев использования, таких как [автообновления и откат](https://www.redhat.com/sysadmin/podman-auto-updates-rollbacks) или запуск [рабочих нагрузок Kubernetes в systemd](https://www.redhat.com/sysadmin/kubernetes-workloads-podman-systemd). Начиная с Podman v4.3 можно дополнительно использовать пользовательские действия health-check, которые в сочетании с запуском Podman под systemd создают идеальную среду для запуска контейнеров в окружении периферийных вычислений.

**********

[linux](/tags/linux.md)
[systemd](/tags/systemd.md)