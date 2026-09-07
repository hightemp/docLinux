# Resolv.conf

Источник: [Resolv.conf](http://tdkare.ru/sysadmin/index.php/Resolv.conf)

## Содержание

  * 1 Литература
  * 2 Справочная информация

---

**Статья с описанием файла resolv.conf**

Файл **[/etc/resolv.conf](http://tdkare.ru/sysadmin/files/Resolv.conf/resolv.conf "http://tdkare.ru/sysadmin/files/Resolv.conf/resolv.conf")** это файл конфигурации для процедур [сервера имен](/sysadmin/index.php/DNS-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D1%8B "DNS-серверы"). Файл конфигурации содержит информацию, которая читается процедурами разрешения имен при первом их вызове процессом. Процедуры обеспечивают доступ к [системе доменных имен](/sysadmin/index.php/DNS-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D1%8B "DNS-серверы").

Файл содержит строки вида:

```text
  ключевое_слово  значение
  например
  **nameserver**      адрес
  **domain**          имя
  **search**          список_поиска
  **sortlist**        список_сортировки
  **options**         список_опций
```

Внимание!

```text
  если установлена утилита [resolvconf](/sysadmin/index.php?title=Resolvconf&action=edit&redlink=1 "Resolvconf \(такой страницы не существует\)") (и файл resolv.conf формируется автоматически), то
  для добавления просматриваемых dns-серверов "до" / "после" локального 127.0.0.1
  добавляем в файл </etc/resolvconf/resolv.conf.d/base> / </etc/resolvconf/resolv.conf.d/tail> строки
     nameserver ip_my_dns
```

Пример файла [/etc/resolv.conf](http://tdkare.ru/sysadmin/files/Resolv.conf/resolv.conf "http://tdkare.ru/sysadmin/files/Resolv.conf/resolv.conf")

```text
  domain my                     - указание имени домена
  search my                     - указание списка поиска
  nameserver ip_dnsserver       - указание [dns-сервера](/sysadmin/index.php/DNS-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D1%8B "DNS-серверы")
```

##  Литература

  * [Man`s rus: Форматы файлов: resolv.conf](http://www.opennet.ru/man.shtml?topic=resolv.conf&category=4 "http://www.opennet.ru/man.shtml?topic=resolv.conf&category=4")
  * [Конфигурирование сервера поиска --- resolv.conf](http://citforum.ru/operating_systems/linux_nag/linuxnag_05.shtml "http://citforum.ru/operating_systems/linux_nag/linuxnag_05.shtml")

**********

[dns](/tags/dns.md)
