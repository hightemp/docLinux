# Изолированные окружения для разработки с помощью Nix

Источник: [Isolated Development Environment using Nix](https://ariya.io/2016/06/isolated-development-environment-using-nix)

12 июня 2016

В более ранней [записи в блоге](/2016/05/nix-as-os-x-package-manager.html) я упоминал использование Nix в качестве пакетного менеджера на OS X. В этом продолжении вы увидите мощь Nix в создании изолированных окружений для разработки.

Предположим, я только что установил Nix, и у меня ещё не установлено никаких других пакетов:

```bash
$ nix-env -qs
IP-  nix-1.11.2
IPS  nss-cacert-3.21
```

Мне нужно поработать над проектом с названием _Finch_. Это стабильный проект, он работает в продакшене и опирается на набор солидных и проверенных окружений: [Go 1.4](https://golang.org/doc/go1.4), [PUC-Lua 5.3](http://www.lua.org/) и [Python 2.7](https://www.python.org/).

С другой стороны, у меня есть ещё один не связанный проект — _Grove_. С этим проектом я всё ещё экспериментирую, и поэтому хочу использовать самые свежие передовые технологии. Его стек основан на новейших Python 3.5 и Go 1.6. По другим причинам мне также понадобился более быстрый Lua, и потому я выбираю [LuaJIT](http://luajit.org/). В качестве системы контроля версий вместо Git выбран [Fossil](http://www.fossil-scm.org/).

Для первого проекта имеется файл `~/projects/finch/default.nix` со следующим содержимым:

```text
with import <nixpkgs> {};
stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = [
    python
    python27Packages.virtualenv
    python27Packages.pip
    go_1_4
    lua5_3
  ];
}
```

Не углубляясь в выражения Nix (подробности смотрите в [руководстве](https://nixos.org/nixpkgs/manual/)), скажем: приведённый выше файл говорит Nix собрать новое окружение с заданным списком пакетов, указанных через путь атрибута пакета и перечисленных как `buildInputs`. Как мне узнать путь атрибута для, скажем, Go 1.4? Один способ — вывести список всех доступных пакетов:

```bash
$ nix-env -qaP | grep 'go-1.4'
nixpkgs.go_1_4             go-1.4.3
```

В примере выше `go_1_4` (или полный путь `nixpkgs.go_1_4`) — это путь атрибута для нашего любимого пакета `go-1.4.3`.

Когда этот Nix-файл готов, каждый раз, когда я хочу поработать над **Finch**, всё, что мне нужно сделать, это:

```bash
$ cd ~/projects/finch/
$ nix-shell
[nix-shell:~/projects/finch]$
```

Это запустит новую оболочку со всеми пакетами, указанными в `default.nix`. То есть я получу именно указанные версии Python, Go и Lua. Если это делается впервые, Nix должен установить или собрать эти пакеты, но последующие вызовы `nix-shell` будут очень быстрыми, поскольку используется то, что есть в кэше.

Чтобы убедиться, что всё работает:

```text
[nix-shell:~/projects/finch]$ python --version
Python 2.7.11
[nix-shell:~/projects/finch]$ pip --version
pip 8.1.2 from /nix/store/3cag9i2pa52qjxq5yvjap6m7jvp6idqm-python2.7-pip-8.1.2/lib/python2.7/site-packages (python 2.7)
[nix-shell:~/projects/finch]$ go version
go version go1.4.3 darwin/amd64
[nix-shell:~/projects/finch]$ lua -v
Lua 5.3.0  Copyright (C) 1994-2015 Lua.org, PUC-Rio
```

Это полностью _герметичное_ окружение для разработки для работы над проектом Finch. Я могу использовать Python, включая `virtualenv` и `pip`, как и ожидалось:

```text
[nix-shell:~/projects/finch]$ virtualenv env
New python executable in env/bin/python2.7
Also creating executable in env/bin/python
Installing setuptools, pip, wheel...done.
[nix-shell:~/projects/finch]$ source env/bin/activate
(env)
[nix-shell:~/projects/finch]$ pip install simplejson
Collecting simplejson
Installing collected packages: simplejson
Successfully installed simplejson-3.8.2
(env)
[nix-shell:~/projects/finch]$ pip list
pip (8.1.2)
setuptools (19.4)
simplejson (3.8.2)
virtualenv (13.1.2)
wheel (0.24.0)
(env)
```

Если я выйду из оболочки, я вернусь в окружение по умолчанию, в котором может не быть вообще никаких из указанных пакетов.

```text
[nix-shell:~/projects/finch]$ exit
ariya:~/projects/finch $ go version
-bash: go: command not found
ariya:~/projects/finch $ pip --version
-bash: pip: command not found
```

Теперь я переключаюсь обратно на **Grove**. Его `default.nix` выглядит немного иначе:

```text
with import <nixpkgs> {};
stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = [
    python35
    python35Packages.virtualenv
    python35Packages.pip
    luajit
    fossil
  ];
}
```

Мой первый шаг перед работой над Grove:

```bash
$ cd ~/projects/grove/
$ nix-shell
[nix-shell:~/projects/grove]$
```

И легко увидеть, что я получаю в этом окружении:

```text
nix-shell:~/projects/grove]$ fossil version
This is fossil version 1.33 [9c65b5432e] 2015-05-23 11:11:31 UTC
[nix-shell:~/projects/grove]$ lua -v
LuaJIT 2.1.0-beta1 -- Copyright (C) 2005-2015 Mike Pall. http://luajit.org/
[nix-shell:~/projects/grove]$ virtualenv env
New python executable in env/bin/python3.5m
Also creating executable in env/bin/python
Installing setuptools, pip, wheel...done.
[nix-shell:~/projects/grove]$ source env/bin/activate
(env)
[nix-shell:~/projects/grove]$ pip list
pip (7.1.2)
setuptools (19.4)
virtualenv (13.1.2)
wheel (0.24.0)
(env)
```

Как видите, я поддерживаю своё глобальное окружение настолько чистым, насколько это возможно, и в то же время у меня есть гибкое рабочее окружение для двух (или более) разных проектов. Необходимые зависимые пакеты одного проекта не будут вмешиваться в другие проекты или загрязнять их, даже если это один и тот же пакет с разными версиями (Python 2.7 против Python 3.5, Go 1.4 против Go 1.6, PUC-Lua 5.3 против Lua-JIT 2.1).

Приятной работы!

**********

[nix](/tags/nix.md)
[linux](/tags/linux.md)