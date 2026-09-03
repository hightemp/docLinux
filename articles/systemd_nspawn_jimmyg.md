# systemd-nspawn

Источник: [Systemd Nspawn](https://jimmyg.org/blog/2022/nspawn/index.html)

10 января 2022

Актуально только для Debian 11.

## Установка

На хосте:

```bash
sudo apt install systemd-container debootstrap
sudo systemctl enable machines.target
sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved
```

Затем:

```bash
export MACHINE=debian
sudo debootstrap --variant=minbase --include=systemd-container stable /var/lib/machines/$MACHINE
sudo du -hs /var/lib/machines/$MACHINE
sudo systemd-nspawn -D /var/lib/machines/$MACHINE -U --machine $MACHINE
```

Установите пароль root, задайте имя хоста и включите сеть при загрузке:

```bash
systemctl enable systemd-networkd.service
systemctl enable systemd-resolved.service
echo 'debian' > /etc/hostname
passwd
logout
```

Снова на хосте:

```bash
sudo mkdir -p /etc/systemd/nspawn
cat << EOF | sudo tee /etc/systemd/nspawn/$MACHINE.nspawn > /dev/null
[Exec]
PrivateUsers=pick
ResolvConf=bind-static

[Network]
VirtualEthernet=yes
# Forward port 80 in the host to port 80 in the container so it is accessible externally
Port=tcp:80

[Files]
PrivateUsersChown=yes
EOF
```

Если вы измените этот файл позже, выполните следующее, чтобы изменения вступили в силу:

```bash
sudo systemctl daemon-reload
```

Теперь настроим автозапуск:

```bash
# Start it at reboot:
sudo systemctl enable systemd-nspawn@$MACHINE.service
# Start it now
sudo systemctl start systemd-nspawn@$MACHINE
systemctl status systemd-nspawn@$MACHINE.service
journalctl -u systemd-nspawn@$MACHINE.service
```

Если вы хотите менять лимиты открытых файлов внутри контейнера, добавьте `LimitNOFILE` в секцию `[Exec]` файла `/etc/systemd/nspawn/$MACHINE.nspawn`:

```text
[Exec]
...
LimitNOFILE=infinity
```

Теперь войдите в контейнер:

```bash
sudo machinectl login $MACHINE
```

ВНИМАНИЕ: убедитесь, что `$MACHINE` действительно установлена, иначе вы по ошибке войдёте в хостовую машину!

Выход — `Ctrl+]]]`.

Установите несколько инструментов:

```bash
apt update
apt install -y nginx iproute2 iputils-ping curl
```

Затем внутри контейнера можно выполнить:

```bash
curl http://127.0.0.1
```

а на хосте (но 127.0.0.1 не работает):

```bash
curl http://<public_ip_address>
```

После перезагрузки всё продолжит работать.

В дальнейшем на хосте:

```bash
sudo machinectl start $MACHINE
sudo machinectl stop $MACHINE
sudo machinectl list
```

## Типовые задачи

Я предпочитаю создать нового пользователя с доступом `sudo` и установить openSSH-сервер для удалённого входа:

```bash
apt update
apt install -y openssh-server sudo
/sbin/adduser james
/sbin/usermod -a -G sudo james
```

После этого я могу войти с хоста так, и у меня будет sudo-доступ, когда понадобится:

```bash
ssh james@$MACHINE
```

(Если вы войдёте по SSH до добавления `james` в группу `sudo`, потребуется войти заново, чтобы изменение было замечено.)

Обычно я также добавляю:

```bash
sudo apt install -y python3 vim screen
```

## Проблемы

  * Контейнеры не обязательно имеют статические IP — но вы всегда можете использовать имя машины как имя хоста для доступа через Zone bridge, например `curl http://$MACHINE`.
  * Сеть контейнеров не переживает suspend — после него нужно перезапустить контейнеры.

## Очистка

```bash
sudo systemctl stop systemd-nspawn@$MACHINE
sudo systemctl disable systemd-nspawn@$MACHINE.service
sudo rm /etc/systemd/nspawn/$MACHINE.nspawn
```

Затем удалите `/var/lib/machines/$MACHINE`.

**********

[systemd](/tags/systemd.md)
[systemd-nspawn](/tags/systemd-nspawn.md)
[Linux](/tags/linux.md)