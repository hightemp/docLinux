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

04.11.2010 , Источник: [https://wiki.archlinux.org/index.ph...](https://wiki.archlinux.org/index.php/Using_File_Capabilities_Instead_Of_Setuid) Ключи: [capabilities](/keywords/capabilities.html), [suid](/keywords/suid.html), [security](/keywords/security.html), [limit](/keywords/limit.html) / Лицензия: CC-BY
Раздел:    **[[Корень](/tips/sml/index.shtml) / [Безопасность](/tips/sml/5.shtml)](/tips/sml/5.shtml) / [Шифрование, PGP](/tips/sml/18.shtml)**

**Обсуждение** | [ [RSS](/cgi-bin/openforum/rss_forum.cgi?forum=vsluhforumID3&om=72094) ]
---|---
|
* [1](/openforum/vsluhforumID3/72094.html#1), [segoon](/~segoon) (ok), 23:11, 04/11/2010 [[ответить](/cgi-bin/openforum/vsluhboard.cgi?az=post&om=72094&forum=vsluhforumID3&omm=1)]   | +/-
---|---
[![](/avatar/acae08f64757e5fffb94f76643d07c6a.jpg)](/~segoon)   setcap cap_chown,cap_dac_override,cap_sys_rawio,cap_sys_admin+ep /usr/bin/Xorg
Это, конечно, сильно уменьшает права Х-сервера. Эксплойту будет очень сложно получить права админа.

* [2](/openforum/vsluhforumID3/72094.html#2), [konst](/~konst) (??), 19:25, 07/11/2010 [[ответить](/cgi-bin/openforum/vsluhboard.cgi?az=post&om=72094&forum=vsluhforumID3&omm=2)]   | +/-
---|---
[![](/avatar/ed229c70d257749dacb8c2cdbe94fbf9.jpg)](/~konst)а зачем это надо, если остаются хоть какие-то setuid-битные файлы?

* [3](/openforum/vsluhforumID3/72094.html#3), [User294](/~User294) (ok), 22:19, 08/11/2010 [[ответить](/cgi-bin/openforum/vsluhboard.cgi?az=post&om=72094&forum=vsluhforumID3&omm=3)]   | -1 +/-
---|---
[![](/avatar/6f956eaf1c9f2ab2556da5c6707ef47b.jpg)](/~User294)>  дает возможность пользователям монтировать
> файловые системы к которым они не имеют доступа О как. Т.е. возможен еще и даунгрейд секурити таким макаром :)

* [4](/openforum/vsluhforumID3/72094.html#4), [eoranged](/~eoranged) (ok), 02:41, 20/01/2014 [[ответить](/cgi-bin/openforum/vsluhboard.cgi?az=post&om=72094&forum=vsluhforumID3&omm=4)]   | +/-
---|---
[![](/avatar/41a12896bd991d3e4ceb432a129bac9f.jpg)](/~eoranged)По-хорошему, выполнение большинства из этих задач от имени пользователя root является более безопасным, поскольку в данном случае происходит дополнительная изоляция процесса, обладающего повышенными привелегиями, и лишение пользователя контроля над этим процессом.

**  Добавить комментарий**
---
| Имя:|
---|---
E-Mail:|
Заголовок:|
Текст:

|

[Добавить заметку](/announce_tips.shtml?c=f)
---
Версия для печати

Поиск заметки:

[Последние заметки](/tips/sml/)
---
**-** 19.04.2026 [PKI с аппаратным TRNG за 10 дней при помощи AI](/tips/3296_ai_pki.shtml)
---
**-** 09.03.2026 [Борьба с web-ботами через запрет HTTP/1.1](/tips/3295_ai_bot_caddy_nginx_filter.shtml)
**-** 27.02.2026 [Удаление всех IPv6 link-local адресов на всех сетевых интерфейсах в Linux](/tips/3294_ipv6_linklocal.shtml)
**-** 27.01.2026 [Ускорение пересборки llama.cpp](/tips/3291_llama_build_ai.shtml)
**-** 25.12.2025 [Атомарные обновления в OSTree](/tips/3290_ostree_linux.shtml)
**-** 03.11.2025 [Отсеивание AI-ботов на web-сервере через Cookie](/tips/3287_bot_block_cookie_javascript_caddy_nginx.shtml)
**-** 01.11.2025 [Запуск Linux-контейнеров во FreeBSD](/tips/3284_freebsd_linux_container_podman.shtml)
**-** 26.10.2025 [Создание загрузочного атомарно обновляемого образа Oracle Linux при помощи OSTree](/tips/3280_rpm_ostree_oracel_rhel_linux_boot.shtml)
**-** 19.09.2025 [Сборка deb-пакета для решения проблем с плагином nvim-cmp для neovim в Debian 13](/tips/3278_debian_deb_dpkg_vim_neovim.shtml)
**-** 09.09.2025 [Запуск KDE Plasma 6 с Wayland во FreeBSD](/tips/3277_kde_freebsd.shtml)
**[RSS](/rss.shtml?last_tips) | [Следующие 15 записей >>](?skip=10#last)**

Партнёры:

[![PostgresPro](/img/pp_200.png)](https://www.postgrespro.ru)

[ ![Inferno Solutions](/img/inferno2.png)](https://ishosting.com/ru)

[![Hosting by Hoster.ru](/img/dh143x60t.png)](http://hoster.ru/?utm_source=site&utm_medium=banner&utm_campaign=opennet)

Хостинг:

[Закладки на сайте](/cgi-bin/opennet/bookmark.cgi)
[Проследить за страницей](/cgi-bin/opennet/bookmark.cgi?submit=add) |  Created 1996-2026 by **[Maxim Chirkov](/contact.shtml "email maxim.chirkov@gmail.com")**
[Добавить](https://www.opennet.ru/add.shtml), [Поддержать](https://www.opennet.ru/donate.shtml), [Вебмастеру](https://www.opennet.ru/banners2.shtml)
---|---|---

**********

[capabilities](/tags/capabilities.md)
[Linux](/tags/linux.md)
