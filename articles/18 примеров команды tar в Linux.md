# 18 примеров команды tar в Linux

## 1. Создание файла архива tar

В приведенном ниже примере команда создаст файл **sedicomm-14-09-12.tar** с каталога **/home/sedicomm** в текущем рабочем каталоге.

```console
$ tar -cvf sedicomm-14-09-12.tar /home/sedicomm/
/home/sedicomm/
/home/sedicomm/cleanfiles.sh
/home/sedicomm/openvpn-2.1.4.tar.gz
/home/sedicomm/phpmyadmin-2.11.11.3-1.el5.rf.noarch.rpm
/home/sedicomm/rpmforge-release-0.5.2-2.el5.rf.i386.rpm
```

Давайте обсудим каждый флаг (опцию), который мы использовали в приведенной выше команде для создания файла архива **tar**.

* **c** — Создает новый .tar файл архива.
* **v** — показать прогресс создания файла .tar.
* **f** — тип имени файла архива.

## 2. Создание файла архива tar.gz

Чтобы создать сжатый файл архива **gzip**, мы используем параметр **z**. Например, приведенная ниже команда создаст сжатый файл **MyImages-14-09-12.tar.gz** для каталога **/home/MyImages**.

**Примечание**: расширения **tar.gz** и **tgz** одинаковы.

```console
$ tar cvzf MyImages-14-09-12.tar.gz /home/MyImages
ИЛИ
$ tar cvzf MyImages-14-09-12.tgz /home/MyImages
/home/MyImages/
/home/MyImages/Sara-Khan-and-model-Priyanka-Shah.jpg
/home/MyImages/RobertKristenviolent101201.jpg
/home/MyImages/Justintimerlake101125.jpg
/home/MyImages/Mileyphoto101203.jpg
/home/MyImages/JenniferRobert101130.jpg
/home/MyImages/katrinabarbiedoll231110.jpg
/home/MyImages/the-japanese-wife-press-conference.jpg
/home/MyImages/ReesewitherspoonCIA101202.jpg
/home/MyImages/yanaguptabaresf231110.jpg
```

## 3. Создание файла архива tar.bz2

Функция **bz2** сжимает и создает файл архива меньшего размера, чем **gzip**. Сжатие **bz2** требует больше времени для сжатия и распаковки файлов по сравнению с **gzip**. Чтобы создать сжатый файл **tar**, мы используем параметр **j**. Следующая команда примера создаст файл **Phpfiles-org.tar.bz2** для каталога **/home/php**.

**Примечание**: **tar.bz2** и **tbz** аналогичны **tb2**.

```console
$ tar cvfj Phpfiles-org.tar.bz2 /home/php
ИЛИ
$ tar cvfj Phpfiles-org.tar.tbz /home/php
ИЛИ
$ tar cvfj Phpfiles-org.tar.tb2 /home/php
/home/php/
/home/php/iframe_ew.php
/home/php/videos_all.php
/home/php/rss.php
/home/php/index.php
/home/php/vendor.php
/home/php/video_title.php
/home/php/report.php
/home/php/object.html
/home/php/video.php
```

## 4. Разархивирование архива tar

Чтобы распаковать или извлечь файл **tar**, просто выполните следующую команду, используя опцию **x** (extract). Например, приведенная ниже команда распакует файл **public_html-14-09-12.tar** в текущий рабочий каталог. Если вы хотите разархивировать файлы в другой каталог, используйте опцию — **C** (specified directory).

```console
## Untar files in Current Directory ##
$ tar -xvf public_html-14-09-12.tar
## Untar files in specified Directory ##
$ tar -xvf public_html-14-09-12.tar -C /home/public_html/videos/
/home/public_html/videos/
/home/public_html/videos/views.php
/home/public_html/videos/index.php
/home/public_html/videos/logout.php
/home/public_html/videos/all_categories.php
/home/public_html/videos/feeds.xml
```

## 5. Разархивирование tar.gz

Чтобы распаковать **tar.gz** архив, просто запустите следующую команду. Если же вы хотите разархивировать в другой каталог, используйте опцию **-C** и путь к каталогу, как показано в приведенном выше примере.

