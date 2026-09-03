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

### Теги

  *   * [Linux](/linux)
  * [security](/security)

💰 [Поддержать проект](/donate)

## Похожие материалы

##  [VMware — просадка производительности Linux на 70% после патча от Retbleed ](/vmware_retbleed_linux_70)

[![Profile picture for user Олег](/images/f54663bef8b47cc442079e25aed312de.png) ](/user/6)

####  [Олег](/user/6 "Просмотр профиля пользователя.")

  * 12 сентября 2022
  * [Подробнее о VMware — просадка производительности Linux на 70% после патча от Retbleed](/vmware_retbleed_linux_70 "VMware — просадка производительности Linux на 70% после патча от Retbleed")

[![VMware vSphere 8](/images/ea24921593699c065647f00793ebfda3.png) ](/vmware_retbleed_linux_70)

Специалисты VMware опубликовали интересную статью. Если на хосте VMware ESXi на виртуальную машину Linux с ядром 5.18 накатить патч до версии 5.19, устраняющий уязвимость Retbleed, то производительность виртуальной машины просядет.

### Теги

  *   * [VMware](/vmware)
  * [Linux](/linux)
  * [security](/security)
  * [news](/news)
  * [Виртуализация](/virtual)

##  [Bitvise SSH Server для Windows ](/bitvise_ssh_server)

[![Profile picture for user Олег](/images/f54663bef8b47cc442079e25aed312de.png) ](/user/6)

####  [Олег](/user/6 "Просмотр профиля пользователя.")

  * 31 июля 2019
  * [Подробнее о Bitvise SSH Server для Windows](/bitvise_ssh_server "Bitvise SSH Server для Windows")

[![SSH](/images/c1d82c44d3d35212e69db69f26874981.png) ](/bitvise_ssh_server)

Bitvise SSH Server (WinSSHD) — SSH-сервер, разработанный специально для Windows. Позволяет на Windows машине организовать сервер Secure Shell Handling 2 (SSH2) и Secure FTP (SFTP). Отличается большим количеством настроек. Бесплатно для частного использования при выборе версии Personal Edition, но с ограничениями.

### Теги

  *   * [soft](/soft)
  * [Windows](/windows)
  * [Linux](/linux)
  * [security](/security)

##  [Linux — не пускает пользователя на сервер по SSH (pam_tally2) ](/linux_pam_tally2)

[![Profile picture for user Олег](/images/f54663bef8b47cc442079e25aed312de.png) ](/user/6)

####  [Олег](/user/6 "Просмотр профиля пользователя.")

  * 30 ноября 2025
  * [Подробнее о Linux — не пускает пользователя на сервер по SSH (pam_tally2)](/linux_pam_tally2 "Linux — не пускает пользователя на сервер по SSH \(pam_tally2\)")

Пользователя не пускает на сервер под доменной учётной записью на сервер Linux по SSH с ошибкой: Access deny.

### Теги

  *   * [Linux](/linux)
  * [security](/security)

* * *

## Популярно

### За сегодня:

  * [Бесплатно обновляем Windows 7 до Windows 10](/win7_to_win10)
  * [Драйвер USB2.0-Ser!](/usb2_0_rs232_com)
  * [Установка MAX без прав администратора](/max_not_admin)

### За все время:

  * [Windows Server 2019 — терминальный сервер без домена](/windows_server_2019_terminal_workgroup)
  * [Из чего состоит компьютер?](/computer_items)
  * [Установка принтера Xerox Phaser 3100MFP на Windows 10](/xerox_phaser_3100mfp_win10)
  * [Бесплатно обновляем Windows 7 до Windows 10](/win7_to_win10)
  * [Windows Server 2019 — установка контроллера домена](/windows_server_2019_dc)

### За последнее время:

  * [Тестовый вирус EICAR](/antivirus_test_eicar)
  * [Windows Server 2019 — терминальный сервер без домена](/windows_server_2019_terminal_workgroup)
  * [Установка vCenter 6.7](/vcenter_6_7_install)
  * [Dell PowerEdge R640 — Clear NVRAM](/dell_poweredge_r640_clear_nvram)

## Почитать

  * [![Python Notes for Professionals](/images/3b419111eda90ddc87825473c2ea95ff.png) ](/python_database_notes_for_professionals)

  * [![PowerShell Notes for Professionals](/images/da2a61bb8ab823a34ba8544476783245.png) ](/powershell_notes_for_professionals)

  * [![Bind 9](/images/ff5fc65bfe41b9b9912a451d143e3c72.png) ](/bind_9_administrator_reference_manual)

  * [![Основы системного администрирования Linux](/images/6426f60fb36a18107729a9e746a71a03.png) ](/book_linux_base)

  * [![Практическая загрузка](/images/61d1d54383320957d03f4d359c9dc1c8.png) ](/book_booting)

  * [![Использование csh и tcsh](/images/d532d1dbc6d254aaa3fa68c2dab219e7.png) ](/using_csh_tcsh)

  * [![PostgreSQL. Основы языка SQL](/images/22cf32228ebac072efbcf682e15df252.png) ](/sqlprimer)

  * [![Почтовый сервер Exim SMTP](/images/1836a1cbfc60dcf21cab63638c6722e5.png) ](/the_exim_smtp_mail_server)

  * [![Внутреннее устройство Microsoft Windows: Windows Server 2003, Windows XP и Windows 2000 \(4-е издание\)](/images/6b3e6f8fbdb7118514f587cc14deb602.png) ](/windows_internal_4)

  * [![grep — Карманный справочник](/images/d630330990d2a204096175e07c93e45f.png) ](/grep_pocket_reference)

  * [![sed & awk](/images/5386164393079860f578c4a245767294.png) ](/sed_and_awk)

  * [![Ubuntu Pocket Guide and Reference](/images/9935c2db30a58b101939fc6d4309b6cb.png) ](/ubuntu_pocket_guide_and_reference)

  * [![Introducing Windows Server 2008 R2](/images/a977e5ef7a52964b8d71d7a926b2fbe3.png) ](/introducing_windows_server_2008_r2)

  * [![Introducing Microsoft SQL Server 2008 R2](/images/d1d981e4c05246ce8f93507bc5205061.png) ](/introducing_microsoft_sql_server_2008_r2)

  * [![The SysAdmin Handbook – The Best of Simple-Talk](/images/d8e4987be666330f22be528e31e2cb06.png) ](/the_sysadmin_handbook_the_best_of_simple_talk)

  * [![Использование SQLite](/images/1361b04f845b5bb0965607b1b5af5b7d.png) ](/books_sqlite)

  * [![Own Your Space : Keep Yourself and Your Stuff Safe Online](/images/ea440d75e1ef1cf738b311450139e9e9.png) ](/own_your_space)

  * [![Introducing Microsoft SQL Server 2012](/images/a9f02904b3cb567af6eb1a7195a82372.png) ](/introducing_microsoft_sql_server_2012)

  * [![SQL Server Upgrade Technical Reference Guide](/images/8360502878a61f90209002035d84920c.png) ](/sql_server_2012_upgrade_technical_reference_guide)

  * [![Introducing Windows Server 2012 \(RTM Edition\)](/images/05b431d3a6b76894d40b14ee8fce1ed9.png) ](/introducing_windows_server_2012_rtm_edition)

**********

[Linux](/tags/linux.md)
