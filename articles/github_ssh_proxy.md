# github ssh proxy

Установка `http.proxy` не будет работать для ssh. Вам необходимо прокси-соединение вашего SSH. См. [Это](http://returnbooleantrue.blogspot.com/2009/06/using-github-through-draconian-proxies.html) описание. Подвести итоги:

Запустите `git-cmd.bat` и создайте `~/.ssh/config` (`notepad %home%\.ssh\config`).

```
ProxyCommand /bin/connect.exe -H proxy.server.name:3128 %h %p

Host github.com
  User git
  Port 22
  Hostname github.com
  IdentityFile "C:\users\username\.ssh\id_rsa"
  TCPKeepAlive yes
  IdentitiesOnly yes

Host ssh.github.com
  User git
  Port 443
  Hostname ssh.github.com
  IdentityFile "C:\users\username\.ssh\id_rsa"
  TCPKeepAlive yes
  IdentitiesOnly yes

```

(установите правильное имя хоста прокси: порт и путь к id\_rsa. Когда вы используете git-bash, используйте косую черту в пути к id\_rsa)
(Моя версия [msysgit](https://github.com/msysgit/msysgit/releases) включает в себя `connect.exe`, поэтому мне не нужно скачивать и компилировать [connect.c](https://web.archive.org/web/20130731110457/http://www.meadowy.org/~gotoh/ssh/connect.c)). Предварительно скомпилированный exe также доступен [здесь](https://web.archive.org/web/20130516045959/http://www.meadowy.org/~gotoh/ssh/connect.exe).

Теперь `ssh github.com` должен работать

Обратите внимание, что если вы хотите подключиться через прокси socks5, измените `-H` на `-S`.

```
ProxyCommand connect -S proxy.server.name:1080 %h %p

```

Если вы используете файловую систему Linux, разрешение файла `~/.ssh/config` должно быть 600, но для стандартного раздела Windows NTFS такого рода разрешения не существует.

Если вашему прокси-серверу требуется NTLM-аутентификация, вы можете использовать [cntlm](http://cntlm.sourceforge.net/), см. Также [этот ответ](https://stackoverflow.com/a/15343300/33499).


**********
[ssh](/tags/ssh.md)
[github](/tags/github.md)
[git](/tags/git.md)
