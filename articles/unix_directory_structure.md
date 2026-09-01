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
*   **[/run](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s15.html)** \- Где хранятся данные переменных во время выполнения. (**run**time)
*   **[/sbin](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s16.html)** \- Где хранятся супер-бинарники. Они, как правило, работают только с root. (**s**uper-**bin**aries)
*   **[/srv](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s17.html)** \- Стенды для «подачи». Этот каталог предназначен для статических файлов, которые раздаются. `/srv/http` будет для статических сайтов, `/srv/ftp` для FTP-сервера. (**s**e**rv**e)
*   **[/tmp](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s18.html)** \- Где временные файлы могут быть сохранены. (**t**e**mp**orary)
*   **[/usr](http://www.linuxbase.org/betaspecs/fhs/fhs/ch04.html)** \- Еще один каталог, унаследованный от старых Unix, он обозначает «Системные ресурсы UNIX». Это не означает «пользователь» (см. [Вики Debian](https://wiki.debian.org/FilesystemHierarchyStandard)). Этот каталог должен быть общим для хостов и может безопасно подключаться по NFS к нескольким хостам. Он может быть смонтирован только для чтения.(**U**NIX **S**ystem **R**esources)
*   **[/var](http://www.linuxbase.org/betaspecs/fhs/fhs/ch05.html)** \- Еще один каталог, унаследованный от Unixes из старых, он обозначает «переменная». Здесь могут храниться системные данные, которые различаются. Здесь можно найти такие каталоги, как спул и кеш. Если программе необходимо записать данные в локальную файловую систему, и она не передает эти данные кому-то напрямую, это будет происходить здесь. (**var**iable)

## /opt vs /usr/local

Эмпирическое правило, которое я видел, лучше всего описать так:

> Используйте `/usr/local` для вещей, которые обычно входят в `/usr`, или переопределяют вещи, которые уже находятся в `/usr`. Используйте `/opt` для вещей, которые устанавливают все в один каталог или являются специальными.

**********
[файловая система](/tags/%D1%84%D0%B0%D0%B9%D0%BB%D0%BE%D0%B2%D0%B0%D1%8F%20%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0.md)
