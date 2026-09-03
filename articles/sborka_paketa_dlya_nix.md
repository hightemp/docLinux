# Сборка пакета для Nix

Источник: [Сборка пакета для Nix](https://uralbash.ru/articles/2017/nixpkgs-contribute/)

[Nix](https://nixos.org/nixpkgs/) \- замечательный пакетный менеджер, который работает на MacOS и любом дистрибутиве Linux, причем из-за своей функциональной чистоты и изоляции зависимостей, гарантировано выдает всегда одинаковый результат.

На сегодняшний день Nix имеет огромную базу пакетов, которая ежедневно пополняется. Для сборки своего пакета потребуется знание языка [Nix expression](https://nixos.org/nix/manual/#chap-writing-nix-expressions). Это чистый функциональный язык созданный специально для пакетного менеджера Nix и операционной системы [NixOS](https://nixos.org/).

Примечание

  * Ресурсы по [NixOS](../../../pages/nixos/#nixos)
  * Статьи <http://uralbash.ru/blog/tag/nix/>

Для примера создадим сборку пакета языка программирования [Red](http://www.red-lang.org/). Будем следовать оф. документации <https://nixos.org/nixpkgs/manual/#chap-quick-start>.

## 1\. Скачиваем исходники¶

```bash
$ git clone git://github.com/NixOS/nixpkgs.git
$ cd nixpkgs
```

## 2\. Добавляем директорию с новым пакетом¶

См.также

Правила именования файлов <https://nixos.org/nixpkgs/manual/#sec-organisation>

```bash
$ mkdir pkgs/development/interpreters/red/
```

## 3\. Создаем файл описания пакета `default.nix`¶

Заготовка для нашего пакета будет выглядеть так:

```text
 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
```

|

```text
{ stdenv, fetchFromGitHub }:

stdenv.mkDerivation rec {
  src = fetchFromGitHub {
    rev = "6a43c767fa2e85d668b83f749158a18e62c30f70";
    owner = "red";
    repo = "red";
    sha256 = "1zh6xc728bs7r4v5jz1jjrdk0xd838xsxmvy9gfg75a3zffm0slr";
  };

  configurePhase = ''
  '';

  buildPhase = ''
  '';

  installPhase = ''
  '';
```

```c
  meta = with stdenv.lib; {
    description = ''
      New programming language strongly inspired by Rebol, but with a
      broader field of usage thanks to its native-code compiler, from system
      programming to high-level scripting, while providing modern support for
      concurrency and multi-core CPUs
    '';
    maintainers = with maintainers; [ uralbash ];
    platforms = [ "i686-linux" "x86_64-linux" ];
    license = licenses.bsd3;
    homepage = http://www.red-lang.org/;
  };
}
```

---|---

В первой строке указан импорт необходимых нам функций.

```text
{ stdenv, fetchFromGitHub }:
```

Далее забираем исходники с GitHub при помощи функции `fetchFromGitHub`.

```text
src = fetchFromGitHub {
  rev = "6a43c767fa2e85d668b83f749158a18e62c30f70";
  owner = "red";
  repo = "red";
  sha256 = "1zh6xc728bs7r4v5jz1jjrdk0xd838xsxmvy9gfg75a3zffm0slr";
};
```

Что бы посчитать хэш (sha256) нам потребуется утилита `nix-prefetch-git`.

```bash
$ nix-prefetch-git https://github.com/red/red 6a43c767fa2e85d668b83f749158a18e62c30f70
Initialized empty Git repository in /tmp/git-checkout-tmp-Jzca0REG/red-6a43c76/.git/
fatal: Invalid refspec '+refs/tags/v0.6.3^{}'
remote: Counting objects: 52473, done.
remote: Total 52473 (delta 0), reused 0 (delta 0), pack-reused 52473
Receiving objects: 100% (52473/52473), 20.39 MiB | 1.50 MiB/s, done.
Resolving deltas: 100% (35793/35793), done.
From https://github.com/red/red
Switched to a new branch 'fetchgit'
removing `.git'...
```

```c
git revision is 6a43c767fa2e85d668b83f749158a18e62c30f70
path is /nix/store/qp10dy2plvskbv0zjpcg9mmrsszd1a6i-red-6a43c76
git human-readable version is v0.6.3
Commit date is 2017-07-17 21:25:27 +0800
hash is 1zh6xc728bs7r4v5jz1jjrdk0xd838xsxmvy9gfg75a3zffm0slr
{
  "url": "https://github.com/red/red",
  "rev": "6a43c767fa2e85d668b83f749158a18e62c30f70",
  "date": "2017-07-17T21:25:27+08:00",
  "sha256": "1zh6xc728bs7r4v5jz1jjrdk0xd838xsxmvy9gfg75a3zffm0slr",
  "fetchSubmodules": true
}
```

В конце файла указывается мета информация:

```c
meta = with stdenv.lib; {
  description = ''
    New programming language strongly inspired by Rebol, but with a
    broader field of usage thanks to its native-code compiler, from system
    programming to high-level scripting, while providing modern support for
    concurrency and multi-core CPUs
  '';
  maintainers = with maintainers; [ uralbash ];
  platforms = [ "i686-linux" "x86_64-linux" ];
  license = licenses.bsd3;
  homepage = http://www.red-lang.org/;
};
```

Сама сборка происходит в 3 директивах `configurePhase`, `buildPhase`, `installPhase`. Если их не указывать, то по умолчанию будут выполняться `./configure`, `make`, `make install` соответственно. Т.к. `Red` не использует `autotools` для сборки, то нам придется вручную прописать все необходимые шаги. Что бы не изобретать велосипед возьмем за основу пакет из `Arch Linux` <https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=red>.

`Red` требует 32х битный `curl`, добавим его в окружение сборки:

```text
{ stdenv, stdenv_32bit, pkgsi686Linux, fetchFromGitHub, fetchurl }:

...

buildInputs = [ pkgsi686Linux.curl stdenv_32bit ];
```

Скачаем [Rebol](http://www.rebol.com/). При помощи него собирается интерпретатор `Red`.

```text
...
```

```c
rebol = fetchurl {
  url = "http://www.rebol.com/downloads/v278/rebol-core-278-4-2.tar.gz";
  sha256 = "1c1v0pyhf3d8z98qc93a5zmx0bbl0qq5lr8mbkdgygqsq2bv2xbz";
};
```

```text
r2 = "./rebol/releases/rebol-core/rebol";

...
```

В нашем случае, что добавлять в фазы установки имеет очень условных характер. Поделим следующим образом - в фазу конфигурации добавим распаковку `Rebol`:

```bash
configurePhase = ''
  # Download rebol
  mkdir rebol/
  tar -xzvf ${rebol} -C rebol/
  patchelf --set-interpreter \
      ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2 \
      ${r2}
'';
```

Заметьте `r2` это переменная, которую мы объявили выше. А [PatchELF](https://nixos.org/patchelf.html) это мега крутая утилита, которой можно подменять динамические зависимости в бинарниках, не пересобирая их. Мы изменили путь до `ld-linux.so.2` файла, т.к. в `NixOS` он имеет нестандартный путь.

Примечание

При этом если такой пакет собирать в Ubuntu то патчить rebol нет необходимости, он подхватит зависимость из стандартного пути. Но для большей универсальности это необходимо.

После условной конфигурации приступим к сборке интерпретатора `Red`. Все шаги выполняются относительно директории с исходными кодами с GitHub:

```bash
buildPhase = ''
  # Do tests
  #${r2} -qw run-all.r

  # Build test
  ${r2} -qw red.r tests/hello.red

  # Compiling the Red console...
  ${r2} -qw red.r -r environment/console/console.red

  # Generating docs...
  cd docs
  ../${r2} -qw makedoc2.r red-system-specs.txt
  ../${r2} -qw makedoc2.r red-system-quick-test.txt
  cd ../
'';
```

Установка:

```bash
installPhase = ''
  mkdir $out

  # Install
  install -d $out/opt/red
  find quick-test -type f -executable -print0 | xargs -0 rm
  cp -R * $out/opt/red/
  rm -rf $out/opt/red/rebol
  install -Dm755 console $out/bin/red
  install -Dm644 BSD-3-License.txt                          \
      $out/share/licenses/${name}/BSD-3-License.txt
  install -Dm644 BSL-License.txt                            \
      $out/share/licenses/${name}/BSL-License.txt
  install -Dm644 docs/red-system-quick-test.html            \
      $out/share/doc/${name}/red-system-quick-test.html
  install -Dm644 docs/red-system-specs.html                 \
      $out/share/doc/${name}/red-system-specs.html

  # PathElf
  patchelf --set-interpreter                            \
      ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2  \
      $out/opt/red/console
  patchelf --set-rpath ${pkgsi686Linux.curl.out}/lib \
      $out/opt/red/console
  patchelf --set-interpreter                            \
      ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2  \
      $out/bin/red
  patchelf --set-rpath ${pkgsi686Linux.curl.out}/lib \
      $out/bin/red

'';
```

## 4\. Добавление в общий список пакетов¶

Почти все готово, осталось добавить новый пакет в общий список и собрать.

```bash
$ vim pkgs/top-level/all-packages.nix

...

rascal = callPackage ../development/interpreters/rascal { };

red = callPackage ../development/interpreters/red { };

regina = callPackage ../development/interpreters/regina { };

...
```

## 5\. Сборка¶

Сборка пакета выполняется командой `nix-build`:

```bash
$ nix-build -A red
```

Или если необходимо его сразу установить в окружение:

```bash
$ nix-build -f . -iA red
```

Полный исходник выглядит так:

default.nix¶

```text
{ stdenv, stdenv_32bit, pkgsi686Linux, fetchFromGitHub, fetchurl }:

stdenv.mkDerivation rec {
  name = "red-v${version}";
  version = "0.6.3";
  src = fetchFromGitHub {
    rev = "6a43c767fa2e85d668b83f749158a18e62c30f70";
    owner = "red";
    repo = "red";
    sha256 = "1zh6xc728bs7r4v5jz1jjrdk0xd838xsxmvy9gfg75a3zffm0slr";
  };
```

```c
  rebol = fetchurl {
    url = "http://www.rebol.com/downloads/v278/rebol-core-278-4-2.tar.gz";
    sha256 = "1c1v0pyhf3d8z98qc93a5zmx0bbl0qq5lr8mbkdgygqsq2bv2xbz";
  };
```

```bash
  buildInputs = [ pkgsi686Linux.curl stdenv_32bit ];

  r2 = "./rebol/releases/rebol-core/rebol";

  configurePhase = ''
    # Download rebol
    mkdir rebol/
    tar -xzvf ${rebol} -C rebol/
    patchelf --set-interpreter \
        ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2 \
        ${r2}
  '';

  buildPhase = ''
    # Do tests
    #${r2} -qw run-all.r

    # Build test
    ${r2} -qw red.r tests/hello.red

    # Compiling the Red console...
    ${r2} -qw red.r -r environment/console/console.red

    # Generating docs...
    cd docs
    ../${r2} -qw makedoc2.r red-system-specs.txt
    ../${r2} -qw makedoc2.r red-system-quick-test.txt
    cd ../
  '';

  installPhase = ''
    mkdir $out

    # Install
    install -d $out/opt/red
    find quick-test -type f -executable -print0 | xargs -0 rm
    cp -R * $out/opt/red/
    rm -rf $out/opt/red/rebol
    install -Dm755 console $out/bin/red
    install -Dm644 BSD-3-License.txt                          \
        $out/share/licenses/${name}/BSD-3-License.txt
    install -Dm644 BSL-License.txt                            \
        $out/share/licenses/${name}/BSL-License.txt
    install -Dm644 docs/red-system-quick-test.html            \
        $out/share/doc/${name}/red-system-quick-test.html
    install -Dm644 docs/red-system-specs.html                 \
        $out/share/doc/${name}/red-system-specs.html

    # PathElf
    patchelf --set-interpreter                            \
        ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2  \
        $out/opt/red/console
    patchelf --set-rpath ${pkgsi686Linux.curl.out}/lib \
        $out/opt/red/console
    patchelf --set-interpreter                            \
        ${stdenv_32bit.cc.libc.out}/lib/32/ld-linux.so.2  \
        $out/bin/red
    patchelf --set-rpath ${pkgsi686Linux.curl.out}/lib \
        $out/bin/red

  '';
```

```c
  meta = with stdenv.lib; {
    description = ''
      New programming language strongly inspired by Rebol, but with a
      broader field of usage thanks to its native-code compiler, from system
      programming to high-level scripting, while providing modern support for
      concurrency and multi-core CPUs
    '';
    maintainers = with maintainers; [ uralbash ];
    platforms = [ "i686-linux" "x86_64-linux" ];
    license = licenses.bsd3;
    homepage = http://www.red-lang.org/;
  };
}
```

Готовый пакет можно отправить в основную ветку `nixpkgs`. Перед этим лучше почитать как правильно делать `pull request`:

  * <https://nixos.org/nixpkgs/manual/#idm140737317358720>
  * <https://nixos.org/nixpkgs/manual/#sec-reviewing-contributions>

В следующей статье я постараюсь описать как собирать свой собственный `NixOS` дистрибутив с шахматами и балеринами.

[ __C++: Приведение Enum структур к общему виду в шаблонах](../cpp-enum/)   [ C# .Net Core для Linux __](../netcore/)

## Comments

Please enable JavaScript to view the [comments powered by Disqus.](http://disqus.com/?ref_noscript) [comments powered by Disqus](http://disqus.com)

**********

[nix](/tags/nix.md)
[nixos](/tags/nixos.md)