```console
$ tar -xvf thumbnails-14-09-12.tar.gz
/home/public_html/videos/thumbnails/
/home/public_html/videos/thumbnails/katdeepika231110.jpg
/home/public_html/videos/thumbnails/katrinabarbiedoll231110.jpg
/home/public_html/videos/thumbnails/onceuponatime101125.jpg
/home/public_html/videos/thumbnails/playbutton.png
/home/public_html/videos/thumbnails/ReesewitherspoonCIA101202.jpg
/home/public_html/videos/thumbnails/snagItNarration.jpg
/home/public_html/videos/thumbnails/Minissha-Lamba.jpg
/home/public_html/videos/thumbnails/Lindsaydance101201.jpg
/home/public_html/videos/thumbnails/Mileyphoto101203.jpg
```

## 6. Разархивирование архива tar.bz2

Чтобы разархивировать сжатый файл **tar.bz2**, просто используйте следующую команду. Приведенная ниже команда распакует все файлы типа **.flv** из архива.

```console
$ tar -xvf videos-14-09-12.tar.bz2
/home/public_html/videos/flv/katrinabarbiedoll231110.flv
/home/public_html/videos/flv/BrookmuellerCIA101125.flv
/home/public_html/videos/flv/dollybackinbb4101125.flv
/home/public_html/videos/flv/JenniferRobert101130.flv
/home/public_html/videos/flv/JustinAwardmovie101125.flv
/home/public_html/videos/flv/Lakme-Fashion-Week.flv
/home/public_html/videos/flv/Mileyphoto101203.flv
/home/public_html/videos/flv/Minissha-Lamba.flv
```

## 7. Просмотр содержимого файла архива tar

Чтобы просмотреть содержимое файла **tar**, просто запустите команду с опцией **t** (просмотр содержимого). В приведенной ниже команде будет отображаться содержимое файла **uploadprogress.tar**.

```console
$ tar -tvf uploadprogress.tar
-rw-r--r-- chregu/staff 2276 2011-08-15 18:51:10 package2.xml
-rw-r--r-- chregu/staff 7877 2011-08-15 18:51:10 uploadprogress/examples/index.php
-rw-r--r-- chregu/staff 1685 2011-08-15 18:51:10 uploadprogress/examples/server.php
-rw-r--r-- chregu/staff 1697 2011-08-15 18:51:10 uploadprogress/examples/info.php
-rw-r--r-- chregu/staff 367 2011-08-15 18:51:10 uploadprogress/config.m4
-rw-r--r-- chregu/staff 303 2011-08-15 18:51:10 uploadprogress/config.w32
-rw-r--r-- chregu/staff 3563 2011-08-15 18:51:10 uploadprogress/php_uploadprogress.h
-rw-r--r-- chregu/staff 15433 2011-08-15 18:51:10 uploadprogress/uploadprogress.c
-rw-r--r-- chregu/staff 1433 2011-08-15 18:51:10 package.xml
``` 

## 8. Просмотр содержимого tar.gz

Используйте следующую команду для отображения содержимого файла **tar.gz**.

```console
$ tar -tvf staging.tecmint.com.tar.gz
-rw-r--r-- root/root 0 2012-08-30 04:03:57 staging.tecmint.com-access_log
-rw-r--r-- root/root 587 2012-08-29 18:35:12 staging.tecmint.com-access_log.1
-rw-r--r-- root/root 156 2012-01-21 07:17:56 staging.tecmint.com-access_log.2
-rw-r--r-- root/root 156 2011-12-21 11:30:56 staging.tecmint.com-access_log.3
-rw-r--r-- root/root 156 2011-11-20 17:28:24 staging.tecmint.com-access_log.4
-rw-r--r-- root/root 0 2012-08-30 04:03:57 staging.tecmint.com-error_log
-rw-r--r-- root/root 3981 2012-08-29 18:35:12 staging.tecmint.com-error_log.1
-rw-r--r-- root/root 211 2012-01-21 07:17:56 staging.tecmint.com-error_log.2
-rw-r--r-- root/root 211 2011-12-21 11:30:56 staging.tecmint.com-error_log.3
-rw-r--r-- root/root 211 2011-11-20 17:28:24 staging.tecmint.com-error_log.4
``` 

## 9. Просмотр содержимого tar.bz2

Чтобы просмотреть содержимое файла **tar.bz2**, выполните следующую команду.

