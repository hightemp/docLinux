# Как создать песочницу и опакетить программу в NixOS?

Источник: [Как создать песочницу и опакетить программу в NixOS?](https://vk.com/@openrc-kak-opaketit-programmu-v-nixos-i-kak-sozdat-pesochnicu)

Доброго времени суток. Сегодня я расскажу о том как можно опакетить программу в NixOS.

**Всех с прошедшем новым годом!
Всем желаю побольше никсов в дом.**

**Введение**

Начнём с того что, как такого понятия «пакет» в NixOS нет, есть понятие «производная». Производную имеет смысл создавать, если вам нужна песочница(например для разработки, у vscode есть расширение [nix-env-selector](/away.php?to=https%3A%2F%2Fmarketplace.visualstudio.com%2Fitems%3FitemName%3Darrterian.nix-env-selector&cc_key= "https://marketplace.visualstudio.com/items?itemName=arrterian.nix-env-selector")), ну или же если вы хотите собрать и установить программу с github/иного ресурса, где располагаются исходники нужной вам программы.

Так же нет такого понятия, как «зависимости времени выполнения», они определяются автоматически и ломать голову на этот счёт не следует, вас волнуют лишь зависимости нужные для «сборки» пакета.

**Производная для песочницы**

Пример:

```text
with import <nixpkgs> {};    # 1

stdenv.mkDerivation    # 2
{
  name = "simpleSandbox";    # 3
  buildInputs = # 4
  [
    nodejs    # 5
  ];

}
```

  1. Импортирую все пакеты из nixpkgs для того что бы работать с ними было удобно. Это можно заменить на `{stdenv, nodejs}:` , но в таком случае будет не очень удобно запускать песочницу из баша. Об этом я скажу чуть позже.

2\. Описываю производную из stdenv, о том какие атрибуты есть у неё можно посмотреть на вики или же глянуть через `nix repl` , в этой статье я опишу те которые используются чаще всего.

3\. Даю имя «simpleSandbox» нашей производной, потому что в противном случае nix-shell выдаст ошибку что у производной нет имени.

4\. Атрибут buildInputs принимает список пакетов(элементы в списке разделяются при помоще пробела), т.е. сюда мы пишем пакеты которые нам нужны в нашей песочнице.

5\. Пакет, который содержит ноду, тут всё просто.

Для того что бы зайти в песочницу достаточно выполнить `nix-shell name.nix` , если выполнить просто `nix-shell` не передавая ему в аргументы название файла, то он будет смотреть содержимое файлов default.nix и shell.nix.

![Как создать песочницу и опакетить программу в NixOS?, изображение №2](/images/82e436e24a01bd37cbe0e1f061642235.png)

Теперь о том про что я сказал в первом пункте.
shell.nix:

```text
{stdenv, nodejs}:

stdenv.mkDerivation
{
  name = "simpleSandbox";
  buildInputs =
  [
    nodejs
  ];
}
```

Для того что бы в такую песочницу зайти надо передать выражение на языке Nix в аргументы nix-shell:
` nix-shell -E 'with import <nixpkgs> {}; callPackage ./shell.nix {}'
`Удобство в данном случае теряем, но таким образом можно зайти как в первую песочницу, так и во вторую. И с помощью `callPackage` можно свою производную вызвать в конфиге, правда, смысла вызывать песочницу в конфиге нету.

И да, если в песочнице выполнить echo $buildInputs(так же и со всеми другими атрибутами) , вы получите пути к пакетам, которые вы указали в buildInputs в производной. И да, то что мы делали можно было заменить одной командой `nix-shell -p nodejs`.

**Производная для программы**

Что же касаемо их, то можно использовать пример из прошлого пункта, только немного изменив его и переименовав иначе.
default.nix:

```text
with import <nixpkgs> {};

stdenv.mkDerivation
{
  src = ./.;
  name = "simplePackage";
  buildInputs =
  [
    gcc
  ];
  buildPhase =
  ''
    mkdir $out/bin -p
    g++ $src/main.cpp
  '';
  installPhase =
  ''
    mv [a.out](/away.php?to=http%3A%2F%2Fa.out&cc_key=) $out/bin/simpleProgram
  '';
}
```

Как мы видим, я добавил src, а так же buildPhase и installPhase, в них буду выполняться команды на этапе сборки и этапе установки. В main.cpp простой хелловорлд.
Что бы собрать данный пакет достаточно выполнить nix-build default.nix , тут так же как и с nix-shell.

Для того что бы проверить работает ли наша программа или нет, надо заглянуть в ./result.

Как мы видим, всё исправно работает. И да если выполнить nix-shell default.nix, то мы попадём в песочницу, где будут все пакеты из buildInputs.

Для того что бы пакетник сам выкачал сурсы, надо в src передать результат функции fetchFromGitHub. Показывать буду на примере [qt1](/away.php?to=https%3A%2F%2Fgithub.com%2FKDE%2Fqt1&cc_key=):
qt1.nix:

```text
#{
#  stdenv
#  ,libGL
#  ,fetchFromGitHub
#  ,cmake
#  ,pkg-config
#  ,mesa
#  ,xorg
#  ,byacc
#  ,flex
#}:
with import <nixpkgs> {};

stdenv.mkDerivation
{
  name = "qt1";
  src = fetchFromGitHub
  {
    owner = "KDE";
    repo = "qt1";
    rev = "46b0d20a2823088b8942020b896a3e77376eb29a";
    sha256 = "1hk9wmbck8mww1pylg01jfw7lyzfam0f900pr09w4im927rp02q5";
  };
  hardeningDisable =
  [
    "format"
  ];
  shellHook =
  ''
    export hardeningDisable=format
  '';
  buildInputs =
  [

    cmake

    pkg-config
    mesa
    [xorg.libXext](/away.php?to=http%3A%2F%2Fxorg.libXext&cc_key=)
    xorg.libX11
    libGL
    byacc
    flex
  ];
}
```

_Без hardeningDisable и shellHook библиотека отказывалась компилироваться, извините ей за 22 года уже._

rev и sha256 можно узнать через `nix-prefetch-git [https://github.com/KDE/qt1`](/away.php?to=https%3A%2F%2Fgithub.com%2FKDE%2Fqt1&cc_key=)

![Как создать песочницу и опакетить программу в NixOS?, изображение №6](/images/ea35bc5be4b6013d010d129c5f545502.png)

Да и как вы уже заметили у этой производной нет buildPhase и installPhase.
Они и не нужны ей, потому что у cmake(у make, meson и т.д. тоже) есть автобилдер, который сам выполняет всю грязную работу за вас.

**Что касаемо qt5.mkDerivation и прочих NaMe.mkDerivation**

Если попробовать испрользовать stdenv.mkDerivation для приложухи на qt5, то вы получите мало приятного:

Не работает, да это можно пофиксить явно указав путь к плагинам qt через пермеменную, но это костыль, а можно использовать специальный qt5.mkDerivation, где всё это исправляется враппером и все qt приложения работают должным образом.

Но stdenv.mkDerivation можно подружить с qt приложухами с помощью qt5.wrapQtAppsHook в buildInputs.

151 просмотр

**********

[nix](/tags/nix.md)
[nixos](/tags/nixos.md)
