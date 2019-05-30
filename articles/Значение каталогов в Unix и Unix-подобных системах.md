# Значение каталогов в Unix и Unix-подобных системах

For more data on the layout of Linux file-systems, look at the [Filesystem Hierarchy Standard](http://www.pathname.com/fhs/) (now at version 2.3, with the [beta 3.0](http://www.linuxbase.org/betaspecs/fhs/fhs.txt) version deployed on most recent distros). It does explain some of where the names came from:

*   **[/bin](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s04.html)**\-**Bin**aries.
*   **[/boot](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s05.html)**\- Files required for**boot**ing.
*   **[/dev](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s06.html)**\-**Dev**ice files.
*   **[/etc](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s07.html)**\-**_Et c_**_etera_. The name is inherited from the earliest Unixes, which is when it became the spot to put config-files.
*   **[/home](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s08.html)**\- Where**home**directories are kept.
*   **[/lib](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s09.html)**\- Where code**lib**raries are kept.
*   **[/media](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s11.html)**\- A more modern directory, but where removable**media**gets mounted.
*   **[/mnt](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s12.html)**\- Where temporary file-systems are**m**ou**nt**ed.
*   **[/opt](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s13.html)**\- Where**opt**ional add-on software is installed. This is discrete from`/usr/local/`for reasons I'll get to later.
*   **[/run](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s15.html)**\- Where**run**time variable data is kept.
*   **[/sbin](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s16.html)**\- Where**s**uper-**bin**aries are stored. These usually only work with root.
*   **[/srv](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s17.html)**\- Stands for "**s**e**rv**e". This directory is intended for static files that are served out.`/srv/http`would be for static websites,`/srv/ftp`for an FTP server.
*   **[/tmp](http://www.linuxbase.org/betaspecs/fhs/fhs/ch03s18.html)**\- Where**t**e**mp**orary files may be stored.
*   **[/usr](http://www.linuxbase.org/betaspecs/fhs/fhs/ch04.html)**\- Another directory inherited from the Unixes of old, it stands for "**U**NIX**S**ystem**R**esources". It does_not_stand for "user" (see the[Debian Wiki](https://wiki.debian.org/FilesystemHierarchyStandard)). This directory should be sharable between hosts, and can be NFS mounted to multiple hosts safely. It can be mounted read-only safely.
*   **[/var](http://www.linuxbase.org/betaspecs/fhs/fhs/ch05.html)**\- Another directory inherited from the Unixes of old, it stands for "**var**iable". This is where system data that varies may be stored. Such things as spool and cache directories may be located here. If a program needs to write to the local file-system and isn't serving that data to someone directly, it'll go here.

**/opt vs /usr/local**

The rule of thumb I've seen is best described as:

> Use`/usr/local`for things that would normally go into`/usr`, or are overriding things that are already in`/usr`. Use`/opt`for things that install all in one directory, or are otherwise special.