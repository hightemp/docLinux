# Linux — работа с ACL

Источник: [Linux — работа с ACL](https://internet-lab.ru/linux_acl)

![Linux](/images/8be84fa9a76ce9691d638a1ab2c4aaf3.png)

Иногда нескольким пользователям или группам нужно назначить разные права на файл или папку. Стандартной системы прав Linux здесь уже недостаточно, на помощь приходит ACL (Access Control List). Права ACL могут быть обычными: применяются к файлу или папке. А могут быть наследуемыми (ACL default): применяются только к папке. При этом все создаваемые файлы и папки в таком каталоге будут наследовать эти права.

Работать будем под пользователем root, поскольку настройка прав доступа требует привилегий.

Установка пакета ACL в Ubuntu:

```text
apt install acl
```

### ACL

Давайте рассмотрим пример, создадим тестовый файл.

```text
cd /home/zabbix
touch test.txt
ll | grep test
```

Получим:

```text
-rw-r--r-- 1 root  root     0 апр 12 19:16 test.txt
```

По указанным правам доступа "-rw-r--r--" уже видно, что на файле нет ACL, владелец (root) может читать и писать в файл, пользователи и группы могут только читать. Для просмотра ACL прав используем команду **getfacl** , которая доступна всем пользователям.

```text
getfacl /home/zabbix/test.txt

getfacl: Удаление начальных '/' из абсолютных путей
# file: home/zabbix/test.txt
# owner: root
# group: root
user::rw-
group::r--
other::r--
```

Настроек ACL у файла нет, отображаются стандартные права. Установим ACL, пусть пользователь zabbix будет иметь доступ на чтение и запись. Для установки ACL прав используем команду **setfacl** , которая доступна только пользователю **root.**

  * -m для модификации прав
  * u (user) для пользователя или g (group) для группы или o (other) для остальных
  * двоеточие, имя пользователя или группы
  * двоеточие, права
  * имя файла

Как-то так:

```text
setfacl -m u:пользователь:rwx имя_файла
setfacl -m g:группа:rw- имя_файла
setfacl -m o:r-- имя_файла
```

Установим ACL на наш файл.

```text
setfacl -m user:zabbix:rw- /home/zabbix/test.txt
# или
setfacl -m u:zabbix:rw- /home/zabbix/test.txt
```

Посмотрим что получилось.

```text
cd /home/zabbix
ll | grep test

-rw-rw-r--+  1 root   root      0 апр 12 19:16 test.txt
```

Смотрим на права "-rw-rw-r--+" и видим плюсик в конце. Это как раз и означает, что на файле есть ACL. И права группы теперь отображаются с максимальной маской -rw. Маска ACL показывает максимально возможные права файла или директории и отображается вместо обычных прав.

```text
getfacl /home/zabbix/test.txt

getfacl: Удаление начальных '/' из абсолютных путей
# file: home/zabbix/test.txt
# owner: root
# group: root
user::rw-
user:zabbix:rw-
group::r--
mask::rw-
other::r--
```

Удаление пользователя или группы из ACL осуществляется опцией **-x** :

```text
setfacl -x u:zabbix /home/zabbix/test.txt
```

Удаление ACL осуществляется опцией **-b** :

```text
setfacl -b /home/zabbix/test.txt
```

### Рекурсия

Назначать и удалять ACL можно рекурсивно опцией **-R**.

```text
setfacl -R -m u:пользователь:права файл
setfacl -R -b каталог
```

### ACL default

Разберёмся с наследованием, такие ACL можно установить только на директорию. Создадим директорию для примера.

```text
cd /home/zabbix
mkdir testdir
ll | grep testdir

drwxr-xr-x  2 root   root   4096 апр 12 19:43 testdir/
```

Применим Default ACL. Делается это с помощью опции **-d**.

```text
setfacl -d -m u:zabbix:rwx /home/zabbix/testdir/
cd /home/zabbix
ll | grep testdir

drwxr-xr-x+  2 root   root   4096 апр 12 19:43 testdir/
```

Видим плюсик в конце.

```text
getfacl /home/zabbix/testdir/

getfacl: Удаление начальных '/' из абсолютных путей
# file: home/zabbix/testdir/
# owner: root
# group: root
user::rwx
group::r-x
other::r-x
default:user::rwx
default:group::r-x
default:other::r-x
```

Появились опции **default**. Создадим в директории тестовый файл.

```text
cd /home/zabbix/testdir
touch test2.txt
ll | grep test

-rw-rw-r--+ 1 root   root      0 апр 12 19:49 test2.txt
```

Права применились к файлу. Их можно удалить, права применяются только к новым создаваемым файлам.

### Маска ACL

Маска показывает максимально возможные права файла или директории и отображается вместо обычных прав. Если у одного пользователя права r--, а у второго rw-, то маска будет rw-. Маску можно изменить.

```text
setfacl -m user:zabbix:rw- /home/zabbix/test.txt
setfacl -m m:r-- /home/zabbix/test.txt
getfacl /home/zabbix/test.txt

getfacl: Удаление начальных '/' из абсолютных путей
# file: home/zabbix/test.txt
# owner: root
# group: root
user::rw-
user:zabbix:rw-                 #effective:r--
group::r--
mask::r--
other::r--
```

Права при этом изменятся (#effective:r--).

**********

[Linux](/tags/linux.md)
