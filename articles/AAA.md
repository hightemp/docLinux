**AAA** – Authentication, Authorization and Accounting, функция, которая представляет собой комплексную структуру организации доступа пользователя в сеть. За ней, собственно, кроются такие базовые процессы, как:

*    **Аутентификация** , где система предлагает пользователю ввести свое имя и пароль, прежде чем позволить ему совершать дальнейшие действия.
*    **Авторизация** . Успешно пройдя аутентификацию, система авторизует пользователя в сети, наделяя его теми полномочиями, которые соотносятся с его учетной записью (именем и паролем).
*    **Учет** . Отвечает за сбор информации об учетной записи пользователя и отправке ее на сервер, хороший тому пример - биллинг интернет-провайдера.

Для активации AAA, в режиме глобальной конфигурации достаточно набрать _aaa new-model_ .

> Будьте осторожны, если вы не успели создать на оборудовании хотя бы одного пользователя [User](http://telecombook.ru/archive/network/cisco/directory/74-user) с паролем, то при попытке зайти на устройство, система запросит имя и пароль, даже если его еще не существует.

Зададим инструкцию командой _aaa authentication login default local_ , которая позволит использовать локальную базу данных для **аутентификации** .

Теперь нам необходимо уточнить, где именно применять данное действие. Для этого мы пропишем команду _login authentication default_ в режиме конфигурации интерфейса [console](http://telecombook.ru/archive/network/cisco/directory/48-console) и [VTY](http://telecombook.ru/archive/network/cisco/directory/76-vty) .

Посредством обращения к локальной базе данных, **авторизация** осуществляется аналогичным методом, командой _aaa authorization exec default local_ и прописывается командой _authorization exec default_ в [console](http://telecombook.ru/archive/network/cisco/directory/48-console) и [VTY](http://telecombook.ru/archive/network/cisco/directory/76-vty) . Чтобы авторизация возымела действие на консоли, в режиме глобальной конфигурации необходимо добавить команду _aaa authorization console_ .

Пример:

```
aaa new-model
aaa authentication login default local
aaa authorization exec default local
aaa authorization console

line console 0
 login authentication default
 authorization exec default

line vty 0 15
 login authentication default
 authorization exec default
```

 **AAA** (от [англ.](https://ru.wikipedia.org/wiki/%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA "Английский язык")   Authentication, Authorization, Accounting ) — семейство протоколов, используется для описания процесса предоставления доступа и контроля над ним.

*    _Authentication_ ( [аутентификация](https://ru.wikipedia.org/wiki/%D0%90%D1%83%D1%82%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F "Аутентификация") ) — сопоставление персоны (запроса) существующей учётной записи в системе безопасности. Осуществляется по [логину](https://ru.wikipedia.org/wiki/%D0%9B%D0%BE%D0%B3%D0%B8%D0%BD_(%D1%83%D1%87%D1%91%D1%82%D0%BD%D0%B0%D1%8F_%D0%B7%D0%B0%D0%BF%D0%B8%D1%81%D1%8C) "Логин (учётная запись)") , [паролю](https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D1%80%D0%BE%D0%BB%D1%8C "Пароль") , [сертификату](https://ru.wikipedia.org/wiki/%D0%A1%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82_(%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D1%8F) "Сертификат (криптография)") , [смарт-карте](https://ru.wikipedia.org/wiki/%D0%A1%D0%BC%D0%B0%D1%80%D1%82-%D0%BA%D0%B0%D1%80%D1%82%D0%B0 "Смарт-карта") и т. д.
*    _Authorization_ ( [авторизация](https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F "Авторизация") , проверка полномочий, проверка уровня доступа) — сопоставление учётной записи в системе (и персоны, прошедшей аутентификацию) и определённых полномочий (или запрета на доступ). В общем случае авторизация может быть «негативной» (пользователю А запрещён доступ к [серверам](https://ru.wikipedia.org/wiki/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80_(%D0%B0%D0%BF%D0%BF%D0%B0%D1%80%D0%B0%D1%82%D0%BD%D0%BE%D0%B5_%D0%BE%D0%B1%D0%B5%D1%81%D0%BF%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5) "Сервер (аппаратное обеспечение)") компании).
*    _Accounting_ (учёт) — слежение за потреблением ресурсов (преимущественно сетевых) пользователем. В accounting включается также и запись фактов получения доступа к системе ( [англ.](https://ru.wikipedia.org/wiki/%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA "Английский язык")   access logs ).

**********
[AAA](/tags/AAA.md)
