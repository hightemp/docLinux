# github ssh proxy

Setting `http.proxy` will not work for ssh. You need to proxy your ssh connection. See [this](http://returnbooleantrue.blogspot.com/2009/06/using-github-through-draconian-proxies.html) description. To summarize:

Start `git-cmd.bat` and create `~/.ssh/config` ( `notepad %home%\.ssh\config.` )

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

(set the correct proxy hostname:port, and the path to id\_rsa. When you use git-bash, use slashes in the path to id\_rsa)  
(My version of [msysgit](https://github.com/msysgit/msysgit/releases) includes `connect.exe` , so I do not need to download and compile [connect.c](https://web.archive.org/web/20130731110457/http://www.meadowy.org/~gotoh/ssh/connect.c) ). A precompiled exe is also available [here](https://web.archive.org/web/20130516045959/http://www.meadowy.org/~gotoh/ssh/connect.exe) .

Now `ssh github.com` should work

Note that if you want to connect via a socks5 proxy, then change `-H` to `-S` .

```
ProxyCommand connect -S proxy.server.name:1080 %h %p

```

If you use a Linux file system, the file permission of `~/.ssh/config` must be 600, but on a standard NTFS windows partition, these kind of permissions do not exist.

If your proxy requires NTLM authentication, you can use [cntlm](http://cntlm.sourceforge.net/) , see also [this answer](https://stackoverflow.com/a/15343300/33499) .

**********
[ssh](/tags/ssh.md)
[github](/tags/github.md)