```console
$ tar -tvf Phpfiles-org.tar.bz2
drwxr-xr-x root/root 0 2012-09-15 03:06:08 /home/php/
-rw-r--r-- root/root 1751 2012-09-15 03:06:08 /home/php/iframe_ew.php
-rw-r--r-- root/root 11220 2012-09-15 03:06:08 /home/php/videos_all.php
-rw-r--r-- root/root 2152 2012-09-15 03:06:08 /home/php/rss.php
-rw-r--r-- root/root 3021 2012-09-15 03:06:08 /home/php/index.php
-rw-r--r-- root/root 2554 2012-09-15 03:06:08 /home/php/vendor.php
-rw-r--r-- root/root 406 2012-09-15 03:06:08 /home/php/video_title.php
-rw-r--r-- root/root 4116 2012-09-15 03:06:08 /home/php/report.php
-rw-r--r-- root/root 1273 2012-09-15 03:06:08 /home/php/object.html
``` 

## 10. Разархивирование отдельного файла из tar

К примеру, чтобы извлечь один файл с именем **cleanfiles.sh** из **cleanfiles.sh.tar**, используйте следующую команду.

```console
$ tar -xvf cleanfiles.sh.tar cleanfiles.sh
ИЛИ
$ tar --extract --file=cleanfiles.sh.tar cleanfiles.sh
cleanfiles.sh
```

## 11. Разархивирование отдельного из файла tar.gz

К примеру, чтобы извлечь один файл **tecmintbackup.xml** из архива **tecmintbackup.tar.gz**, используйте команду следующим образом.

```console
$ tar -zxvf tecmintbackup.tar.gz tecmintbackup.xml
ИЛИ
$ tar --extract --file=tecmintbackup.tar.gz tecmintbackup.xml
tecmintbackup.xml
```

## 12. Разархивирование отдельного файл из файла tar.bz2

Чтобы извлечь один файл **index.php** из файла **Phpfiles-org.tar.bz2**, используйте следующий параметр.

```console
$ tar -jxvf Phpfiles-org.tar.bz2 home/php/index.php
ИЛИ
$ tar --extract --file=Phpfiles-org.tar.bz2 /home/php/index.php
/home/php/index.php
``` 

## 13. Разархивирование нескольких файлов из tar, tar.gz и tar.bz2

Чтобы извлечь несколько файлов из архива **tar**, **tar.gz** и **tar.bz2** необходимо использовать приведенную ниже команду. Эта команда извлекает из архива **«file 1»** и **«file 2»**.

```console
$ tar -xvf sedicomm-14-09-12.tar "file 1" "file 2"
$ tar -zxvf MyImages-14-09-12.tar.gz "file 1" "file 2"
$ tar -jxvf Phpfiles-org.tar.bz2 "file 1" "file 2"
``` 

## 14. Извлечение группы файлов с помощью метасимволов

Чтобы извлечь группу файлов, мы используем метасимволы. Например, чтобы извлечь группу файлов с расширением **.php** из архива **tar**, **tar.gz** и **tar.bz2** необходимо использовать следующую команду:

```console
$ tar -xvf Phpfiles-org.tar --wildcards '*.php'
$ tar -zxvf Phpfiles-org.tar.gz --wildcards '*.php'
$ tar -jxvf Phpfiles-org.tar.bz2 --wildcards '*.php'
/home/php/iframe_ew.php
/home/php/videos_all.php
/home/php/rss.php
/home/php/index.php
/home/php/vendor.php
/home/php/video_title.php
/home/php/report.php
/home/php/video.php
``` 

## 15. Добавление файла или директории в файл архива tar

Чтобы добавить файлы или каталоги в существующий файл архива **tar**, мы используем параметр **r** (присоединить). Например, мы добавляем файл **xyz.txt** и каталог **php** в существующий архив **tecmint-14-09-12.tar**.

