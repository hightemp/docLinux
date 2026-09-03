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

##  Справочная информация

  * 25.05.2012: ****Resolv.conf**** : создание статьи в википедии

Источник — «<http://tdkare.ru/sysadmin/index.php/Resolv.conf>»

[Категория](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:Categories "Служебная:Categories"): [Resolv.conf](/sysadmin/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:Resolv.conf&action=edit&redlink=1 "Категория:Resolv.conf \(такой страницы не существует\)")

##### Просмотры

  * [Статья](/sysadmin/index.php/Resolv.conf "Содержание статьи \[c\]")
  * [Обсуждение](/sysadmin/index.php?title=%D0%9E%D0%B1%D1%81%D1%83%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5:Resolv.conf&action=edit&redlink=1 "Обсуждение содержания страницы \[t\]")
  * [Просмотр](/sysadmin/index.php?title=Resolv.conf&action=edit "Эта страница защищена от изменений, но вы можете посмотреть и скопировать её исходный текст \[e\]")
  * [История](/sysadmin/index.php?title=Resolv.conf&action=history "Журнал изменений страницы \[h\]")

##### Личные инструменты

  * [Представиться системе](/sysadmin/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:UserLogin&returnto=Resolv.conf "Здесь можно зарегистрироваться в системе, но это необязательно. \[o\]")

##### Поиск

##### Навигация

  * [Главная](/sysadmin/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0)
  * [Новости](/sysadmin/index.php/News)
  * [Указатель](/sysadmin/index.php/Abc-article)
  * [Рубрикатор](/sysadmin/index.php/Theme-article)
  * [Случайное](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:Random)
  * [Популярное](/sysadmin/index.php/Popularpagespage)
  * [Поиск](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:PrefixIndex)
  * [Справка](/sysadmin/index.php/%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0:%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0)

##### участие

  * [Форум](/sysadmin/index.php/Forum-url)
  * [Текущие события](/sysadmin/index.php/%D0%9F%D0%B8%D0%BD%D0%B3%D0%B2%D0%B8%D0%BD%D1%8C%D0%B8_%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8:%D0%A2%D0%B5%D0%BA%D1%83%D1%89%D0%B8%D0%B5_%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D1%8F "Список текущих событий")
  * [Свежие правки](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:RecentChanges "Список последних изменений \[r\]")
  * [Статистика](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:Statistics)

##### поддержка

  * [Контакты](/sysadmin/index.php/%D0%9A%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82%D0%BD%D0%B0%D1%8F_%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D1%8F)
  * [Помощь сайту](/sysadmin/index.php/Mercypage)
  * [Наш Спонсор](http://tdkare.ru/)
  * [ЗнайкаФон](http://tdkare.ru/znaikafon)

##### Инструменты

  * [Ссылки сюда](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:WhatLinksHere/Resolv.conf "Список всех страниц, которые ссылаются на эту страницу \[j\]")
  * [Связанные правки](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:RecentChangesLinked/Resolv.conf "Последние изменения в страницах, на которые ссылается эта страница \[k\]")
  * [Спецстраницы](/sysadmin/index.php/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:SpecialPages "Список служебных страниц \[q\]")
  * [Версия для печати](/sysadmin/index.php?title=Resolv.conf&printable=yes "Версия этой страницы для печати \[p\]")
  * [Постоянная ссылка](/sysadmin/index.php?title=Resolv.conf&oldid=5122 "Постоянная ссылка на эту версию страницы")

  * Последнее изменение этой страницы: 07:16, 27 марта 2013.
  * К этой странице обращались 5094 раза.
  * [Политика конфиденциальности](/sysadmin/index.php/%D0%9F%D0%B8%D0%BD%D0%B3%D0%B2%D0%B8%D0%BD%D1%8C%D0%B8_%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8:%D0%9F%D0%BE%D0%BB%D0%B8%D1%82%D0%B8%D0%BA%D0%B0_%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B4%D0%B5%D0%BD%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8 "Пингвиньи радости:Политика конфиденциальности")
  * [Описание Пингвиньи радостей](/sysadmin/index.php/%D0%9F%D0%B8%D0%BD%D0%B3%D0%B2%D0%B8%D0%BD%D1%8C%D0%B8_%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8:%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5 "Пингвиньи радости:Описание")
  * [Отказ от ответственности](/sysadmin/index.php/%D0%9F%D0%B8%D0%BD%D0%B3%D0%B2%D0%B8%D0%BD%D1%8C%D0%B8_%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8:%D0%9E%D1%82%D0%BA%D0%B0%D0%B7_%D0%BE%D1%82_%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D0%B8 "Пингвиньи радости:Отказ от ответственности")

**********

[dns](/tags/dns.md)
