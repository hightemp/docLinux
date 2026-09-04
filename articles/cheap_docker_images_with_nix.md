# Дешёвые Docker-образы с Nix

Источник: [Cheap Docker images with Nix](https://lucabrunox.github.io/2016/04/cheap-docker-images-with-nix_15.html)

Luca Bruno · 15 апреля 2016

Сегодня поговорим о [Docker](https://www.docker.com/) и [Nix](http://nixos.org/nix/). Прежде чем объяснить, что такое Nix, если вы ещё не знаете, и прежде чем углубляться в детали, я покажу вам фрагмент, похожий на Dockerfile, для создания образа Redis, эквивалентного образу из [docker hub](https://github.com/docker-library/redis/blob/master/3.0/Dockerfile).

Итоговый образ будет размером около **42 МБ** (или **25 МБ**) против 177 МБ.

ПРАВКА: как заметили на HN, [образы на базе alpine](https://github.com/docker-library/redis/blob/7dec62fe6de187165dce3f771efa57ce4e5d7a32/3.0/alpine/Dockerfile) могут быть ещё меньше — около 15 МБ.

Если хотите попробовать, первый шаг — [установить Nix](http://nixos.org/nix/download.html).

Вот фрагмент `redis.nix`:

```nix
{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
  entrypoint = writeScript "entrypoint.sh" ''
    #!${stdenv.shell}
    set -e
    # allow the container to be started with `--user`
    if [ "$1" = "redis-server" -a "$(${coreutils}/bin/id -u)" = "0" ]; then
      chown -R redis .
      exec ${goPackages.gosu.bin}/bin/gosu redis "$BASH_SOURCE" "$@"
    fi
    exec "$@"
  '';
in
dockerTools.buildImage {
  name = "redis";
  runAsRoot = ''
    #!${stdenv.shell}
    ${dockerTools.shadowSetup}
    groupadd -r redis
    useradd -r -g redis -d /data -M redis
    mkdir /data
    chown redis:redis /data
  '';

  contents = [ redis ];

  config = {
    Cmd = [ "redis-server" ];
    Entrypoint = [ entrypoint ];
    ExposedPorts = {
      "6379/tcp" = {};
    };
    WorkingDir = "/data";
    Volumes = {
      "/data" = {};
    };
  };
}
```

Соберите его командой: `nix-build redis.nix`
Загрузите командой: `docker load < result`

После загрузки вы увидите с помощью `docker images`, что он занимает около 42 МБ.

## Принципиальные отличия от классических docker-сборок

* Мы не используем никакой базовый образ, как это делается в большинстве docker-образов, включая [redis из hub](https://hub.docker.com/_redis/). Всё начинается с нуля. Фактически мы настраиваем несколько базовых файлов, связанных с shadow, с помощью утилиты `shadowSetup` — этого достаточно, чтобы добавить пользователя redis и заставить `gosu` работать.
* Пакет Redis не компилируется внутри Docker. Это делает Nix, как и для любого другого пакета.
* Собранный образ имеет всего один слой, по сравнению с десятками, которые обычно выдаёт читаемый `Dockerfile`. В нашем случае наличие множества слоёв бесполезно, потому что кэшированием управляет Nix, а не Docker.

## Образ поменьше

Мы можем урезать размер до **25 МБ**, отказавшись от использования id из coreutils. Для примера мы всегда будем запускать redis без entrypoint:

```nix
{ pkgs ? import <nixpkgs> {} }:

with pkgs;
dockerTools.buildImage {
  name = "redis";
  runAsRoot = ''
    #!${stdenv.shell}
    ${dockerTools.shadowSetup}
    groupadd -r redis
    useradd -r -g redis -d /data -M redis
    mkdir /data
    chown redis:redis /data
  '';

  config = {
    Cmd = [ "${goPackages.gosu.bin}/bin/gosu" "redis" "${redis}/bin/redis-server" ];
    ExposedPorts = {
      "6379/tcp" = {};
    };
    WorkingDir = "/data";
    Volumes = {
      "/data" = {};
    };
  };
}
```

Вы можете спросить: но coreutils всё равно нужен для `chown`, `mkdir` и подобных команд!

Секрет в том, что эти команды используются только во время сборки и не нужны во время выполнения в контейнере. Nix способен определить это для нас автоматически.

Это значит, что нам не нужно вручную удалять пакеты после сборки контейнера, как с другими менеджерами пакетов! См., например, [эту строку](https://github.com/docker-library/redis/blob/master/3.0/Dockerfile#L40) в `Dockerfile` Redis.

## Использование другой версии redis

Допустим, мы хотим собрать Docker-образ с Redis 2.8.23. Сначала мы хотим написать пакет (или _деривацию_ — derivation, как говорят в мире Nix) для него, а затем использовать его внутри образа:

```nix
{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
  redis = pkgs.redis.overrideDerivation (attrs: rec {
    name = "redis-2.8.23";
    src = fetchurl {
      url = "http://download.redis.io/releases/${name}.tar.gz";
      sha256 = "1kjsx79jhhssh5k9v17s9mifaclkl6mfsrsv0cvi583qyiw9gizk";
    };
  });
in
dockerTools.buildImage {
  name = "redis";
  tag = "2.8.23";

  runAsRoot = ''
    #!${stdenv.shell}
    ${dockerTools.shadowSetup}
    groupadd -r redis
    useradd -r -g redis -d /data -M redis
    mkdir /data
    chown redis:redis /data
  '';

  config = {
    Cmd = [ "${goPackages.gosu.bin}/bin/gosu" "redis" "${redis}/bin/redis-server" ];
    ExposedPorts = {
      "6379/tcp" = {};
    };
    WorkingDir = "/data";
    Volumes = {
      "/data" = {};
    };
  };
}
```

Обратите внимание, что мы также добавили тег 2.8.23 к итоговому образу. И это всё. Красота в том, что мы переиспользуем то же выражение redis из nixpkgs, но переопределяем только собираемую версию.

## Универсальная сборка

С Nix можно сделать больше. Поскольку это язык, можно создать универсальную функцию для сборки образов Redis по заданному пакету:

```nix
{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
  redis_3_0_7 = pkgs.redis.overrideDerivation (attrs: rec {
    version = "3.0.7";
    name = "redis-${version}";
    src = fetchurl {
      url = "http://download.redis.io/releases/${name}.tar.gz";
      sha256 = "08vzfdr67gp3lvk770qpax2c5g2sx8hn6p64jn3jddrvxb2939xj";
    };
  });

  redis_2_8_23 = pkgs.redis.overrideDerivation (attrs: rec {
    version = "2.8.23";
    name = "redis-${version}";
    src = fetchurl {
      url = "http://download.redis.io/releases/${name}.tar.gz";
      sha256 = "1kjsx79jhhssh5k9v17s9mifaclkl6mfsrsv0cvi583qyiw9gizk";
    };
  });

  redisImage = redis: dockerTools.buildImage {
    name = "redis";
    tag = redis.version;

    runAsRoot = ''
      #!${stdenv.shell}
      ${dockerTools.shadowSetup}
      groupadd -r redis
      useradd -r -g redis -d /data -M redis
      mkdir /data
      chown redis:redis /data
    '';

    config = {
      Cmd = [ "${goPackages.gosu.bin}/bin/gosu" "redis" "${redis}/bin/redis-server" ];
      ExposedPorts = {
        "6379/tcp" = {};
      };
      WorkingDir = "/data";
      Volumes = {
        "/data" = {};
      };
    };
  };

in {
  redisDocker_3_0_7  = redisImage redis_3_0_7;
  redisDocker_2_8_23 = redisImage redis_2_8_23;
}
```

Мы создали функцию «redisImage», которая принимает параметр «redis» на входе и возвращает Docker-образ на выходе.

Соберите её командами:

* `nix-build redis-generic.nix -A redisDocker_3_0_7`
* `nix-build redis-generic.nix -A redisDocker_2_8_23`

## Сборка на основе базового образа

Один из аргументов в пользу Docker — переиспользование существующего образа, чтобы добавить поверх него больше содержимого.

Nix поставляется с совершенно другим набором пакетов по сравнению с другими дистрибутивами, со своим собственным тулчейном и версией glibc. Но это не значит, что нельзя создать новый образ на основе существующего образа Debian, например.

С помощью `dockerTools.pullImage` также можно скачивать образы из Docker hub.

```nix
{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
  redis_3_0_7 = pkgs.redis.overrideDerivation (attrs: rec {
    version = "3.0.7";
    name = "redis-${version}";
    src = fetchurl {
      url = "http://download.redis.io/releases/${name}.tar.gz";
      sha256 = "08vzfdr67gp3lvk770qpax2c5g2sx8hn6p64jn3jddrvxb2939xj";
    };
  });

  redis_2_8_23 = pkgs.redis.overrideDerivation (attrs: rec {
    version = "2.8.23";
    name = "redis-${version}";
    src = fetchurl {
      url = "http://download.redis.io/releases/${name}.tar.gz";
      sha256 = "1kjsx79jhhssh5k9v17s9mifaclkl6mfsrsv0cvi583qyiw9gizk";
    };
  });

  redisImage = redis: baseImage: dockerTools.buildImage {
    name = "redis";
    tag = redis.version;
    fromImage = baseImage;

    runAsRoot = ''
      #!${stdenv.shell}
      export PATH=/bin:/usr/bin:/sbin:/usr/sbin:$PATH
      ${if baseImage == null then dockerTools.shadowSetup else ""}
      groupadd -r redis
      useradd -r -g redis -d /data -M redis
      mkdir /data
      chown redis:redis /data
    '';

    config = {
      Cmd = [ "${goPackages.gosu.bin}/bin/gosu" "redis" "${redis}/bin/redis-server" ];
      ExposedPorts = {
        "6379/tcp" = {};
      };
      WorkingDir = "/data";
      Volumes = {
        "/data" = {};
      };
    };
  };

  debianImage = dockerTools.pullImage {
    imageName = "debian";
    sha256 = "08w22gx6hmmq75rybqzrxs03nzq2k39lrcj291yhsc08p9d9l9cj";
  };

in {
  redisDocker_3_0_7  = redisImage redis_3_0_7 null;
  redisDocker_2_8_23 = redisImage redis_2_8_23 null;
  redisOnDebian = redisImage redis_3_0_7 debianImage;
}
```

Соберите командой: `nix-build redis-generic.nix -A redisOnDebian`.

Обратите внимание, что мы добавили пару вещей. Мы передаём базовый образ (`debianImage`) в нашу универсальную функцию `redisImage` и инициализируем shadow-utils только если базовый образ равен null.

В результате получается Docker-образ на базе последнего Debian, но с Redis, скомпилированным тулчейном nixpkgs и использующим glibc из nixpkgs. Он размером около 150 МБ. В нём все слои базового образа плюс новый единственный слой для Redis.

Впрочем, можно использовать и один из ранее определённых образов Redis в качестве базового. Результат `pullImage` и `buildImage` в обоих случаях — это docker-образ в виде .tar.gz.

Вы понимаете, что можно собрать нечто весьма похожее на [docker-library](https://github.com/docker-library), используя только выражения Nix. Возможно, это интересный проект.

_Имейте в виду: такие вещи, как конфигурации PAM и прочее, созданные для Debian, могут не работать с программами Nix, которые используют другую glibc._

## Другие разные детали

Код выше стал возможен благодаря коммиту nixpkgs 3ae4d2afe (2016-04-14) и более поздним — коммиту, в котором я наконец упаковал `gosu`, и с тех пор размер дериваций заметно уменьшился.

Сборка образа выполняется без использования каких-либо команд Docker. Работает это так:

1. Создаётся каталог слоя со всем произведённым содержимым внутри. Сюда входят как файловая система, так и метаданные json. Этот процесс использует определённые зависимости сборки (например, `coreutils`, `shadow-utils`, `bash`, `redis`, `gosu`, …).
2. Nix спрашивается, каковы зависимости времени выполнения для каталога слоя (например, `redis`, `gosu`). Такие зависимости всегда будут подмножеством зависимостей сборки.
3. Такие зависимости времени выполнения добавляются в каталог слоя.
4. Слой упаковывается в .tar.gz согласно [спецификации Docker](https://github.com/docker/docker/blob/master/image/spec/v1.md).

Хочу отметить, что **у Nix более безопасное и простое кэширование** операций при сборке образа.
Что касается Docker, нужно проявлять большую осторожность, чтобы правильно использовать кэш слоёв, потому что такое кэширование основано исключительно на строке команды `RUN`. Этот [пост в блоге](http://thenewstack.io/understanding-the-docker-cache-for-faster-builds/) хорошо это объясняет.
Для Nix это не так, потому что каждый вывод зависит от набора точных входных данных. Если какой-либо из входов меняется, вывод будет пересобран.

## Так что же такое Nix?

[Nix](http://nixos.org/nix/) — это язык и инструмент развёртывания, часто используемый как менеджер пакетов, конструктор конфигураций и средство подготовки систем. Операционная система [NixOS](http://nixos.org/nixos) основана на нём.

Показанный выше код — это Nix. Мы использовали репозиторий [nixpkgs](https://github.com/NixOS/nixpkgs), который предоставляет множество переиспользуемых выражений Nix, таких как [redis](https://github.com/NixOS/nixpkgs/blob/master/pkgs/servers/nosql/redis/default.nix) и [dockerTools](https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/docker/default.nix).

Концепция Nix проста: напишите выражение Nix, соберите его. Вот как работает процесс сборки на высоком уровне:

1. Прочитать выражение Nix
2. Вычислить его и определить сущность (называемую _деривацией_), которую нужно собрать.
3. Вычисляя код, Nix способен точно определить входные данные сборки, необходимые для такой деривации.
4. Собрать (или взять из кэша) все нужные входы.
5. Собрать (или взять из кэша) итоговую деривацию.

Nix хранит все такие деривации в общем nix store (обычно `/nix/store`), идентифицируемом по хешу. Каждая деривация может иметь зависимости от других путей в том же хранилище. Каждая деривация хранится в отдельном от других дериваций каталоге.

Не буду углубляться дальше — о том, как работает Nix и его хранилище, есть множество документации.

Надеюсь, чтение было приятным, и вы дадите Nix шанс.

**********

[nix](/tags/nix.md)
[docker](/tags/docker.md)
[nixos](/tags/nixos.md)