```console
$ tar -rvf tecmint-14-09-12.tar xyz.txt
$ tar -rvf tecmint-14-09-12.tar php
drwxr-xr-x root/root 0 2012-09-15 02:24:21 home/tecmint/
-rw-r--r-- root/root 15740615 2012-09-15 02:23:42 home/tecmint/cleanfiles.sh
-rw-r--r-- root/root 863726 2012-09-15 02:23:41 home/tecmint/openvpn-2.1.4.tar.gz
-rw-r--r-- root/root 21063680 2012-09-15 02:24:21 home/tecmint/tecmint-14-09-12.tar
-rw-r--r-- root/root 4437600 2012-09-15 02:23:41 home/tecmint/phpmyadmin-2.11.11.3-1.el5.rf.noarch.rpm
-rw-r--r-- root/root 12680 2012-09-15 02:23:41 home/tecmint/rpmforge-release-0.5.2-2.el5.rf.i386.rpm
-rw-r--r-- root/root 0 2012-08-18 19:11:04 xyz.txt
drwxr-xr-x root/root 0 2012-09-15 03:06:08 php/
-rw-r--r-- root/root 1751 2012-09-15 03:06:08 php/iframe_ew.php
-rw-r--r-- root/root 11220 2012-09-15 03:06:08 php/videos_all.php
-rw-r--r-- root/root 2152 2012-09-15 03:06:08 php/rss.php
-rw-r--r-- root/root 3021 2012-09-15 03:06:08 php/index.php
-rw-r--r-- root/root 2554 2012-09-15 03:06:08 php/vendor.php
-rw-r--r-- root/root 406 2012-09-15 03:06:08 php/video_title.php
```

## 16. Добавление файлов или каталогов в tar.gz и tar.bz2.

У команды **tar** нет возможности добавлять файлы или каталоги в существующий сжатый файл **tar.gz** и **tar.bz2**. Если мы попытаемся, то получим следующую ошибку:

```console
$ tar -rvf MyImages-14-09-12.tar.gz xyz.txt
$ tar -rvf Phpfiles-org.tar.bz2 xyz.txt
tar: This does not look like a tar archive
tar: Skipping to next header
xyz.txt
tar: Error exit delayed from previous errors
``` 

## 17. Как проверить архивы tar, tar.gz и tar.bz2

Для проверки любого **tar** архива мы используем опцию **-W** (проверка). Для этого просто используйте приведенные ниже примеры команд.

**Примечание**. Вы не можете выполнить проверку в сжатом архиве (***.tar.gz**, ***.tar.bz2**).

```console
$ tar tvfW tecmint-14-09-12.tar
tar: This does not look like a tar archive
tar: Skipping to next header
tar: Archive contains obsolescent base-64 headers
tar: VERIFY FAILURE: 30740 invalid headers detected
Verify -rw-r--r-- root/root 863726 2012-09-15 02:23:41 /home/tecmint/openvpn-2.1.4.tar.gz
Verify -rw-r--r-- root/root 21063680 2012-09-15 02:24:21 /home/tecmint/tecmint-14-09-12.tar
tar: /home/tecmint/tecmint-14-09-12.tar: Warning: Cannot stat: No such file or directory
Verify -rw-r--r-- root/root 4437600 2012-09-15 02:23:41 home/tecmint/phpmyadmin-2.11.11.3-1.el5.rf.noarch.rpm
tar: /home/tecmint/phpmyadmin-2.11.11.3-1.el5.rf.noarch.rpm: Warning: Cannot stat: No such file or directory
Verify -rw-r--r-- root/root 12680 2012-09-15 02:23:41 home/tecmint/rpmforge-release-0.5.2-2.el5.rf.i386.rpm
tar: /home/tecmint/rpmforge-release-0.5.2-2.el5.rf.i386.rpm: Warning: Cannot stat: No such file or directory
Verify -rw-r--r-- root/root 0 2012-08-18 19:11:04 xyz.txt
Verify drwxr-xr-x root/root 0 2012-09-15 03:06:08 php/
``` 

## 18. Проверка размера tar, tar.gz и tar.bz2.

Чтобы проверить размер архива **tar**, **tar.gz** и **tar.bz2**, используйте следующую команду. Например, приведенная ниже команда отобразит размер архивного файла в **Kilobytes** (KB).

```console
$ tar -czf - tecmint-14-09-12.tar | wc -c
12820480
$ tar -czf - MyImages-14-09-12.tar.gz | wc -c
112640
$ tar -czf - Phpfiles-org.tar.bz2 | wc -c
20480
``` 

## Использование опций:
* **c** — создать файл архива.
* **x** — извлечение архивного файла.
* **v** — показывает ход создания архивного файла.
* **f** — имя архивного файла.
* **t** — просмотр содержимого архивного файла.
* **j** — сжимать архив через bzip2.
* **z** — сжимать архив через gzip.
* **r** — добавлять или обновлять файлы или каталоги в существующий файл архива.
* **W** — проверка архивного файла.
* **wildcards** — задание шаблона команде unix tar.