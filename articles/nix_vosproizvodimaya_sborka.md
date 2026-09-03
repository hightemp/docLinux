# Nix: воспроизводимая сборка

Источник: [Nix: воспроизводимая сборка](https://habr.com/ru/companies/typeable/articles/556828/)

![](/images/af6b7774434400c52d717ed8aea1e584.png)

Привет, Хаброюзеры!

Сегодня мы продолжим наш цикл статей о Nix и как мы в Typeable его используем.

Первый пост из серии, рассказывающий об основах языка Nix, можно прочитать [здесь](https://habr.com/ru/company/typeable/blog/550860/).

Так как мы очень любим и много используем Haskell для разработки, пример приложения будет на этом языке, но знание Haskell здесь никак не требуется. С лёгким допиливанием, код из примеров можно использовать и для сборки проектов на других языках.

Весь код для этой статьи можно найти в [репозитарии на Github](https://github.com/typeable/nix-reproducible-example).

## Проблема

Сборка и CI — одни из самых больших проблем в разработке софта. На поддержку сборочной инфраструктуры очень часто уходит невообразимое количество ресурсов. С помощью Nix мы попытаемся если не исправить ситуацию, то сделать её немного более приемлемой. Nix позволяет нам обеспечить воспроизводимость сборки наших проектов, переносимость между разными ОС, унифицировать сборку компонентов на различных языках и так далее.

## Наше приложение

Итак, начнём с приложения, которое мы хотим собрать. В нашем случае, это будет простая программа на языке Haskell, выводящая сообщение Hello world.

Наш `Main.hs`:

```text
module Main where

main :: IO ()
main = putStrLn "Hello, World!"
```

Для сборки проекта без Nix мы используем утилиту `stack` (подробнее с ней можно ознакомиться [здесь](https://docs.haskellstack.org/en/stable/README/)). В качестве описания проекта для stack требуется файл `stack.yaml`, содержащий список наших пакетов и `resolver`. Последнее — это стабильный срез Hackage, базы пакетов для языка Haskell, в котором гарантируется, что все пакеты собираются и дружат друг с другом (NB подобных срезов крайне не хватает в других языках ): ).

`stack.yaml`:

```text
resolver: lts-17.11

packages:
- hello-world
```

Рецепт сборки конкретного пакета находится в `hello-world.cabal`:

```text
cabal-version:      2.4
name:               hello-world
version:            1.0
synopsis:           Hello World
license:            MIT
license-file:       LICENSE
author:             Nick

executable hello-world
    main-is:          Main.hs
    build-depends:    base >= 4 && < 5
    hs-source-dirs:   src
    default-language: Haskell2010
    ghc-options:      -Wall -O2
```

Из этих двух файлов наш код на Nix и будет черпать информацию о том, что именно и как собирать. В качестве эксперимента, можем проверить, что наш код действительно запускается и работает:

```bash
$ stack run hello-world
Hello, World!
```

## Come to the dar^Wnix side, we have cookies!

Сам по себе stack — отличное средство для сборки проектов на Haskell, но в нём не хватает многих возможностей. Для сборки программ на Haskell для Nix есть библиотека [haskell.nix](https://input-output-hk.github.io/haskell.nix/), разработанная компанией [IOHK](https://iohk.io). Её-то мы и будем здесь использовать. Для начала, сделаем так, чтобы наш проект собирался с помощью Nix.

Haskell.nix позволяет нам в несколько строчек преобразовать всю информацию о сборке нашего проекта из `.cabal`-файлов и `stack.yaml` в `derivation` для Nix.

`nix/stackyaml.nix`:

```c
{
  # Импортируем последнюю версию haskell.nix с GitHub и инициализируем Nixpkgs с её использованием.
  haskellNix ? import (builtins.fetchTarball "https://github.com/input-output-hk/haskell.nix/archive/b0d03596f974131ab64d718b98e16f0be052d852.tar.gz") {}
  # Здесь мы используем последнюю стабильную версию Nixpkgs. Версия 21.05 скоро выйдет :)
, nixpkgsSrc ? haskellNix.sources.nixpkgs-2009
, nixpkgsArgs ? haskellNix.nixpkgsArgs
, pkgs ? import nixpkgsSrc nixpkgsArgs
}:
```

```text
let
  # Создаём проект на базе stack. Для проектов Cabal есть функция cabalProject.
  project = pkgs.haskell-nix.stackProject {
    name = "hello-world";

    # Derivation с исходным кодом проекта.
    # Функция cleanGit копирует для сборки проекта только файлы, присутствующие в нашем git-репозитарии.
    src = pkgs.haskell-nix.haskellLib.cleanGit {
      name = "hello-world";

      # Параметр src должен указывать на корневую директорию, содержащую stack.yaml.
      src = ../.;

      # keepGitDir оставляет директорию .git при сборке.
      # Это может быть полезно, например, чтобы вставить хэш коммита в код.
      keepGitDir = true;
    };

    # В параметре modules можно указать параметры сборки как для всех модулей сразу, так и для каждого в отдельности.
    modules = [{
      # doCheck отвечает за запуск юнит-тестов при сборке проекта, в том числе содержащихся во всех зависимостях.
      # Здесь мы этого хотим избежать, поэтому этот параметр лучше всего ставить false и включить только для нужных
      # пакетов.
      doCheck = false;

      # Добавим для нашего Hello World флаг -Werror.
      packages.hello-world.components.exes.hello-world.ghcOptions = [ "-Werror" ];
    }];
  };

# Наружу из этого файла мы выставляем project -- наш проект, а также pkgs -- срез nixpkgs, который мы будем использовать дальше.
in { inherit project; inherit pkgs; }
```

Давайте проверим, что наш проект теперь можно собрать через Nix. Для этого достаточно команды `nix build`. Как и всегда, в текущей директории будет создана символическая ссылка `result`, содержащая результаты сборки.

```bash
$ nix build project.hello-world.components.exes
$ ./result/bin/hello-world
Hello, World!
```

Отлично! Небольшой магией выше мы обеспечили полностью воспроизводимую сборку нашего проекта, вплоть до всех системных зависимостей. Поехали дальше!

## Dockerfile? Какой Dockerfile?

Сейчас 2021 год, и очень многие компании используют Docker для деплоя и запуска сервисов. Typeable здесь не будет исключением. В составе `nixpkgs` есть весьма удобный инструментарий для сборки контейнеров под названием `dockerTools`. Более подробно с его возможностями можно ознакомиться [по ссылке](https://nixos.org/guides/building-and-running-docker-images.html), я лишь покажу, как мы с его помощью упаковываем наш код в контейнеры. Полностью код можно посмотреть в файле `nix/docker.nix`.

Для начала нам понадобится исходный контейнер, в который мы закинем всё что нам нужно. Nix позволяет собрать контейнер полностью с нуля без каких-либо лишних компонентов, но, тем не менее, этот подход не всегда удобен. Иногда, особенно во внештатных ситуациях, приходится залезать в контейнер руками через командную строку. Поэтому здесь мы используем CentOS.

```text
sourceImage = dockerTools.pullImage {
  imageName = "centos";
  imageDigest = "sha256:e4ca2ed0202e76be184e75fb26d14bf974193579039d5573fb2348664deef76e";
  sha256 = "1j6nplfs6999qmbhjkaxwjgdij7yf31y991sna7x4cxzf77k74v3";
  finalImageTag = "7";
  finalImageName = "centos";
};
```

Здесь всё очевидно для всех, кто когда-либо работал с Docker. Мы говорим Nix, какой образ из публичного Docker Registry мы хотим использовать и что дальше мы будем на него ссылаться как на `sourceImage`.

Для сборки самого образа в dockerTools есть функция `buildImage`. У неё довольно много параметров, и часто проще написать свою обёртку над ней, что мы и сделаем:

```text
makeDockerImage = name: revision: packages: entryPoint:
  dockerTools.buildImage {
    name = name;
    tag = revision;
    fromImage = sourceImage;
    contents = (with pkgs; [ bashInteractive coreutils htop strace vim ]) ++ packages;
    config.Cmd = entryPoint;
  };
```

Наша функция `makeDockerImage` принимает четыре параметра: имя контейнера, его версия (в Typeable мы обычно используем хэш коммита из git в качестве тега), пакеты, которые мы хотим включить, и точку входа при запуске контейнера. Внутри же мы ссылаемся на образ с CentOS как основу (`fromImage`), плюс добавляем всякие утилиты, крайне полезные при экстренных случаях.

И, наконец, создадим образ с нашим великолепным приложением.

```text
hello-world = project.hello-world.components.exes.hello-world;
helloImage = makeDockerImage "hello"
  (if imageTag == null then "undefined" else imageTag)
  [ hello-world ]
  [ "${hello-world}/bin/hello-world"
  ];
```

Для начала мы создадим алиас для нужного нам пакета, чтобы не писать `project.hello-world...` повсюду. Дальше, вызвав написанную ранее функцию `makeDockerImage`, мы создаём образ контейнера с пакетом `hello-world`. В качестве тэга будет указан параметр `imageTag`, передаваемый снаружи, либо "undefined" если ничего не передано.

Проверим сборку:

```bash
$ nix build --argstr imageTag 1.0 helloImage
[4 built, 0.0 MiB DL]

 $ ls -l result
lrwxrwxrwx 1 user users 69 May 11 13:12 result -> /nix/store/56qqhiwahyi46g6mf355fjr1g6mcab0b-docker-image-hello.tar.gz
```

Через пару минут или даже быстрее мы получим символическую ссылку `result`, указывающую на наш готовый образ. Проверим, что всё получилось.

```bash
$ docker load < result
76241b8b0c76: Loading layer [==================================================>]  285.9MB/285.9MB
Loaded image: hello:1.0
$ docker run hello:1.0
Hello, World!
```

## Заключение

В итоге, с помощью сравнительно небольшого количества кода, у нас получилось сделать воспроизводимую сборку нашего проекта на Haskell. Точно так же, заменив haskell.nix на что-то другое, можно поступить с проектами на других языках: в nixpkgs есть встроенные средства для C/C++, Python, Node и других популярных языков.

В следующей статье цикла я расскажу о частых проблемах, которые возникают при работе с Nix. Stay tuned!

### Вам может быть интересно:

  1. [Nix: Что это и с чем это употреблять?](https://habr.com/ru/company/typeable/blog/550860/)
  2. [Haskell – хороший выбор с точки зрения безопасности ПО?](https://habr.com/ru/company/typeable/blog/560286/)
  3. [Антирегрессионное тестирование – минимизируйте затраты](https://habr.com/ru/company/typeable/blog/583062/)
  4. [А вы знаете, где сейчас используется Лисп?](https://habr.com/ru/company/typeable/blog/581488/)

Версия на английском языке: <https://typeable.io/blog/2021-05-18-nix-2.html>

**********

[nix](/tags/nix.md)
[nixos](/tags/nixos.md)
