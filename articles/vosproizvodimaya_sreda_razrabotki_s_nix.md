# Воспроизводимая среда разработки с Nix

Источник: [Воспроизводимая среда разработки с Nix](https://archercreat.github.io/build-environment-with-nix-shell/)

Вся моя разработка происходит внутри виртуальных машин на нескольких устройствах: иногда я использую стационарный пк, иногда ноутбук, и на каждой машине приходится настраивать одинаковое окружение. Как C++ разработчик, я часто нуждаюсь в менеджере пакетов и если раньше я полагался на [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) и скрипты сборки для установки зависимостей, то в этом году решил разобраться с инструментом [Nix](https://nixos.org/), который является и пакетным менеджером, и позволяет настраивать детерминированное окружение одной командой. В этой статье я коротко расскажу что такое Nix, что он предлагает и покажу как с его помощью я создаю окружения разработки.

Вся моя разработка происходит внутри виртуальных машин на нескольких устройствах: иногда я использую стационарный пк, иногда ноутбук, и на каждой машине приходится настраивать одинаковое окружение. Как C++ разработчик, я часто нуждаюсь в менеджере пакетов и если раньше я полагался на [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) и скрипты сборки для установки зависимостей, то в этом году решил разобраться с инструментом [Nix](https://nixos.org/), который является и пакетным менеджером, и позволяет настраивать детерминированное окружение одной командой. В этой статье я коротко расскажу что такое Nix, что он предлагает и покажу как с его помощью я создаю окружения разработки.

##  Что такое Nix

Nix - это дистрибутив (NixOS) и пакетный менеджер для Linux и Mac OS. В основе Nix лежит собственный [функциональный язык программирования](https://nixos.org/manual/nix/stable/language/index.html) с одноименным названием. Nix позволяет [создавать воспроизводимое и детерминированное окружение](https://nixos.wiki/wiki/Development_environment_with_nix-shell) в декларативном стиле, что исключает необходимость вручную устанавливать и собирать отдельные пакеты. С Nix можно быть уверенным, что на любом компьютере будет одинаковое окружение разработки, а так же что никакие сторонние зависимости не привнесут свои изменения в проект.

В пакетном менеджере Nix каждый пакет создается из рецепта - [Derivation](https://nixos.org/manual/nix/stable/language/derivations.html). Рецепт описывает все, что необходимо для сборки пакета: зависимости, переменные окружения, исходные файлы, и т.п. Все установленные пакеты хранятся в директории `/nix/store` и имеют пути `/nix/store/8p4l1ih9drlfybaddajjj22x028dqn0b-z3-4.12.1`, где `8p4l1ih9drl...` \- хэш графа зависимостей. Таким образом достигается атомарность и версионность - если изменить какие-либо зависимости пакета, хэш будет другой. У Nix доступно множество команд: `nix-build`, `nix-env`, `nix-shell`, в этой статье же речь пойдет только о последней.

Команда [nix-shell](https://nixos.org/manual/nix/stable/command-ref/nix-shell.html) управляет зависимостями рецепта: их загрузкой, сборкой и настройкой окружения. `nix-shell` можно сравнить с `venv` питона, только помимо зависимостей (библиотек), она позволяет устанавливать различные программы:

```bash
$ nix-shell -p stdenv
these 4 paths will be fetched (0.03 MiB download, 0.17 MiB unpacked):
  /nix/store/45a55rzx3k794626g8adslzc6557gh0j-expand-response-params
  /nix/store/bfbp3ypd9nm3fapz634gvvs738blrl0y-gcc-wrapper-12.2.0
  /nix/store/c3f4jdwzn8fm9lp72m91ffw524bakp6v-stdenv-linux
  /nix/store/i2pdyabq6nrrnisbkma71h42fw6ha0y6-binutils-wrapper-2.40
copying path '/nix/store/45a55rzx3k794626g8adslzc6557gh0j-expand-response-params' from 'https://cache.nixos.org'...
copying path '/nix/store/i2pdyabq6nrrnisbkma71h42fw6ha0y6-binutils-wrapper-2.40' from 'https://cache.nixos.org'...
copying path '/nix/store/bfbp3ypd9nm3fapz634gvvs738blrl0y-gcc-wrapper-12.2.0' from 'https://cache.nixos.org'...
copying path '/nix/store/c3f4jdwzn8fm9lp72m91ffw524bakp6v-stdenv-linux' from 'https://cache.nixos.org'...

[nix-shell:~]$
```

Здесь создается окружение с единственным пакетом `stdenv`, в который входит `gcc` компилятор, `make` и другие базовые программы. Если запустить `nix-shell` без аргументов, конфигурация загрузится из `shell.nix`.

##  Настройка окружения

Начнем с простого. У меня есть проект, который нужно собрать с помощью `cmake` и `clang-15`. Проект так же будет зависеть от трех библиотек: [fmt](https://github.com/fmtlib/fmt), [range-v3](https://github.com/ericniebler/range-v3) и [LLVM 15](https://github.com/llvm/llvm-project/tree/release/15.x). К счастью, пакетный менеджер предлагает [более 80 тыс. различных пакетов](https://search.nixos.org/packages) и эти библиотеки точно в нем есть. Поэтому `shell.nix` файл будет выглядеть следующим образом:

```text
{ pkgs ? import <nixpkgs> {} }:
let
  stdenv = pkgs.llvmPackages_15.stdenv;
in rec {
  project = stdenv.mkDerivation {
    name = "my-project";

    nativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
    ];

    buildInputs = [
      pkgs.range-v3
      pkgs.fmt
      pkgs.llvm_15
    ];
  };
}
```

Здесь `pkgs` \- коллекция пакетов (рецептов) из `https://search.nixos.org/packages`:

```text
{ pkgs ? import <nixpkgs> {} }:
```

Стандартное окружение перезаписывается окружением из пакета [llvmPackages_15](https://search.nixos.org/packages?channel=22.11&show=llvmPackages_15.stdenv&from=0&size=50&sort=relevance&type=packages&query=llvmPackages_15). Благодаря этому сборка проекта и зависимостей будет производиться компилятором `clang-15`:

```text
stdenv = pkgs.llvmPackages_15.stdenv;
```

В этом файле есть один рецепт под названием project. В нем переменной `nativeBuildInputs` описываются `build-time` зависимости, т.е. система сборки:

```text
nativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
    ];
```

`runtime` зависимости т.е. динамические библиотеки описываются переменной `buildInputs`:

```text
buildInputs = [
      pkgs.range-v3
      pkgs.fmt
      pkgs.llvm_15
    ];
```

После запуска `nix-shell`, все скомпилированные зависимости загрузятся и будут доступны в cmake через функцию `find_package`:

```bash
cmake_minimum_required(VERSION 3.15)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(my_project)

# Packages
find_package(fmt CONFIG REQUIRED)
find_package(LLVM 15.0 CONFIG REQUIRED)
find_package(range-v3 CONFIG REQUIRED)

target_link_libraries(${PROJECT_NAME} PRIVATE
  fmt::fmt
  range-v3
  ${llvm_libs}
)
```

##  Сборка пакета из исходных файлов

Допустим требуется библиотека, которой нет у пакетного менеджера или пакет, который чем-то не устраивает, например `z3`. По какой-то непонятной причине, в пакете `z3` отсутствует `cmake` файл из-за чего `find_package` его не найдет. Чтобы решить эту проблему, необходимо написать рецепт под свою версию `z3` и собрать его из исходных файлов:

```text
z3 = stdenv.mkDerivation rec {
    version = "4.12.1";
    name = "z3-${version}";
```

```c
    src = pkgs.fetchurl {
      url = "https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.12.1.tar.gz";
      sha256 = "sha256-o3Nfq/AOE0GtzHA5SZPAX9PirhZ6Ppu0YEXjMITrZKM=";
    };
```

```text
    cmakeFlags = [
      "-DZ3_BUILD_DOCUMENTATION=OFF"
    ];

    nativeBuildInputs = [
      pkgs.cmake
    ];

    buildInputs = [
      pkgs.python39
    ];

    postPatch = "substituteInPlace z3.pc.cmake.in \
      --replace '=\$\{exec_prefix\}/' '' \
      --replace '=\$\{prefix\}/' ''";
  };
```

Сначала нужно указать откуда скачать исходные файлы. В Nix есть [огромное](https://nixos.org/manual/nixpkgs/stable/#chap-pkgs-fetchers) кол-во способов скачать исходные файлы: `fetchzip`, `fetchurl`, `fetchFromGithub`, `fetchFromGitlab`, и т.д. `fetchurl` и `fetchzip` знают как работать с архивами, поэтому после загрузки они их еще и распакуют:

```c
src = pkgs.fetchurl {
      url = "https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.12.1.tar.gz";
      sha256 = "sha256-o3Nfq/AOE0GtzHA5SZPAX9PirhZ6Ppu0YEXjMITrZKM=";
    };
```

Переменной `cmakeFlags` можно передать дополнительный список переменных в `cmake` на этапе конфигурации проекта:

```text
cmakeFlags = [
      "-DZ3_BUILD_DOCUMENTATION=OFF"
    ];
```

Иногда, при установке пакета, необходимо изменить исходные файлы. Для этого есть метод `substituteInPlace`. `substituteInPlace` в качестве аргументов берет имя файла и список строк под замену. В данном случае необходимо изменить пути в файле `z3.pc.cmake.in`, требуемый для `pkg-config` программы.

Содержимое [z3.pc.cmake.in](https://github.com/Z3Prover/z3/blob/master/z3.pc.cmake.in):

```text
prefix=@CMAKE_INSTALL_PREFIX@
exec_prefix=@CMAKE_INSTALL_PREFIX@
libdir=${exec_prefix}/@CMAKE_INSTALL_LIBDIR@
sharedlibdir=${exec_prefix}/@CMAKE_INSTALL_LIBDIR@
includedir=${prefix}/@CMAKE_INSTALL_INCLUDEDIR@
```

Дело в том, что переменные `prefix`, `exec_prefix`, `CMAKE_INSTALL_LIBDIR`, и т.д. будут содержать полные пути директорий и из-за этого `libdir`, `sharedlibdir` и `includedir` будут равны `/nix/store/хэш-z3//nix/store/хэш…`.

Хоть мы и не используем `pkg-config`, Nix все равно будет ругаться, что пути неверные, поэтому исходники необходимо подредактировать. Эта команда просто удалит префиксы из файла:

```text
postPatch = "substituteInPlace z3.pc.cmake.in \
  --replace '=\$\{exec_prefix\}/' '' \
  --replace '=\$\{prefix\}/' ''";
```

Далее включаем библиотеку `z3` в список `runtime` зависимостей и теперь она так же будет доступна через `find_package`:

```text
buildInputs = [
      pkgs.range-v3
      pkgs.fmt
      pkgs.llvm_15
      z3
    ]
```

##  Изменение уже существующего рецепта

Бывают случаи, когда нужно обновить версию пакета или url для скачивания и чтобы не писать рецепт заново, его можно перезаписать. Например в рецепте `xed` от Intel, как и в случае с `z3`, отсутстует `cmake` файл. Только сборка из исходных файлов его не добавит, поэтому необходимо добавить его руками, взяв за основу уже существующий рецепт:

```text
xed = pkgs.xed.overrideAttrs (finalAttrs: previousAttrs: {
    buildPhase = previousAttrs.buildPhase + ''
      mkdir -p $out/lib/cmake/xed/

      echo '
      set(XED_LIBRARY_DIR "''${CMAKE_CURRENT_LIST_DIR}/../../../lib")
      set(XED_LIBRARIES "''${XED_LIBRARY_DIR}/libxed''${CMAKE_STATIC_LIBRARY_SUFFIX}" "''${XED_LIBRARY_DIR}/libxed-ild''${CMAKE_STATIC_LIBRARY_SUFFIX}")
      set(XED_INCLUDE_DIRS "''${CMAKE_CURRENT_LIST_DIR}/../../../include")

      add_library(XED::Main STATIC IMPORTED)
      set_target_properties(XED::Main PROPERTIES
          IMPORTED_LOCATION "''${XED_LIBRARY_DIR}/libxed''${CMAKE_STATIC_LIBRARY_SUFFIX}"
      )

      add_library(XED::ILD STATIC IMPORTED)
      set_target_properties(XED::ILD PROPERTIES
          IMPORTED_LOCATION "''${XED_LIBRARY_DIR}/libxed-ild''${CMAKE_STATIC_LIBRARY_SUFFIX}"
      )

      add_library(XED::XED INTERFACE IMPORTED)
      set_target_properties(XED::XED PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES "''${XED_INCLUDE_DIRS}"
          INTERFACE_LINK_LIBRARIES "XED::Main;XED::ILD"
      )
      ' >> $out/lib/cmake/xed/XEDConfig.cmake
    '';
  });
```

К уже существующему `buildPhase` добавляется скрипт, который создает файл `XEDConfig.cmake` в директории `$out/lib/cmake/xed`. Стоит заметить, что чтобы экранировать `$`, необходимо перед ним добавить `''` (см. [документацию](https://nixos.org/manual/nix/stable/language/values.html#type-string)).

##  Заморозка зависимостей

Рецепт выше является воспроизводимым, но не детерминированным. Версии пакетов и пакетного менеджера меняются и через некоторое время `pkgs.fmt`, `pkgs.range-v3` и остальные зависимости будут иметь другие версии. Чтобы достичь детерминированности, необходимо заморозить версию пакетного менеджера. Для этого вместо:

```text
{ pkgs ? import <nixpkgs> {} }:
```

Нужно написать:

```c
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/06278c77b5d162e62df170fec307e83f1812d94b.tar.gz") {} }:
```

Где `06278c77b5d162e62df170fec307e83f1812d94b.tar.gz` \- определенная версия Nixpkgs.

##  Заключение

`nix-shell` \- это мощный инструмент, который значительно упрощает управление зависимостями и обеспечивает репродуцируемость среды разработки. В этой статье я рассказал что такое Nix, как с помощью `nix-shell` можно собрать воспроизводимую среду разработки и привел пример своего рецепта окружения. Кстати для локальной сборки этого блога я так же использую `nix-shell`:

```text
with import <nixpkgs> {};
let
  env = pkgs.bundlerEnv rec {
    inherit ruby;
    name     = "jekyll-env";
    gemfile  = ./Gemfile;
    lockfile = ./Gemfile.lock;
    gemset   = ./gemset.nix;
  };
in
  stdenv.mkDerivation rec {
    name = "blog";
    buildInputs = [
      bundler
      ruby
      env
    ];

    shellHook = ''
      exec ${env}/bin/jekyll serve --host 0.0.0.0 --watch
    '';
  }
```

##  Литература

  * https://nixos.org/guides/ad-hoc-developer-environments.html
  * https://devenv.sh/
  * https://zero-to-nix.com/
  * https://nix.dev/
  * https://medium.com/att-israel/how-nix-shell-saved-our-teams-sanity-a22fe6668d0e

##  Приложения

Полный рецепт окружения:

```text
{ pkgs ? import <nixpkgs> {} }:
let
  stdenv = pkgs.llvmPackages_15.stdenv;

  z3 = stdenv.mkDerivation rec {
    version = "4.12.1";
    name = "z3-${version}";
```

```c
    src = pkgs.fetchurl {
      url = "https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.12.1.tar.gz";
      sha256 = "sha256-o3Nfq/AOE0GtzHA5SZPAX9PirhZ6Ppu0YEXjMITrZKM=";
    };
```

```text
    nativeBuildInputs = [
      pkgs.cmake
    ];

    buildInputs = [
      pkgs.python39
    ];

    postPatch = "substituteInPlace z3.pc.cmake.in --replace '=\$\{exec_prefix\}/' '' --replace '=\$\{prefix\}/' ''";
  };

  triton = stdenv.mkDerivation rec {
    version = "dev-1.0";
    name = "triton-${version}";

    src = pkgs.fetchFromGitHub {
      owner = "JonathanSalwan";
      repo = "Triton";
      rev = "c344d78281ed9267d83820e06efe89baa27e12b2";
      sha256 = "sha256-NUkWUXsCIhX8el2By3zVVLZcmU09p4Vn4TcsbdEjIfU=";
    };

    cmakeFlags = [
      "-DBOOST_INTERFACE=OFF"
      "-DBUILD_EXAMPLES=OFF"
      "-DENABLE_TEST=OFF"
      "-DPYTHON_BINDINGS=OFF"
    ];

    nativeBuildInputs = [
      pkgs.cmake
    ];

    buildInputs = [
      pkgs.capstone
      z3
    ];
  };

  xed = pkgs.xed.overrideAttrs (finalAttrs: previousAttrs: {
    buildPhase = previousAttrs.buildPhase + ''
      mkdir -p $out/lib/cmake/xed/

      echo '
      set(XED_LIBRARY_DIR "''${CMAKE_CURRENT_LIST_DIR}/../../../lib")
      set(XED_LIBRARIES "''${XED_LIBRARY_DIR}/libxed''${CMAKE_STATIC_LIBRARY_SUFFIX}" "''${XED_LIBRARY_DIR}/libxed-ild''${CMAKE_STATIC_LIBRARY_SUFFIX}")
      set(XED_INCLUDE_DIRS "''${CMAKE_CURRENT_LIST_DIR}/../../../include")

      add_library(XED::Main STATIC IMPORTED)
      set_target_properties(XED::Main PROPERTIES
          IMPORTED_LOCATION "''${XED_LIBRARY_DIR}/libxed''${CMAKE_STATIC_LIBRARY_SUFFIX}"
      )

      add_library(XED::ILD STATIC IMPORTED)
      set_target_properties(XED::ILD PROPERTIES
          IMPORTED_LOCATION "''${XED_LIBRARY_DIR}/libxed-ild''${CMAKE_STATIC_LIBRARY_SUFFIX}"
      )

      add_library(XED::XED INTERFACE IMPORTED)
      set_target_properties(XED::XED PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES "''${XED_INCLUDE_DIRS}"
          INTERFACE_LINK_LIBRARIES "XED::Main;XED::ILD"
      )
      ' >> $out/lib/cmake/xed/XEDConfig.cmake
    '';
  });

in rec {
  project = stdenv.mkDerivation {
    name = "my-project";

    nativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
    ];

    buildInputs = [
      pkgs.range-v3
      pkgs.fmt
      pkgs.llvm_15
      z3
      xed
      triton
    ];
  };
}
```

`CmakeLists.txt` проекта:

```text
cmake_minimum_required(VERSION 3.15)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(my_project)

# Packages
find_package(Z3 CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)
find_package(LLVM 15.0 CONFIG REQUIRED)
find_package(triton CONFIG REQUIRED)
find_package(range-v3 CONFIG REQUIRED)
find_package(XED CONFIG REQUIRED)

llvm_map_components_to_libnames(llvm_libs
  support core irreader
  bitreader bitwriter
  passes asmprinter)
```

```c
file(GLOB_RECURSE PROJECT_SOURCES  CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")
file(GLOB_RECURSE PROJECT_INCLUDES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.hpp")
source_group(TREE ${PROJECT_SOURCE_DIR} FILES ${PROJECT_SOURCES} ${PROJECT_INCLUDES})
```

```bash
add_executable(${PROJECT_NAME} ${PROJECT_SOURCES} ${PROJECT_INCLUDES})

target_include_directories(${PROJECT_NAME} PRIVATE
  "src/"
)

target_compile_features(${PROJECT_NAME} PRIVATE
  cxx_std_20
)

target_link_libraries(${PROJECT_NAME} PRIVATE
  fmt::fmt
  range-v3
  ${llvm_libs}
  z3::libz3
  triton::triton
  XED::XED
)
```

**********

[nix](/tags/nix.md)
[nixos](/tags/nixos.md)
