# Упрощаем администрирование с etckeeper. Настройка контроля версий конфигов в /etc

Источник: [Упрощаем администрирование с etckeeper. Настройка контроля версий конфигов в /etc — короткий практический туториал по `etckeeper` на Debian: установка с Git, первичный commit, автокоммиты после `apt`, просмотр истории через `git log`, сравнение изменений через `git log -p` и `git diff`, исключение шумных файлов через `git rm --cached` и `.gitignore`.](https://admins.su/etckeeper-tutorial/)

С самого появления систем управления версиями, многие администраторы присматриваются к ним. Крайне удобным кажется слежение за конфигурационными файлами серверов с возможностью сравнения версий, отката в любой момент. В свое время я использовал Mercurial, который натравливал на важные мне конфиги с помощью директории с симлинками. Но познакомившись с etckeeper, не променяю его на старые приемы. Etckeeper позволяет держать под наблюдением всю директорию etc, при этом не ограничиваясь какой-то конкретной VCS, так как поддерживает Git, Mercurial, Bazaar, Darks. Главным аргументом при использовании etckeeper перед простым добавлением директории /etc в VCS является возможность контроля метаданных файлов. Помимо этого, Git и Mercurial не отслеживают пустые директории, хотя в рамках etc они могут иметь значение.

Etckeeper в рамках DEB систем встраивается в pre-intall и post-install менеджера пакетов apt, что позволяет эффективно контролировать изменения содержимого etc при установке или обновлении софта. При попытке установки софта будет проводиться проверка на существование неподтвержденных изменений, после установки софта новые конфиги добавятся в список наблюдения VCS и будет произведен коммит уже с ними.

В статье приведены примеры с использованием Git, как наиболее часто применяемого. Пушить изменения мы будем на этот же сервер, хотя никто не мешает нам использовать сторонний. Главное не забывать, что пушатся в том числе и файлы, к которым необходимо ограничить доступ для посторонних (passwd, shadow), так что не забывайте защищать репозиторий от несанкционированного доступа.

Установка etckeeper производится из пакета:

```text
1
```

|

```text
sudo apt-get install etckeeper git-core
```

---|---

При установке из пакета первичная инициализация etckeeper произойдет автоматически. Если вы поставите его другими способами, инициализацию можно провести командой:

```text
1
```

|

```text
sudo etckeeper init
```

---|---

В директории /etc появится .git

Настройки etckeeper лежат в файле /etc/etckeeper/etckeeper.conf. В нашем случае мы оставим их по умолчанию.

Самое время совершить первый коммит:

```text
1
```

|

```text
etckeeper commit 'Initial commit'
```

---|---

etckeeper commit 'Initial commit'

```text
1
```

|

```text
sudo apt-get install mc
```

---|---

Проверим, что появилось в Git.

```text
1
2
```

|

```text
cd /etc
git log
```

---|---

```text
1
2
3
4
5
6
7
8
```

|

```text
commit 0e592864b520d148f81f61f715a6e2c7f4594a2f
Author: root <root@vm716.local>
Date: Sun Apr 26 22:21:10 2015 +0300
committing changes in /etc after apt run
Package changes:
+mc 3:4.8.3-10
+mc-data 3:4.8.3-10
+unzip 6.0-8+deb7u2
```

---|---

Теперь попробуем изменить конфигурационный файл и сравнить его версии.

```text
1
2
3
4
5
```

|

```text
echo "test1" > /etc/testfile
etckeeper commit "test commit 1"
echo "test2" > /etc/testfile
etckeeper commit "test commit 2"
git log -p /etc/testfile
```

---|---

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
```

|

```text
commit 5f7e7db6ba070f8244efb4e25be27ed96201c663
Author: root <root@vm95716.local>
Date: Sun Apr 26 22:28:22 2015 +0300
test commit 2
diff --git a/testfile b/testfile
index a5bce3f..180cf83 100644
--- a/testfile
+++ b/testfile
@@ -1 +1 @@
-test1
+test2
commit 416c9dc355c45c359c05a9e1e3aee865b968a41e
Author: root <root@vm716.local>
Date: Sun Apr 26 22:28:15 2015 +0300
test commit 1
diff --git a/testfile b/testfile
new file mode 100644
index 0000000..a5bce3f
```

---|---

Теперь сравним текущую версию файла с определенным коммитом:

```text
1
```

|

```text
echo "test3" >testfile
```

---|---

Из списка коммитов (git log) выберем нужный и выполним:

```text
1
```

|

```text
git diff e91a38271edc9497346ae2455b201fe2a7e6b175 #имя коммита
```

---|---

```text
1
2
3
4
5
6
7
```

|

```text
diff --git a/testfile b/testfile
index 180cf83..df6b0d2 100644
--- a/testfile
+++ b/testfile
@@ -1 +1 @@
-test2
+test3
```

---|---

В процессе эксплуатации полезно исключить из контроля файлы, редактируемые демонами. Предположим файл testfile — как раз такой:

```text
1
2
3
```

|

```text
git rm --cached testfile
echo testfile >> .gitignore
git commit -a -m "don't track testfile"
```

---|---

Безусловно у любой VCS гораздо больше возможностей, чем описано в статье. Важно то, что лучше начать контроль версий уже сейчас, даже если вы никогда не использовали VCS, ведь потом это может сэкономить ваши время и силы.

[Linux](https://admins.su/tags/linux/)  [Debian](https://admins.su/tags/debian/)  [Tutorial](https://admins.su/tags/tutorial/)

* * *

  * [__](//twitter.com/share?url=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f&text=%d0%a3%d0%bf%d1%80%d0%be%d1%89%d0%b0%d0%b5%d0%bc%20%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b8%d1%80%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5%20%d1%81%20etckeeper.%20%d0%9d%d0%b0%d1%81%d1%82%d1%80%d0%be%d0%b9%d0%ba%d0%b0%20%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8f%20%d0%b2%d0%b5%d1%80%d1%81%d0%b8%d0%b9%20%d0%ba%d0%be%d0%bd%d1%84%d0%b8%d0%b3%d0%be%d0%b2%20%d0%b2%20%2fetc.&via= "Share on Twitter")
  * [__](//www.facebook.com/sharer/sharer.php?u=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f "Share on Facebook")
  * [__](//reddit.com/submit?url=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f&title=%d0%a3%d0%bf%d1%80%d0%be%d1%89%d0%b0%d0%b5%d0%bc%20%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b8%d1%80%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5%20%d1%81%20etckeeper.%20%d0%9d%d0%b0%d1%81%d1%82%d1%80%d0%be%d0%b9%d0%ba%d0%b0%20%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8f%20%d0%b2%d0%b5%d1%80%d1%81%d0%b8%d0%b9%20%d0%ba%d0%be%d0%bd%d1%84%d0%b8%d0%b3%d0%be%d0%b2%20%d0%b2%20%2fetc. "Share on Reddit")
  * [__](//www.linkedin.com/shareArticle?url=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f&title=%d0%a3%d0%bf%d1%80%d0%be%d1%89%d0%b0%d0%b5%d0%bc%20%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b8%d1%80%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5%20%d1%81%20etckeeper.%20%d0%9d%d0%b0%d1%81%d1%82%d1%80%d0%be%d0%b9%d0%ba%d0%b0%20%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8f%20%d0%b2%d0%b5%d1%80%d1%81%d0%b8%d0%b9%20%d0%ba%d0%be%d0%bd%d1%84%d0%b8%d0%b3%d0%be%d0%b2%20%d0%b2%20%2fetc. "Share on LinkedIn")
  * [__](//www.stumbleupon.com/submit?url=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f&title=%d0%a3%d0%bf%d1%80%d0%be%d1%89%d0%b0%d0%b5%d0%bc%20%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b8%d1%80%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5%20%d1%81%20etckeeper.%20%d0%9d%d0%b0%d1%81%d1%82%d1%80%d0%be%d0%b9%d0%ba%d0%b0%20%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8f%20%d0%b2%d0%b5%d1%80%d1%81%d0%b8%d0%b9%20%d0%ba%d0%be%d0%bd%d1%84%d0%b8%d0%b3%d0%be%d0%b2%20%d0%b2%20%2fetc. "Share on StumbleUpon")
  * [__](//www.pinterest.com/pin/create/button/?url=https%3a%2f%2fadmins.su%2fetckeeper-tutorial%2f&description=%d0%a3%d0%bf%d1%80%d0%be%d1%89%d0%b0%d0%b5%d0%bc%20%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b8%d1%80%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5%20%d1%81%20etckeeper.%20%d0%9d%d0%b0%d1%81%d1%82%d1%80%d0%be%d0%b9%d0%ba%d0%b0%20%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8f%20%d0%b2%d0%b5%d1%80%d1%81%d0%b8%d0%b9%20%d0%ba%d0%be%d0%bd%d1%84%d0%b8%d0%b3%d0%be%d0%b2%20%d0%b2%20%2fetc. "Share on Pinterest")

#### Смотрите также

  * [Как добавить постоянные статические маршруты (persistent static routes) в Mac OS X.](/kak-dobavit-postoyannye-staticheskie-marshruty-persistent-static-routes-v-mac-os-x/)
  * [Знакомство с CMake. Часть 3. CMakeCache, модули CMake, зависимости сборки.](/znakomstvo-s-cmake-chast-3-cmakecache-moduli-cmake-zavisimosti-sborki/)
  * [maybe? Интересная песочница для отладки операций с файлами в скриптах Linux.](/maybe-interesnaya-pesochnica-dlya-otladki-operacij-s-fajlami-v-skriptax-linux/)
  * [Знакомство с CMake. Часть 2. Переменные, условия, сообщения, опции.](/znakomstvo-s-cmake-chast-2/)
  * [Знакомство с CMake. Часть 1. Установка, CMakeLists.txt, сборка.](/znakomstvo-s-cmake-2/)

**********

[аудит](/tags/audit.md)
[etckeeper](/tags/etckeeper.md)
