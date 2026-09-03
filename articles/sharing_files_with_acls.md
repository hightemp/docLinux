# Совместное использование файлов с помощью ACL

Источник: [sharing files with ACLs](https://www.cs.swarthmore.edu/newhelp/sharing_files.html)

Если вы работаете над групповым проектом и хотите делиться кодом, один из вариантов — использовать ACL. ACL расшифровывается как Access Control List (список контроля доступа). ACL позволяют сделать обычные [права доступа к файлам](https://www.cs.swarthmore.edu/newhelp/chmod.html) более специфичными.

### Настройка ACL

Для настройки ACL попробуйте наш скрипт `easyfacl`. Он запросит у вас:

  1. Разделённый пробелами список имён пользователей (включите в него и своё имя!).
  2. Каталог, права на который вы хотите изменить. Можно ввести полный путь или путь относительно текущего расположения.

Затем скрипт покажет команды, которые собирается выполнить. Вы можете подтвердить их или ввести самостоятельно. Они должны выглядеть примерно так:

```bash
setfacl -R -d -m user:uname1:rwx,user:uname2:rwx dir
setfacl -R -m user:uname1:rwx,user:uname2:rwx dir
```

  * Вы должны быть одним из перечисленных пользователей, чтобы у вас были ACL-привилегии, если кто-то из других пользователей создаст файлы и папки в этом каталоге.

  * `setfacl` — команда для изменения ACL-информации о файле или каталоге.

  * `-R` — сделать команду рекурсивной, то есть применить те же ACL ко всем существующим файлам и подкаталогам в каталоге.

  * `-d` — сделать эти ACL значениями по умолчанию. Все новые файлы и каталоги, созданные внутри, будут иметь те же ACL.

  * `-m` — изменить (modify). Это настраивает для пользователей (в нашем случае user1 и user2) права rwx на каталог.

После запуска `easyfacl` или ручной настройки ACL через `setfacl` используйте `getfacl dirname`, чтобы посмотреть ACL конкретного файла или каталога.

Вот пример всего процесса, выполненный от пользователя jk:

```bash
BASIL[jk]$ mkdir project
BASIL[jk]$ easyfacl
Enter a space separated list of users: jk dhp mary
Enter a pathname (relative or full): project

These commands will be entered
setfacl -R -d -m user:jk:rwx,user:dhp:rwx,user:mary:rwx project
setfacl -R -m user:jk:rwx,user:dhp:rwx,user:mary:rwx project
Should I do this? (Y/n)y
acls are set up
press Return>
BASIL[jk]$ getfacl project/
# file: project
# owner: jk
# group: users
user::rwx
user:jk:rwx
user:mary:rwx
user:dhp:rwx
group::r-x
mask::rwx
other::r-x
```

**********

[ACL](/tags/acl.md)
[Linux](/tags/linux.md)