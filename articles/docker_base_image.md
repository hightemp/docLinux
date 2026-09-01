# Создание базового изображения

Большинство Dockerfiles начинаются с родительского образа. Если вам необходимо полностью контролировать содержимое вашего изображения, вам может потребоваться создать базовое изображение. Вот разница:

*   [Родительское изображение](https://docs.docker.com/glossary/?term=parent%20image) - это изображение, на котором основано ваше изображение. Это относится к содержанию директивы `FROM` в Dockerfile. Каждое последующее объявление в Dockerfile изменяет этот родительский образ. Большинство файлов Docker начинаются с родительского изображения, а не с базового изображения. Однако термины иногда используются взаимозаменяемо.
    
*   [Базовое изображение](https://docs.docker.com/glossary/?term=base%20image) либо не имеет строки `FROM` в своем Dockerfile, либо имеет `FROM scratch`.
    
В этом разделе показано несколько способов создания базового изображения. Конкретный процесс будет сильно зависеть от дистрибутива Linux, который вы хотите упаковать. У нас есть несколько примеров ниже, и вам предлагается отправлять запросы на добавление новых.

## Создать полное изображение, используя tar

В общем, начните с работающей машины, на которой выполняется дистрибутив, который вы хотели бы упаковать как родительский образ, хотя это не требуется для некоторых инструментов, таких как Debian [Debootstrap](https://wiki.debian.org/Debootstrap), который вы также можете использовать для создания образов Ubuntu.

Создать родительский образ Ubuntu очень просто:

```console
$ sudo debootstrap xenial xenial > /dev/null
$ sudo tar -C xenial -c . | docker import - xenial

a29c15f1bf7a

$ docker run xenial cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=16.04
DISTRIB_CODENAME=xenial
DISTRIB_DESCRIPTION="Ubuntu 16.04 LTS"

```

Еще несколько примеров сценариев для создания родительских изображений в Docker GitHub Repo:

* [BusyBox](https://github.com/moby/moby/blob/master/contrib/mkimage/busybox-static) 
* CentOS / Scientific Linux CERN (SLC) [on Debian/Ubuntu](https://github.com/moby/moby/blob/master/contrib/mkimage/rinse) или же [on CentOS/RHEL/SLC/etc.](https://github.com/moby/moby/blob/master/contrib/mkimage-yum.sh) 
* [Debian / Ubuntu](https://github.com/moby/moby/blob/master/contrib/mkimage/debootstrap) 

## Создать простое родительское изображение с помощью scratch

Вы можете использовать зарезервированное минимальное изображение Docker `scratch`, в качестве отправной точки для построения контейнеров. Использование «scratch» «image» сигнализирует процессу сборки, что следующая команда в `Dockerfile` должна быть первым слоем файловой системы в вашем изображении.

Пока в хранилище Docker на концентраторе появляется `scratch`, вы не можете вытащить его, запустить или пометить любое изображение с именем `scratch`. Вместо этого вы можете обратиться к нему в вашем `Dockerfile`. Например, чтобы создать минимальный контейнер, используя `scratch`:

```Dockerfile
FROM scratch
ADD hello /
CMD ["/hello"]

```

Предполагая, что вы создали исполняемый пример «hello», следуя инструкциям на [https://github.com/docker-library/hello-world/](https://github.com/docker-library/hello-world/ ), и вы скомпилировали его с флагом `-static`, вы можете создать этот образ Docker с помощью команды `docker build`:

```
docker build --tag hello .
```

Не забывайте символ `.` в конце, который устанавливает контекст сборки для текущего каталога.

>  **Note** : Because Docker Desktop for Mac and Docker Desktop for Windows use a Linux VM, you need a Linux binary, rather than a Mac or Windows binary. You can use a Docker container to build it:
> 
> ```
> $ docker run --rm -it -v $PWD:/build ubuntu:16.04
> 
> container# apt-get update && apt-get install build-essential
> container# cd /build
> container# gcc -o hello -static -nostartfiles hello.c
> 
> ```

Чтобы запустить новый образ, используйте команду `docker run`:

```
docker run --rm hello

```

В этом примере создается изображение hello-world, используемое в руководствах. Если вы хотите проверить это, вы можете клонировать [репозиторий](https://github.com/docker-library/hello-world).

## Больше ресурсов

Есть много других доступных ресурсов, которые помогут вам написать свой `Dockerfile`.

* [Полное руководство по всем инструкциям](https://docs.docker.com/engine/reference/builder/) доступно для использования в `Dockerfile` в справочном разделе.
* Чтобы помочь вам написать понятный, читаемый и поддерживаемый `Dockerfile`, мы также написали [Руководство по оптимальным методам Dockerfile](https://docs.docker.com/develop/develop-images/dockerfile_best-practices /).
* Если ваша цель - создать новый официальный образ, обязательно ознакомьтесь с [Официальными изображениями](https://docs.docker.com/docker-hub/official_images/).

**********
[docker](/tags/docker.md)
[Dockerfile](/tags/Dockerfile.md)
