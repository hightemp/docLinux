# Замена setuid-бита на capabilities для системных программ в Linux

Источник: [Замена setuid-бита на capabilities для системных программ в Linux](https://www.opennet.ru/tips/2469_capabilities_suid_security_limit.shtml)

С целью избавления системы от программ с suid-битом, можно использовать следующую инструкцию.
Для привязки capabilities к исполняемому файлу используется утилита setcap из пакета libcap2-bin:

```bash
sudo apt-get install libcap2-bin

```
Для формирования списка setuid-root и setgid-root программ можно использовать следующие команды:

```bash
find /bin /sbin /lib /usr/bin /usr/sbin /usr/lib -perm /4000 -user root
find /bin /sbin /lib /usr/bin /usr/sbin /usr/lib -perm /2000 -group root

```
Команды для замены setuid/setgid для базовых пакетов:

coreutils

```bash
chmod u-s /bin/su
setсap cap_setgid,cap_setuid+ep /bin/su

```
dcron

```bash
chmod u-s /usr/bin/crontab
setcap cap_dac_override,cap_setgid+ep /usr/bin/crontab

```
inetutils

```bash
chmod u-s /usr/bin/rsh
setcap cap_net_bind_service+ep /usr/bin/rsh

chmod u-s /usr/bin/rcp
setcap cap_net_bind_service+ep /usr/bin/rcp

chmod u-s /usr/bin/rlogin
setcap cap_net_bind_service+ep /usr/bin/rlogin

```
iputils

```bash
chmod u-s /bin/ping
setcap cap_net_raw+ep /bin/ping

chmod u-s /bin/ping6
setcap cap_net_raw+ep /bin/ping6

chmod u-s /bin/traceroute
setcap cap_net_raw+ep /bin/traceroute

chmod u-s /bin/traceroute6
setcap cap_net_raw+ep /bin/traceroute6

```
pam

```bash
chmod u-s /sbin/unix_chkpwd
setcap cap_dac_read_search+ep /sbin/unix_chkpwd

```
shadow

```bash
chmod u-s /usr/bin/chage
setcap cap_dac_read_search+ep /usr/bin/chage

chmod u-s /usr/bin/chfn
setcap cap_chown,cap_setuid+ep /usr/bin/chfn

chmod u-s /usr/bin/chsh
setcap cap_chown,cap_setuid+ep /usr/bin/chsh

chmod u-s /usr/bin/expiry
setcap cap_dac_override,cap_setgid+ep /usr/bin/expiry

chmod u-s /usr/bin/gpasswd
setcap cap_chown,cap_dac_override,cap_setuid+ep /usr/bin/gpasswd

chmod u-s /usr/bin/newgrp
setcap cap_dac_override,cap_setgid+ep /usr/bin/newgrp

chmod u-s /usr/bin/passwd
setcap cap_chown,cap_dac_override,cap_fowner+ep /usr/bin/passwd

```
xorg-xserver

```bash
chmod u-s /usr/bin/Xorg
setcap cap_chown,cap_dac_override,cap_sys_rawio,cap_sys_admin+ep /usr/bin/Xorg

```
screen - обязательно требует setuid для выполнения определенных проверок

util-linux-ng - не рекомендуется использовать данный пакет с capabilities, так
как в реализации команд mount и umount присутствуют определенные проверки,
которые действуют только с setuid и пропускаются с  capabilities, что дает
возможность пользователям монтировать файловые системы к которым они не имеют доступа.
Подробнее об опасностях, которые сулит перевод программы с setuid на
capabilities без проведения аудита кода, можно прочитать [здесь](https://www.opennet.ru/openforum/vsluhforumID3/71880.html#13).

Лицензия оригинала: CC-BY.

**********

[capabilities](/tags/capabilities.md)
[Linux](/tags/linux.md)
