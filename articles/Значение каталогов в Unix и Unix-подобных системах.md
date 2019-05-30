# Значение каталогов в Unix и Unix-подобных системах

Для получения дополнительных сведений о компоновке файловых систем Linux см. [Стандарт иерархии файловых систем](http://www.pathname.com/fhs/) (теперь версия 2.3, с [beta 3.0](http: / /www.linuxbase.org/betaspecs/fhs/fhs.txt) версия, развернутая на самых последних дистрибутивах). Это объясняет, откуда пришли имена:

*   **[/bin](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s04.html)** \- Бинарники (**Bin**aries).
*   **[/boot](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s05.html)** \- Файлы, необходимые для **boot**ing.
*   **[/dev](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s06.html)** \- Файлы устройств (**Dev**ice).
*   **[/etc](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s07.html)** \- **_Et c_**_etera_. Имя унаследовано от самых ранних Unix, то есть когда оно стало местом для размещения конфигурационных файлов.
*   **[/home](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s08.html)** \- Где хранятся **домашние** каталоги.
*   **[/lib](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s09.html)** \- Где хранятся библиотеки кода (**lib**raries).
*   **[/media](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s11.html)** \- Более современный каталог, но где монтируется съемный носитель. (**media**)
*   **[/mnt](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s12.html)** \- Где смонтированы временные файловые системы. (**m**ou**nt**ed.)
*   **[/opt](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s13.html)** \- Где установлено дополнительное программное обеспечение. Это отдельно от `/usr/local/` по причинам, о которых я расскажу позже. (**opt**ional)
*   **[/run](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s15.html)**\- Where**run**time variable data is kept.
*   **[/sbin](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s16.html)**\- Where**s**uper-**bin**aries are stored. These usually only work with root.
*   **[/srv](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s17.html)**\- Stands for "**s**e**rv**e". This directory is intended for static files that are served out.`/srv/http`would be for static websites,`/srv/ftp`for an FTP server.
*   **[/tmp](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s18.html)**\- Where**t**e**mp**orary files may be stored.
*   **[/usr](http://www.linuxbase.org/betaspecs/fhs/fhs/ch04.html)**\- Another directory inherited from the Unixes of old, it stands for "**U**NIX**S**ystem**R**esources". It does_not_stand for "user" (see the[Debian Wiki](https://wiki.debian.org/FilesystemHierarchyStandard)). This directory should be sharable between hosts, and can be NFS mounted to multiple hosts safely. It can be mounted read-only safely.
*   **[/var](http://www.linuxbase.org/betaspecs/fhs/fhs/ch05.html)**\- Another directory inherited from the Unixes of old, it stands for "**var**iable". This is where system data that varies may be stored. Such things as spool and cache directories may be located here. If a program needs to write to the local file-system and isn't serving that data to someone directly, it'll go here.

**/opt vs /usr/local**

The rule of thumb I've seen is best described as:

> Use`/usr/local`for things that would normally go into`/usr`, or are overriding things that are already in`/usr`. Use`/opt`for things that install all in one directory, or are otherwise special.