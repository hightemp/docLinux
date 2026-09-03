# SSH: локальная переадресация портов

Источник: [SSH Local Port Forwarding](https://penkovski.com/post/ssh-local-port-forwarding/)

penkovski · 16 марта 2020 · 122 слова

Чтобы переадресовать запросы, приходящие на локальный TCP-порт, на другой сервер [host:port], подключённый через SSH, можно использовать конфигурационный файл или аргументы командной строки напрямую. Для использования конфигурационного файла он должен называться `config` и располагаться в каталоге `~/.ssh`. Вот пример файла `~/.ssh/config` с некоторыми опциями:

```text
Host my-ssh-connection
  Hostname 10.20.30.40
  User penkovski
  LocalForward 7070 localhost:8080
  LocalForward 7171 localhost:8181
  ControlMaster auto
```

Эта настройка переадресует все запросы, поступающие на локальный (клиентский) TCP-порт 7070, на localhost:8080 сервера, а все запросы на локальный TCP-порт 7171 — на localhost:8181 сервера. Приведённая конфигурация будет использоваться автоматически при установке SSH-соединения по алиасу:

```bash
ssh my-ssh-connection
```

**********

[ssh](/tags/ssh.md)
[ssh туннели](/tags/ssh_tunnels.md)
[Linux](/tags/linux.md)