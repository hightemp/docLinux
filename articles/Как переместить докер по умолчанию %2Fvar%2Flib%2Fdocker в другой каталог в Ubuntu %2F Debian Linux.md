# Как переместить докер из /var/lib/docker в другой каталог в Ubuntu / Debian Linux

Следующая конфигурация проведет вас через процесс изменения дискового пространства по умолчанию для докера /var/lib/docker на другой каталог. Существуют различные причины, по которым вы можете захотеть изменить каталог докера по умолчанию, из которых наиболее очевидным может быть то, что не хватило места на диске. Следующее руководство должно работать как для Ubuntu, так и для Debian Linux или любой другой системы systemd. Обязательно следуйте этому руководству в точном порядке исполнения.
  
Давайте начнем с изменения сценария запуска докера systemd. Откройте файл `/lib/systemd/system/docker.service` в вашем любимом текстовом редакторе и замените следующую строку, где `/new/path/docker` - это местоположение вашего нового выбранного каталога докеров:

```
FROM:
ExecStart=/usr/bin/docker daemon -H fd://
TO:
ExecStart=/usr/bin/docker daemon -g /new/path/docker -H fd://
```

Когда будете готовы остановить сервис докеров:

```console
$ systemctl stop docker
```

Здесь важно, чтобы вы полностью остановили демон Docker. Следующая [команда linux](https://linuxconfig.org/linux-commands) не выдаст никаких результатов, только если служба Docker остановлена:

```console
$ ps aux | grep -i docker | grep -v grep
```

Если вышеприведенная команда не произвела никакого вывода, перезагрузите демон systemd:

```console
$ systemctl daemon-reload
```

Как только это будет сделано, создайте новый каталог, который вы указали выше, и, необязательно, текущие данные докера rsync в новый каталог:

```console
$ mkdir /new/path/docker
$ rsync -aqxP /var/lib/docker/ /new/path/docker
```

На этом этапе мы можем безопасно запустить Docker Daemon:

```console
$ systemctl start docker
```

Убедитесь, что Docker работает в новом каталоге данных:

```console
$  ps aux | grep -i docker | grep -v grep
root      2095  0.2  0.4 664472 36176 ?        Ssl  18:14   0:00 /usr/bin/docker daemon -g  /new/path/docker -H fd://
root      2100  0.0  0.1 360300 10444 ?        Ssl  18:14   0:00 docker-containerd -l /var/run/docker/libcontainerd/docker-containerd.sock --runtime docker-runc
```

Все сделано.

**********
[docker](/tags/docker.md)
[Ubuntu](/tags/Ubuntu.md)
