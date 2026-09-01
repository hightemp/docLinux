# Как сбросить забытый пароль root на серверах CentOS 7

Для начала включите компьютер, на котором вы забыли пароль root. Для устройств CentOS 7 вам будет предоставлено 5 секунд в меню загрузки, чтобы выбрать ядро операционной системы для загрузки.

Эти 5 секунд важны, потому что позволяет администраторам выбирать разные ядра или редактировать существующие параметры ядра перед загрузкой.

В меню загрузки нажмите **e** для редактирования существующего ядра (Core), как показано ниже.

[![Changing root password on centos 7](/images/6639ad12dfb81779c5ab262634ba2ba3.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password.png)

[  
](https://is.ltroute.com/click.track?CID=420817&AFID=426982&SID=liberiangeek&nonencodedurl=https://www.fandomcentre.com/products/doctor-who-spinning-3d-tardis-police-box-pendant-necklace-w-30-chain)

Далее, прокрутите вниз до списка, пока не увидите строку, подчеркнутую ниже (**ro**). Что нам нужно сделать, это изменить это ro на rw и начать в оболочке bash. Это должно выглядеть так **rw init=/sysroot/bin/sh.**

[![forgotten root password on centos 7](/images/fec0c31cfaf6dc4587d9008125b9a50d.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-1.png)

Измените строку **ro** на **rw** и добавьте **init=/sysroot/bin/sh**

```
rw init=/sysroot/bin/sh
```

[![changing root password on centos](/images/91ec5236a7880cf72f8d01ebe5b1775f.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-2.png)

После изменения этого нажмите **Control + X** или **Ctrl + X** на клавиатуре, чтобы перейти в однопользовательский режим, используя оболочку bash, указанную выше. В этом режиме мы собираемся изменить пароль root.

В однопользовательском режиме выполните команду, как показано ниже

```
chroot /sysroot
```

[![password change on centos 7](/images/5db43420e207098a193135248fcae6cb.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-3.png)

Наконец, выполните команды ниже, чтобы изменить пароль root.

[![change password on centos 7](/images/629515fa748d692d5f3e254117e5f55a.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-4.png)

Вам будет предложено создать и подтвердить новый пароль. После создания пароля выполните команды ниже, чтобы обновить параметры SELinux

```
touch /.autorelabel
```

Выйдите и перезагрузите вашу систему. Вы должны иметь возможность войти в систему и использовать систему с новым паролем, который вы создали. Так вы меняете пароль root в CentOS 7.

**********
[CentOS](/tags/CentOS.md)
