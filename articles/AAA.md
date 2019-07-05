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