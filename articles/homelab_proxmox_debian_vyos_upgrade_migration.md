# Homelab: миграция и обновление Proxmox + Debian + VyOS

Источник: [Homelab Proxmox + Debian + VyOS upgrade migration](https://www.vanwerkhoven.org/blog/2024/homelab-upgrade-migration/)

Тим ванн Веркховен · 16 ноября 2024

Здесь я документирую конфигурацию своего домашнего сервера и путь обновления с Debian 11 до 12 / Proxmox 7 до 8. Около 2 лет назад я [мигрировал на Proxmox (vanwerkhoven.org)](https://www.vanwerkhoven.org/blog/2022/home-server-configuration/) как на хост с клиентами под ним. До сих пор это был хороший опыт: например, миграция Home Assistant из Docker-образа в отдельную VM сработала и прошла гладко. Кроме того, при обновлении Debian с 11 до 12 я могу создать параллельную VM и переносить сервисы один за другим вместо полной переустановки. Наконец, я хочу обновить сам Proxmox с 7 до 8 — это самое сложное и может потребовать переустановки.

# Содержание

  * Обзор конфигурации
  * Целевые сервисы и архитектура
  * Подход к миграции Proxmox
    * План
    * Выполнение
  * Выбор новой файловой системы
  * Сборка нового Debian LXC
    * Получение образа и запуск LXC
    * Первоначальная настройка Debian
    * Оптимизация Debian
    * Установка Docker
  * Миграция сервисов
    * Nginx
    * Grafana
    * Docker
    * Mosquitto
    * mqtt2influxdb
    * InfluxDB
    * Рабочие скрипты
    * Автоматические резервные копии
    * zigbee2mqtt
    * smokeping
    * Медиасервер
    * Transmission
    * Ente photos

# Обзор конфигурации

Цель и железо не изменились по сравнению с [моим оригинальным постом (vanwerkhoven.org)](https://www.vanwerkhoven.org/blog/2022/home-server-configuration/).

# Целевые сервисы и архитектура

Моя конфигурация такова:

  * Proxmox (32 ГБ хранилища + 2 ГБ RAM)
    * предоставляет гостям общее «бulk»-хранилище через точки монтирования
    * N.B. Изначально у меня здесь было 8 ГБ хранилища — это немного впритык
  * VyOS VM (8 ГБ хранилища + 2 ГБ RAM)
    * [dns adblock (vanwerkhoven.org)](https://www.vanwerkhoven.org/blog/2023/dns-based-adblocking-on-vyos/)
    * wireguard VPN
    * fq-codel QoS
    * зонный фаервол через VLAN'ы
    * N.B. Это уже давно работает стабильно. VyOS функционально богат и хорошо подходит для запуска как VM под Proxmox
  * Debian Stable LXC 'unifi' (8 ГБ хранилища + 2 ГБ RAM)
    * unifi-controller установлен нативно
  * Debian Stable LXC 'proteus' (256 ГБ хранилища + 24 ГБ RAM)
    * Сервисы первого приоритета
      * Nginx (для сайта и обратных прокси)
      * Letsencrypt/Lego (для SSL-сертификатов)
      * Docker
        * Nextcloud (для обмена файлами)
        * bpatrik/pigallery2 (для личного обмена фотографиями)
      * Рабочие скрипты домашней автоматизации (для генерации/сбора данных)
        * много
      * Influxdb (для хранения данных)
      * Mosquitto (склейка домашней автоматизации)
    * Второй приоритет
      * Grafana (для визуализации данных)
      * Plex/Jellyfin/Emby (HTPC)
      * Collectd (для генерации/сбора данных)
      * Внешний сервер метрик Proxmox
      * smbd (для резервных копий Time Machine)
      * Transmission (скачивание торрентов)
  * Home Assistant VM (для мониторинга)

# Подход к миграции Proxmox

## План

  * Развернуть второй сервер Proxmox, чтобы разгрузить виртуальный роутер на время обновления
    * Инициализировать proxmox 8
    * Перенести образ VyOS со старого proxmox на новый
    * Использовать второй proxmox как временный роутер
  * Обновить существующий Proxmox свежей установкой
    * Забэкапить и скачать всех гостей (~50 ГБ) `rsync -avH --progress --delete pve:/mnt/backup/vms/dump/\*2025_02_22-2\* ~/Documents/20250221_proxmox_migration/`
    * Скачать все данные вне гостей (bulk, исключая бэкапы time machine)
    * Скачать все конфигурационные данные на proxmox (`/etc/*`)
    * Очистить сервер и выполнить чистую установку proxmox (см. )
      * Установка с настройкой ZFS
    * Восстановить гостей
      * Убедиться, что настройки сохранены (unprivileged, правильные сетевые интерфейсы) — OK
    * Восстановить конфигурацию
      * sudoers (для bluetooth и lvs) — не нужно
      * collectd (для мониторинга) — OK
      * точки монтирования — OK
      * проброс bluetooth не нужен — OK
    * Отладка и тестирование
      * HA
        * zigbee уходит в qemu HA -> проброс USB порта — OK
      * VyOS
        * Проверить VPN
      * unifi
        * Проверить приложение — OK
      * proteus
        * проверить логин — OK

## Выполнение

  * Развернуть второй сервер Proxmox, чтобы разгрузить виртуальный роутер на время обновления — OK

  * Подготовить USB

```bash
diskutil unmountDisk /dev/disk6
sudo dd if=proxmox-ve_8.3-1.dmg  bs=1M of=/dev/disk6
```

  * Загрузиться с USB
  * Выбрать диск 2TB для начала
  * Следовать инструкциям на экране
  * Выбрать размер диска 300 ГБ для VM с использованием zfs
  * Позже: создать второй zpool из оставшегося места NVME-диска и всего SATA-диска для данных и бэкапов
  * Отладка: очистить старый ZFS с диска

```bash
zpool labelclear -f /dev/sda{1,2,3,4}
```

  * Отладка: не удаётся импортировать rpool: добавить задержку загрузки [https://pve.proxmox.com/wiki/ZFS:_Tips_and_Tricks#Grub_boot_ZFS_problem (proxmox.com)](https://pve.proxmox.com/wiki/ZFS:_Tips_and_Tricks#Grub_boot_ZFS_problem)
  * Выполнить первоначальную настройку из XX
  * Отправить обратно образы бэкапов

```bash
chown root:adm /var/lib/vz/*
chmod g+w /var/lib/vz/*
rsync -avH --progress ~/Documents/20250221_proxmox_migration/ 172.17.10.4:/var/lib/vz/dump/
```

  * настроить `/etc/sub?uid`

```text
cat « 'EOF' »/etc/subuid root:1010:10 EOF cat « 'EOF' »/etc/subgid root:1010:10 EOF
```

  * обновить точки монтирования

```bash
pct set 203 -mp0 /tank/bulk,mp=/mnt/bulk
pct set 203 -mp1 /tank/backups/backupsmbp,mp=/mnt/backup/mbp
pct set 203 -mp2 /tank/backups/backupsmba,mp=/mnt/backup/mba
pct set 203 -mp3 /tank/backups/data-tim,mp=/mnt/backup/data-tim
pct set 203 -mp4 /tank/backups/data-helene,mp=/mnt/backup/data-helene
```

  * Отправить данные обратно на сервер -> OK

```bash
rsync -avH --progress /Volumes/WD5TB-TM-Helene/ 172.17.10.4:/tank/backups/backupsmba/
rsync -avH --progress /Volumes/3TB/ 172.17.10.4:/tank/bulk/
```

  * исправить scaling_governor (доступны только performance и powersave?) -> исправить командную строку через /etc/kernel/cmdline
  * исправить collectd на pve для zfs -> позже
  * восстановить схему бэкапов -> OK

# Выбор новой файловой системы

Раньше я использовал ext4 поверх LVM с тонкими томами (thin volumes). LVM имеет преимущество гибкого использования нескольких дисков, однако он не предоставляет COW (copy-on-write) или обнаружение/защиту от битрота (bitrot).

Тест производительности: [https://www.percona.com/blog/taking-a-look-at-btrfs-for-mysql/ (percona.com)](https://www.percona.com/blog/taking-a-look-at-btrfs-for-mysql/) Тюнинг ZFS: [https://www.zfshandbook.com/docs/advanced-zfs/performance-tuning/ (zfshandbook.com)](https://www.zfshandbook.com/docs/advanced-zfs/performance-tuning/) Бенчмарки: [https://www.reddit.com/r/btrfs/comments/bpphbz/my_benchmarks_of_the_new_zstd_levels_in_51/ (reddit.com)](https://www.reddit.com/r/btrfs/comments/bpphbz/my_benchmarks_of_the_new_zstd_levels_in_51/)

```bash
sudo mkdir /mnt/btrfs-test
sudo mkdir /mnt/ext4-test
sudo mkdir /mnt/zfs-record128k-test
sudo mkdir /mnt/zfs-record32k-test
sudo mkdir /mnt/zfs-record8k-test

sudo mkfs.btrfs /dev/nvme0n1p6
sudo mount /dev/nvme0n1p6 /mnt/btrfs-test
cd /mnt/btrfs-test

  WRITE: bw=721MiB/s (756MB/s), 39.5MiB/s-54.6MiB/s (41.4MB/s-57.3MB/s), io=21.4GiB (23.0GB), run=30302-30369msec
  WRITE: bw=675MiB/s (708MB/s), 36.4MiB/s-50.7MiB/s (38.2MB/s-53.2MB/s), io=20.1GiB (21.6GB), run=30516-30539msec

sudo mount -t btrfs /dev/nvme0n1p6 /mnt/btrfs-test -o compress-force=zstd:1,noatime,autodefrag
cd /mnt/btrfs-test

  WRITE: bw=735MiB/s (771MB/s), 42.1MiB/s-50.5MiB/s (44.2MB/s-52.9MB/s), io=22.0GiB (23.6GB), run=30468-30640msec

# sudo mkfs.ext4 /dev/nvme0n1p7
sudo zpool create -o ashift=12 ztest12 /dev/nvme0n1p7
sudo zfs create ztest12/test128
sudo zfs set recordsize=128k ztest12/test128
cd /ztest12/test128

  WRITE: bw=294MiB/s (308MB/s), 14.7MiB/s-29.0MiB/s (15.4MB/s-30.4MB/s), io=9031MiB (9469MB), run=30687-30720msec
  WRITE: bw=370MiB/s (388MB/s), 19.2MiB/s-29.6MiB/s (20.1MB/s-31.0MB/s), io=11.1GiB (11.9GB), run=30660-30701msec

sudo zfs create ztest12/test32
sudo zfs set recordsize=32k ztest12/test32
cd /ztest12/test32

  WRITE: bw=640MiB/s (671MB/s), 36.7MiB/s-44.1MiB/s (38.5MB/s-46.3MB/s), io=19.1GiB (20.5GB), run=30441-30496msec
  WRITE: bw=514MiB/s (538MB/s), 27.2MiB/s-44.6MiB/s (28.5MB/s-46.8MB/s), io=15.5GiB (16.7GB), run=30954-30996msec

sudo zfs create ztest12/test8
sudo zfs set recordsize=8k ztest12/test8
cd /ztest12/test8

  WRITE: bw=473MiB/s (496MB/s), 24.2MiB/s-36.8MiB/s (25.4MB/s-38.6MB/s), io=14.0GiB (15.1GB), run=30300-30337msec
  WRITE: bw=351MiB/s (368MB/s), 13.8MiB/s-35.3MiB/s (14.5MB/s-37.0MB/s), io=10.4GiB (11.2GB), run=30393-30452msec

sudo mkfs.ext4 /dev/nvme0n1p8
sudo mount /dev/nvme0n1p8 /mnt/ext4-test
cd /mnt/ext4-test

  WRITE: bw=1513MiB/s (1586MB/s), 86.6MiB/s-106MiB/s (90.8MB/s-111MB/s), io=46.4GiB (49.8GB), run=30340-31393msec
  WRITE: bw=951MiB/s (997MB/s), 53.9MiB/s-67.6MiB/s (56.5MB/s-70.9MB/s), io=29.0GiB (31.1GB), run=30277-31223msec

sudo mkfs.xfs /dev/nvme0n1p9
sudo mount -t xfs /dev/nvme0n1p9 /mnt/xfs-test
cd /mnt/xfs-test

  WRITE: bw=1672MiB/s (1753MB/s), 85.7MiB/s-147MiB/s (89.9MB/s-154MB/s), io=51.3GiB (55.0GB), run=30124-31393msec

cd /root/

  WRITE: bw=712MiB/s (747MB/s), 16.1MiB/s-227MiB/s (16.9MB/s-238MB/s), io=23.1GiB (24.8GB), run=32295-33180msec

sudo fio --name=random-write --ioengine=posixaio --rw=randwrite --bs=64k --size=128m --numjobs=16 --iodepth=16 --runtime=30 --time_based --end_fsync=1

sudo fio --ioengine=libaio --direct=1 --sync=1 --rw=read --bs=4K --numjobs=1 --iodepth=1 --runtime=30 --time_based --name seq_read
```

# Сборка нового Debian LXC

## Получение образа и запуск LXC

Получите образы через [Proxmox VE Appliance Manager (proxmox.com)](https://pve.proxmox.com/pve-docs/pve-admin-guide.html#pct_container_images):

```bash
sudo pveam update
sudo pveam available
# sudo pveam download local debian-11-standard_11.6-1_amd64.tar.zst
sudo pveam download local debian-12-standard_12.7-1_amd64.tar.zst
sudo pveam list local
```

Проверьте, какое хранилище использовать:

```bash
pvesm status
```

[Создайте и настройте LXC-контейнер (proxmox.com)](https://pve.proxmox.com/pve-docs/pve-admin-guide.html#pct_settings) на основе скачанного образа. Убедитесь, что это непривилегированный (unprivileged) контейнер, чтобы защитить наш хост и работающий на нём роутер.

```bash
sudo pct create 203 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst --description "Debian 12 LXC" --hostname proteus2 --rootfs thinpool_vms:256 --unprivileged 1 --cores 4 --memory 16384 --ssh-public-keys /root/.ssh/tim.id_rsa.pub --net0 name=eth0,bridge=vmbr0,firewall=0,gw=172.17.10.1,ip=172.17.10.7/24,tag=10
```

Теперь настройте сеть — на `vmbr0` Proxmox с VLAN ID 10. Это значит, что гость может получать доступ только к VLAN 10.

```bash
# This does not work, cannot create network device on vmbr0.10
# pct set 203 --net0 name=eth0,bridge=vmbr0.10,firewall=0,gw=172.19.10.1,ip=172.19.10.2/24
# Does not work:
# pct set 203 --net0 name=eth0,bridge=vmbr0,firewall=0,gw=172.17.10.1,ip=172.17.10.2/24,trunks=10
# Works:
# pct set 203 --net0 name=eth0,bridge=vmbr0,firewall=0,gw=172.17.10.1,ip=172.17.10.2/24,tag=10
sudo pct set 203 --onboot 1
```

Опционально: требуется только если хост настроил это некорректно (может быть из-за недоступности сети при инициализации):

```bash
sudo pct set 203 --searchdomain lan.vanwerkhoven.org --nameserver 172.17.10.1
```

Если SSH в гостя не работает или занимает много времени, это может быть из-за [функций безопасности LXC / Apparmor (stackoverflow.com)](https://stackoverflow.com/a/74804457), которые не дают выполниться `mount`. Чтобы решить, [разрешите nesting (ostechnix.com)](https://ostechnix.com/enable-nested-virtualization-in-proxmox/):

```bash
sudo pct set 203 --features nesting=1
```

Чтобы [включить Docker (jlu5.com)](https://jlu5.com/blog/docker-unprivileged-lxc-2021) внутри LXC-контейнера, нужны и nesting, и keyctl:

```bash
sudo pct set 203 --features nesting=1,keyctl=1
```

## Первоначальная настройка Debian

Запустите и войдите, задайте пароль root, настройте основы:

```bash
sudo pct start 203
sudo pct enter 203

passwd
apt install sudo vim

cat << 'EOF' | sudo tee -a /usr/share/vim/vim??/defaults.vim
" TvW 20230808 enable copy-paste - see https://vi.stackexchange.com/questions/13099/not-able-to-copy-from-terminal-when-using-vim-from-homebrew-on-macos
set mouse=r
EOF

dpkg-reconfigure locales
dpkg-reconfigure tzdata
```

Подправьте bashrc, чтобы [объединять историю (askubuntu.com)](https://askubuntu.com/questions/80371/bash-history-handling-with-multiple-terminals) и хранить её дольше:

```bash
cat << 'EOF' >> ~tim/.bashrc
# TvW 20230812 expand history, add date/time (iso fmt), ignore space/duplicates
HISTSIZE=500000
HISTFILESIZE=1000000
HISTTIMEFORMAT="%F %T "
HISTCONTROL=ignoreboth:erasedups
PROMPT_COMMAND="history -a"
EOF
```

Добавьте обычного пользователя, добавьте его в [системные группы (debian.org)](https://wiki.debian.org/SystemGroups#Other_System_Groups) и задайте ssh-ключ:

```bash
adduser tim
usermod -aG adm,render,sudo,staff,ssl-cert tim
mkdir -p ~tim/.ssh/
touch ~tim/.ssh/authorized_keys
chown -R tim:tim ~tim/.ssh

cp /root/.ssh/authorized_keys ~tim/.ssh/authorized_keys
chmod og-rwx ~tim/.ssh/authorized_keys

cat << 'EOF' >>~tim/.ssh/authorized_keys
ssh-rsa AAAA...
EOF

# Allow non-root to use ping
setcap cap_net_raw+p $(which ping)
```

Обновление и апгрейд, [установка автоматических обновлений (linode.com)](https://www.linode.com/docs/guides/how-to-configure-automated-security-updates-debian/):

```bash
sudo apt update
sudo apt upgrade

sudo apt install unattended-upgrades
# Comment 'label=Debian' to not auto-update too much
sudo vi /etc/apt/apt.conf.d/50unattended-upgrades

# Tweak some settings
cat << 'EOF' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

sudo unattended-upgrades --dry-run --debug
```

Включите SSH и разрешение в фаерволе:

```text
set system static-host-mapping host-name proteus2.lan.vanwerkhoven.org inet 172.17.10.7

set firewall name FW_TRUST2INFRA rule 212 action accept
# set firewall name FW_TRUST2INFRA rule 212 description 'accept mqtt(s)/http(s)/HA/ssh/grafana/jellyfin&emby/plex/iperf/transmission to proteus'
set firewall name FW_TRUST2INFRA rule 212 description 'accept ssh,http(s) to proteus2'
set firewall name FW_TRUST2INFRA rule 212 destination address 172.17.10.7
set firewall name FW_TRUST2INFRA rule 212 protocol tcp
# set firewall name FW_TRUST2INFRA rule 212 destination port 8883,1883,80,443,8123,22,3000,8096,32400,32469,7575,9001
set firewall name FW_TRUST2INFRA rule 212 destination port 22,80,443
```

### Усиление защиты (hardening) — TODO

С помощью [lynis (github.com)](https://github.com/CISOfy/lynis):

```bash
/usr/sbin/lynis audit system
sudo apt install apt-listbugs needrestart
```

Усильте [системные сервисы (ruderich.org)](https://ruderich.org/simon/notes/systemd-service-hardening), добавив настройки безопасности; см. также [https://unix.stackexchange.com/questions/691008/systemd-analyze-does-not-detect-changes-made-by-systemctl-edit` (stackexchange.com)](https://unix.stackexchange.com/questions/691008/systemd-analyze-does-not-detect-changes-made-by-systemctl-edit%60):

```bash
sudo systemctl edit $service
```

```ini
CapabilityBoundingSet=
KeyringMode=private
LockPersonality=yes
MemoryDenyWriteExecute=yes
NoNewPrivileges=yes
PrivateDevices=yes
PrivateMounts=yes
PrivateNetwork=yes
PrivateTmp=yes
PrivateUsers=yes
ProtectClock=true
ProtectControlGroups=yes
ProtectHome=yes
ProtectHostname=yes
ProtectKernelLogs=true
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectProc=invisible
ProtectSystem=strict
# Permit AF_UNIX for syslog(3) to help debugging. (Empty setting permits all
# families! A possible workaround would be to blacklist AF_UNIX afterwards.)
RestrictAddressFamilies=
RestrictAddressFamilies=AF_UNIX
RestrictNamespaces=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
SystemCallArchitectures=native
SystemCallFilter=
SystemCallFilter=@system-service
SystemCallFilter=~@aio @chown @clock @cpu-emulation @debug @keyring @memlock @module @mount @obsolete @privileged @raw-io @reboot @resources @setuid @swap userfaultfd mincore

# Restrict access to potential sensitive data (kernels, config, mount points,
# private keys). The paths will be created if they don't exist and they must
# not be files.
TemporaryFileSystem=/boot:ro /etc/luks:ro /etc/ssh:ro /etc/ssl/private:ro /media:ro /mnt:ro /run:ro /srv:ro /var:ro
# Permit syslog(3) messages to journald
BindReadOnlyPaths=/run/systemd/journal/dev-log
```

### Усиление SSH

Протестируйте с [ssh-audit (ssh-audit.com)](https://www.ssh-audit.com/hardening_guides.html), а также посмотрите [это очень старое руководство (stribik.technology)](https://blog.stribik.technology/2015/01/04/secure-secure-shell.html).

Перегенерируйте ключи RSA и ED25519:

```bash
sudo rm /etc/ssh/ssh_host_*
sudo ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key -N ""
sudo ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ""
echo -e "\nHostKey /etc/ssh/ssh_host_ed25519_key\nHostKey /etc/ssh/ssh_host_rsa_key" | sudo tee -a /etc/ssh/sshd_config
```

Удалите маленькие модули Диффи-Хеллмана:

```bash
awk '$5 >= 3071' /etc/ssh/moduli | sudo tee -a /etc/ssh/moduli.safe
sudo mv /etc/ssh/moduli.safe /etc/ssh/moduli
```

Ограничьте поддерживаемые алгоритмы обмена ключами, шифрования и MAC:

```bash
echo -e "# Restrict key exchange, cipher, and MAC algorithms, as per sshaudit.com\n# hardening guide.\n KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org,gss-curve25519-sha256-,diffie-hellman-group16-sha512,gss-group16-sha512-,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha256\n\nCiphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-gcm@openssh.com,aes128-ctr\n\nMACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,umac-128-etm@openssh.com\n\nHostKeyAlgorithms sk-ssh-ed25519-cert-v01@openssh.com,ssh-ed25519-cert-v01@openssh.com,rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-256-cert-v01@openssh.com,sk-ssh-ed25519@openssh.com,ssh-ed25519,rsa-sha2-512,rsa-sha2-256\n\nRequiredRSASize 3072\n\nCASignatureAlgorithms sk-ssh-ed25519@openssh.com,ssh-ed25519,rsa-sha2-512,rsa-sha2-256\n\nGSSAPIKexAlgorithms gss-curve25519-sha256-,gss-group16-sha512-\n\nHostbasedAcceptedAlgorithms sk-ssh-ed25519-cert-v01@openssh.com,ssh-ed25519-cert-v01@openssh.com,sk-ssh-ed25519@openssh.com,ssh-ed25519,rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-512,rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256\n\nPubkeyAcceptedAlgorithms sk-ssh-ed25519-cert-v01@openssh.com,ssh-ed25519-cert-v01@openssh.com,sk-ssh-ed25519@openssh.com,ssh-ed25519,rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-512,rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256\n\n" | sudo tee -a /etc/ssh/sshd_config.d/ssh-audit_hardening.conf
```

Реализуйте ограничение скорости подключений — я предпочитаю версию через sshd, чтобы концентрировать конфигурацию `sshd` только в его файле:

```bash
echo -e "\nPerSourceMaxStartups 1" | sudo tee -a /etc/ssh/sshd_config
```

Запретите вход по паролю через `/etc/ssh/sshd_config`:

```text
PasswordAuthentication no
ChallengeResponseAuthentication no
```

## Оптимизация Debian

[Отберите большие пакеты (cyberciti.biz)](https://www.cyberciti.biz/faq/find-apt-packages-occupy-the-most-space-on-debian-ubuntu/):

```bash
sudo apt install debian-goodies
dpigs -H -n 20

# Manually installed packages
apt list --manual-installed=true

sudo apt install ncdu
```

[Очистите кэш docker (stackoverflow.com)](https://stackoverflow.com/a/64917377):

```bash
sudo docker image prune -a
```

## Установка Docker

[Установите Docker (docker.com)](https://docs.docker.com/engine/install/debian/). Нужно использовать кастомный apt-репозиторий, чтобы получить последнюю версию, которая работает внутри непривилегированного LXC-контейнера ([как предложено на форумах docker (docker.com)](https://forums.docker.com/t/docker-problem-in-unpriviledged-lxc-on-debian-11-2-bullseye/121685)):

```bash
sudo apt remove docker docker-engine docker.io containerd runc docker-compose

sudo apt update

sudo apt install \
   ca-certificates \
   curl \
   gnupg \
   lsb-release

sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Подтвердите, что всё работает:

```bash
sudo docker run hello-world
```

# Миграция сервисов

## Nginx

Установите Nginx с [Lego (github.io)](https://go-acme.github.io/lego/) как ACME-менеджером сертификатов. Certbot был слишком непрозрачным для моего вкуса, поэтому я переключился на lego. К сожалению, пакет Debian [молча отключает некоторые DNS-провайдеры (debian.org)](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=968964), поэтому Debian 12 не поддерживает нужные мне DNS-провайдеры. См. также ([здесь (github.com)](https://github.com/go-acme/lego/issues/1922) и [здесь (github.com)](https://github.com/go-acme/lego/discussions/1514)). Вместо этого я вручную установил бинарник от самих Lego.

Подход:

  1. Установить nginx и lego
  2. Мигрировать конфигурацию nginx
  3. Адаптировать конфигурацию nginx под lego
  4. Определить виртуальные хосты по именам хостов
  5. Усилить nginx

### Установка nginx и lego

```bash
sudo apt install nginx
sudo apt remove lego
# Install manually instead
wget https://github.com/go-acme/lego/releases/download/v4.20.4/lego_v4.20.4_linux_amd64.tar.gz
mkdir -p ~/download/lego_v4.20.4_linux_amd64
tar xvf lego_v4.20.4_linux_amd64.tar.gz -C ~/download/lego_v4.20.4_linux_amd64
```

Запустите Lego для всех доменов один раз:

```bash
TRANSIP_ACCOUNT_NAME="twerkhov" TRANSIP_PRIVATE_KEY_PATH="/etc/ssl/private/transipkey.pem" lego --accept-tos --email tim@vanwerkhoven.org --dns transip --domains isboudewijnretired.nl --path=/etc/ssl/lego run
GANDI_API_KEY_FILE=/etc/ssl/private/gandiapikey lego --accept-tos --email tim@vanwerkhoven.org --dns gandi -d '*.vanwerkhoven.org' --path=/etc/ssl/lego renew
GANDIV5_PERSONAL_ACCESS_TOKEN_FILE=/etc/ssl/private/gandipersonalaccesstoken lego --accept-tos --email tim@vanwerkhoven.org --dns gandiv5 -d '*.vanwerkhoven.org' --path=/etc/ssl/lego  run
install -m 600 -o tim -g tim /dev/null /var/log/lego.log
```

Разрешите пользователю перезапускать nginx в /etc/sudoers:

```bash
visudo
# Allow user tim to reload nginx after certificate renewal
%tim  ALL=NOPASSWD: /sbin/service nginx reload
```

Установите cronjob, добавьте случайную задержку, чтобы быть хорошим гражданином и распределять нагрузку, [перенаправьте stderr в stdout (cyberciti.biz)](https://www.cyberciti.biz/faq/redirecting-stderr-to-stdout/) и сохраняйте в файл лога:

```bash
# Lego, supersedes certbot for letsencrypt
30 01 * * * perl -e 'sleep int(rand(43200))' && TRANSIP_ACCOUNT_NAME="twerkhov" TRANSIP_PRIVATE_KEY_PATH="/etc/ssl/private/transipkey.pem" /usr/local/bin/lego --accept-tos --email tim@vanwerkhoven.org --dns transip --domains isboudewijnretired.nl --path=/etc/ssl/lego renew >>/var/log/lego.log 2>&1 && sudo service nginx reload
35 01 * * *  perl -e 'sleep int(rand(43200))' && GANDIV5_PERSONAL_ACCESS_TOKEN_FILE=/etc/ssl/private/gandipersonalaccesstoken /usr/local/bin/lego --accept-tos --email tim@vanwerkhoven.org --dns gandiv5 -d '*.vanwerkhoven.org' --path=/etc/ssl/lego renew >>/var/log/lego.log 2>&1 && sudo service nginx reload
```

Установите детекторы смены IP, проверка каждые 5 минут для минимизации простоя:

```bash
install -m 600 -o tim -g tim /dev/null /var/log/livedns.log
install -m 600 -o tim -g tim /dev/null /var/log/livedns-error.log
sudo apt install python3-netifaces

*/5 * * * * python3 /home/tim/workers/gandi-live-dns/src/gandi-live-dns.py 1>> /var/log/livedns.log 2>> /var/log/livedns-error.log
*/5 * * * * /home/tim/workers/transip-live-dns/transip-dynamic-ip.sh >> /var/log/livedns.log 2>> /var/log/livedns-error.log
```

### Миграция конфигурации nginx

Перенесите со старого сервера на новый, просмотрите конфиги, протестируйте nginx, перезапустите:

```bash
sudo systemctl restart nginx.service
sudo nginx -t
```

Обновите доверенные прокси, например, в Home Assistant:

```text
trusted_proxies:
- 172.17.10.7
```

### Разделение внутренних/внешних виртуальных хостов — TODO

Некоторые виртуальные хосты я хочу ограничить LAN, а другие должны быть доступны из WAN. Помимо установки директив allow/deny на каждый виртуальный хост, можно получить несколько IP на одном NIC и привязать виртуальные хосты nginx к отдельным IP.

Сначала получите [несколько IP (cyberciti.biz)](https://www.cyberciti.biz/faq/bind-alias-range-of-ip-address-in-linux/) для этого хоста. Учтите, что [алиасинг IP (kernel.org)](https://www.kernel.org/doc/html/v5.8/networking/alias.html) устарел, и следует использовать инструмент `ip` вместо решений на основе `ifconfig`:

```text
# in /etc/network/interfaces:
iface eth0 inet static
        address 172.17.10.7/24
        gateway 172.17.10.1
        up   ip addr add 172.17.10.8/24 dev eth0 label eth0:0
        down ip addr del 172.17.10.8/24 dev eth0 label eth0:0

sudo systemctl restart networking
```

Затем привяжите к отдельным IP и настройте свой роутер/фаервол так, чтобы только один IP был доступен из WAN.

### Просмотр полной конфигурации

Конфигурация Nginx может быть немного непрозрачной из-за разных директив include, поэтому можно [сдампить вашу конфигурацию nginx (stackoverflow.com)](https://stackoverflow.com/questions/12832033/dump-conf-from-running-nginx-process), чтобы просмотреть её полностью:

```bash
sudo nginx -T > nginx-full.conf
```

### Усиление Nginx

Источники:

  1. [https://beaglesecurity.com/blog/article/nginx-server-security.html (beaglesecurity.com)](https://beaglesecurity.com/blog/article/nginx-server-security.html)
  2. [https://linuxize.com/post/secure-nginx-with-let-s-encrypt-on-debian-10/ (linuxize.com)](https://linuxize.com/post/secure-nginx-with-let-s-encrypt-on-debian-10/)
  3. [https://ssl-config.mozilla.org/ (mozilla.org)](https://ssl-config.mozilla.org/)
  4. [https://weakdh.org/sysadmin.html (weakdh.org)](https://weakdh.org/sysadmin.html)
  5. [https://isitquantumsafe.info/ (isitquantumsafe.info)](https://isitquantumsafe.info/)

Исправьте DH, чтобы предотвратить Logjam, используйте 4096 бит, чтобы получить 100% в [SSL Labs SSL Server Rating (github.com)](https://github.com/ssllabs/research/wiki/SSL-Server-Rating-Guide):

```bash
openssl dhparam -out ssl-dhparams-weakdh.org-4096.pem 4096
```

Дополнительно это требует подстройки сертификата Letsencrypt и отсечения 128-битных шифров, чего я не делал.

## Grafana

Можно использовать либо apt, либо docker-образ. Я выбираю apt, чтобы проще [переиспользовать мой letsencrypt-сертификат через /etc/grafana/grafana.ini (grafana.com)](https://community.grafana.com/t/grafana-https-configuration/524).

[Установка для Debian (grafana.com)](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian):

```bash
sudo apt-get install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

Добавьте репозиторий:

```bash
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```

Установите:

```bash
sudo apt-get update
sudo apt-get install grafana
```

Запустите сейчас и настройте автозапуск:

```bash
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server
sudo systemctl enable grafana-server.service
```

### Настройка letsencrypt HTTPS (1/2)

Включите HTTPS, [используя letsencrypt-сертификат (grafana.com)](https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/#generate-certificates-using-certbot):

```bash
sudo ln -s /etc/letsencrypt/live/vanwerkhoven.org/privkey.pem /etc/grafana/grafana.key
sudo ln -s /etc/letsencrypt/live/vanwerkhoven.org/fullchain.pem /etc/grafana/grafana.crt

# Allow access
sudo groupadd letsencrypt-cert
sudo usermod --append --groups letsencrypt-cert grafana

sudo chgrp -R letsencrypt-cert /etc/letsencrypt/*
sudo chmod -R g+rx /etc/letsencrypt/*
sudo chgrp -R grafana /etc/grafana/grafana.crt /etc/grafana/grafana.key
sudo chmod 400 /etc/grafana/grafana.crt /etc/grafana/grafana.key
```

### Настройка HTTPS-прокси (2/2)

Используйте nginx как прокси для Grafana, чтобы обслуживание SSL было в одном месте и наружу nginx выставлял только nginx:

```nginx
server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;

  server_name grafana.vanwerkhoven.org;

  location / {
    include snippets/nginx-server-proxy-tim.conf;
      # TvW 20241126: only allow from LAN (and thus also via VPN)
      allow 127.0.0.1;
      allow 172.17.0.0/16;
      deny all;

    #client_max_body_size 16G;
    proxy_buffering off;
    #proxy_pass http://grafana.lan.vanwerkhoven.org:3000;
    # Use fixed IP instead because DNS might not be up yet
    # resuting in error
    # "nginx: [emerg] host not found in upstream"
    #proxy_pass http://172.17.10.2:3000;
    # https://stackoverflow.com/questions/32845674/nginx-how-to-not-exit-if-host-not-found-in-upstream
    resolver 172.17.10.1 valid=30s;
    set $upstream_ha grafana.lan.vanwerkhoven.org;
    proxy_pass http://$upstream_ha:3000;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection “upgrade”;
  }
  include snippets/nginx-server-ssl-tim.conf;
  include snippets/nginx-server-cert-vanwerkhoven-tim.conf;
}
```

### Миграция конфигурации

Миграция конфигурации:

  1. Установите используемые плагины на новом сервере (нет)
  2. Остановите сервис Grafana на исходном и целевом серверах
  3. Скопируйте /var/lib/grafana/grafana.db со старого сервера на новый
  4. Проверьте /etc/grafana/grafana.ini
  5. Переподключитесь к источнику данных

```bash
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/grafana/grafana.db tim@proteus2:migrate/grafana.db-migrate
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /etc/grafana/grafana.ini tim@proteus2:migrate/grafana.ini-migrate

sudo diff grafana.ini-migrate /etc/grafana/grafana.ini # manually port changes in case new version has new syntax
sudo chown grafana:grafana grafana.db-migrate
sudo cp grafana.db-migrate /var/lib/grafana/grafana.db

sudo systemctl enable grafana-server.service
sudo systemctl start grafana-server.service
```

### Настройка уведомлений — TODO

TODO: Настроить уведомления для всего [https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rules/message-templating/ (grafana.com)](https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rules/message-templating/) [https://grafana.com/docs/grafana/latest/alerting/manage-notifications/template-notifications/using-go-templating-language/ (grafana.com)](https://grafana.com/docs/grafana/latest/alerting/manage-notifications/template-notifications/using-go-templating-language/)

## Docker

Docker должно быть легко мигрировать с одного хоста на другой. Есть две вещи для миграции:

  1. Мигрировать тома (volumes):
  2. [https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes (docker.com)](https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes)
  3. [https://stackoverflow.com/questions/45714456/how-to-migrate-docker-volume-between-hosts (stackoverflow.com)](https://stackoverflow.com/questions/45714456/how-to-migrate-docker-volume-between-hosts)
  4. Мигрировать контейнеры: можно, но не нужно(?)

### Nextcloud

Обновление: в качестве альтернативы [Sandstorm (github.com)](https://github.com/sandstorm-io/sandstorm) выглядит хорошо, с фокусом на безопасность.

Это руководство помогает [мигрировать Nextcloud (rair.dev)](https://rair.dev/nextcloud-backup-pt-1/) из Docker в Docker:

```bash
sudo docker exec -u www-data docker-app-1 php occ maintenance:mode --on
sudo docker exec -u mysql docker-db-1 mkdir -m 750 /var/lib/mysql/backup
sudo docker exec -u mysql docker-db-1 bash -c 'umask 007 && mysqldump --single-transaction -u nextcloud \
-p$MYSQL_PASSWORD nextcloud > /var/lib/mysql/backup/nextcloud-sqlbkp_`date +"%Y%m%d"`.bak'
sudo docker exec -u mysql docker-db-1 ls -lh /var/lib/mysql/backup
```

Бэкап данных:

```bash
tar cvf docker_nextcloud.tar /var/lib/docker/volumes/docker_nextcloud/_data/
cp /var/lib/docker/volumes/docker_db/_data/backup/*
```

Восстановление данных и базы:

```bash
tar xvf docker_nextcloud.tar
sudo rsync -Aax --progress var/lib/docker/volumes/docker_nextcloud/_data/data/ /var/lib/docker/volumes/docker_nextcloud/_data/data/
sudo rsync -Aax --progress var/lib/docker/volumes/docker_nextcloud/ /var/lib/docker/volumes/docker_nextcloud/

# Beware of the lack of the leading slash! This is a var subdirectory, not /var!
rm docker_nextcloud.tar && rm -r var/lib/docker/volumes
```

Альтернативно — rsync напрямую с одной машины на другую как root (опасно!):

```bash
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/docker/volumes/docker_nextcloud/ root@proteus2:/var/lib/docker/volumes/docker_nextcloud/
```

Восстановите базу из бэкапа: сначала скопируйте файл в том контейнера, затем восстановите в базу.

```bash
sudo docker exec -u mysql docker-db-1 mkdir -m 750 /var/lib/mysql/backup
sudo cp nextcloud-sqlbkp_20241127.bak /var/lib/docker/volumes/docker_db/_data/backup/

sudo docker exec docker-db-1 bash -c 'mysql -u nextcloud -p$MYSQL_PASSWORD \
-e "DROP DATABASE nextcloud"'
sudo docker exec docker-db-1 bash -c 'mysql -u nextcloud -p$MYSQL_PASSWORD \
-e "CREATE DATABASE nextcloud"'
sudo docker exec docker-db-1 bash -c 'mysql -u nextcloud -p$MYSQL_PASSWORD \
nextcloud < /var/lib/mysql/backup/nextcloud-sqlbkp_20241127.bak'
```

Завершите и восстановите nextcloud:

```bash
sudo docker exec -u www-data docker-app-1 php occ maintenance:mode --off
sudo docker exec -u www-data docker-app-1 php occ maintenance:data-fingerprint
sudo docker exec -u www-data docker-app-1 php occ files:scan --all
```

Обновите фаервол / DNS:

```text
set system static-host-mapping host-name nextcloud.vanwerkhoven.org inet 172.17.10.2
delete system static-host-mapping host-name nextcloud.lan.vanwerkhoven.org
set system static-host-mapping host-name nextcloud.lan.vanwerkhoven.org inet 172.17.10.7
```

Подтвердите, что `/var/lib/docker/volumes/docker_nextcloud/_data/config/config.php` всё ещё корректен (например, `overwrite_host`/`overwrite.cli.url`).

Убедитесь, что DNS-кэш вашего браузера обновлён. Это может занять время (30-60 мин), даже после [нажатия «clear DNS cache»](about:networking#dns), как ни удивительно.

Если ваш экземпляр Nextcloud доступен из интернета, вы можете использовать [Nextcloud Security Scan (nextcloud.com)](https://scan.nextcloud.com) и [SSL Labs Test (ssllabs.com)](https://www.ssllabs.com/ssltest/), чтобы получить рекомендации.

```bash
sudo vim /var/lib/docker/volumes/docker_nextcloud/_data/config/config.php

  'allowed_admin_ranges' => [
    '127.0.0.1/8',
    '172.17.0.0/16',
    'fd00::/8',
  ],
  'debug' => false,

sudo docker restart docker-app-1
```

### Pigallery2

Скопируйте конфигурацию pigallery (не `tmp/`, потому что я хотел перегенерировать миниатюры в более низком качестве для экономии места):

```bash
sudo mkdir -p /var/lib/pigallery2/config/
sudo mkdir -p /var/lib/pigallery2/tmp/
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/pigallery/config/ root@proteus2:/var/lib/pigallery2/config/
```

Затем запустите новый контейнер pigallery с этой конфигурацией:

```bash
sudo docker compose -f pigallery2-compose.yml up -d
```

Скопируйте базу данных (или нет?). Может иметь другую схему между источником и назначением. Попробуем всё равно. Копируйте только `sqlite.db`, не `sqlite.db-shm` и т.п.

```bash
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/docker/volumes/docker_db-data/_data/sqlite.db root@proteus2:/var/lib/docker/volumes/docker_db-data/_data/sqlite.db
```

Кажется, работает. В следующий раз обновите исходный Docker-хост перед миграцией базы, чтобы предотвратить возможное несовпадение схем.

Бонус: проверьте использование диска альбомом и при необходимости адаптируйте -> снизьте качество до

## Mosquitto

Установите демон и клиенты:

```bash
sudo apt install mosquitto mosquitto-clients
```

Конфигурация портов, пока без SSL:

```bash
cat << 'EOF' | sudo tee  /etc/mosquitto/conf.d/tim.conf
# TvW 20190818
# From https://www.digitalocean.com/community/questions/how-to-setup-a-mosquitto-mqtt-server-and-receive-data-from-owntracks
connection_messages true
log_timestamp true

# https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04
# TvW 201908
allow_anonymous false
password_file /etc/mosquitto/passwd

listener 1883
EOF

cat << 'EOF' | sudo tee /etc/mosquitto/conf.d/ssl-tim.conf.off
# Letsencrypt needs different CA https://mosquitto.org/blog/2015/12/using-lets-encrypt-certificates-with-mosquitto/
# Or not?
#cafile /etc/ssl/certs/DST_Root_CA_X3.pem
certfile /etc/letsencrypt/live/vanwerkhoven.org/cert.pem
cafile /etc/letsencrypt/live/vanwerkhoven.org/chain.pem
keyfile /etc/letsencrypt/live/vanwerkhoven.org/privkey.pem

tls_version tlsv1.2
listener 8883
EOF
```

Создайте тестового пользователя и перенесите пользователей со старого сервера:

```bash
sudo install -m 600 -o mosquitto -g tim /dev/null /etc/mosquitto/passwd
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /etc/mosquitto/passwd root@proteus2:/etc/mosquitto/passwd
```

Тестовый запуск конфигурации (sudo важен, иначе можете получить `Error: Unable to write pid file.`):

```bash
sudo /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

Если получите ошибку PID, поправьте свой `mosquitto.conf`:

```text
# TvW 20230715 Gave an error? https://github.com/eclipse/mosquitto/issues/1950
#pid_file /run/mosquitto/mosquitto.pid
pid_file /var/run/mosquitto/mosquitto.pid
```

Опционально: если работаете с mosquitto >2.0 и letsencrypt-сертификатами, обеспечьте [правильное копирование после выдачи (mosquitto.org)](https://mosquitto.org/documentation/migrating-to-2-0/#use-of-rootprivileged-user), например, [этим скриптом (github.com)](https://github.com/eclipse/mosquitto/blob/master/misc/letsencrypt/mosquitto-copy.sh). Я это не использую, так как это требует слишком многих движущихся частей. Вместо этого рассмотрите использование самоподписанного сертификата на 100 лет.

Переход в продакшн: смените DNS, перезапустите сервер.

## mqtt2influxdb

[Установка (stackexchange.com)](https://unix.stackexchange.com/questions/47695/how-to-write-startup-script-for-systemd) [как systemd-сервис (stackoverflow.com)](https://stackoverflow.com/questions/21830670/start-systemd-service-after-specific-service):

```bash
sudo apt install python3-paho-mqtt
sudo cp mqtt2influxdb.service  /etc/systemd/system/
sudo systemctl enable mqtt2influxdb.service
sudo systemctl start mqtt2influxdb.service
```

Проверьте, что всё прошло хорошо:

```bash
sudo systemctl start mqtt2influxdb.service
journalctl -u mqtt2influxdb.service
```

## InfluxDB

Хотя я предпочитаю нативные пакеты Debian, этот пакет устарел без причины, [даже по стандартам Debian (debian.org)](https://tracker.debian.org/pkg/influxdb) («The package is severely out of date with respect to the Debian Policy.»). Поэтому здесь я выбрал [установку из репозитория InfluxDB (influxdata.com)](https://docs.influxdata.com/influxdb/v1/introduction/install/). Я изменил расположение подписи на `/etc/apt/keyrings`, потому что docker и grafana уже были там.

```bash
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/keyrings/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```

Теперь установите influxdb:

```bash
sudo apt-get update
sudo apt-get install influxdb
sudo systemctl unmask influxdb.service
sudo systemctl start influxdb
```

Мигрируйте конфигурацию, перезагрузите:

```bash
scp -P 10022 tim@172.17.10.107:/etc/influxdb/influxdb.conf influxdb.conf-migrate
sudo diff /etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf-migrate
sudo diff -I '#.*' -I '  #.*' -I ' #.*' influxdb.conf /etc/influxdb/influxdb.conf
sudo service influxdb restart
journalctl -u influxdb.service
```

Чтобы работал collectd, скопируйте types.db со старой системы (альтернативно установите `collectd`). Убедитесь, что конфигурационный файл influxdb указывает на правильный путь.

```bash
scp /usr/share/collectd/types.db proteus2:
sudo mkdir -p  /usr/share/collectd
mv types.db /usr/share/collectd/types.db
```

Сделайте бэкап на старой системе, восстановите на новой:

```bash
/usr/bin/influxd backup -portable /home/tim/backup/influx_snapshot.db/$(date +%Y%m%d)-migrate
sudo systemctl stop influxdb.service
scp -r /home/tim/backup/influx_snapshot.db/$(date +%Y%m%d)-migrate proteus2:migrate/

/usr/bin/influxd restore -portable /home/tim/migrate/$(date +%Y%m%d)-migrate
```

[Добавьте пользователей в InfluxDB (influxdata.com)](https://docs.influxdata.com/influxdb/v1.8/administration/authentication_and_authorization/):

```text
influx -precision rfc3339

CREATE USER influxadmin WITH PASSWORD 'pwd' WITH ALL PRIVILEGES
CREATE USER influxwrite WITH PASSWORD 'pwd'
GRANT WRITE ON collectd TO influxwrite
GRANT WRITE ON smarthomev3 TO influxwrite
CREATE USER influxread WITH PASSWORD 'pwd'
GRANT READ ON collectd TO influxread
GRANT READ ON smarthomev3 TO influxread
CREATE USER influxreadwrite WITH PASSWORD 'pwd'
GRANT ALL ON collectd TO influxreadwrite
GRANT ALL ON smarthomev3 TO influxreadwrite
```

Протестируйте учётную запись с curl:

```bash
chmod o-r ~/.profile
cat << 'EOF' >>~/.profile
export INFLUX_USERNAME=influxadmin
export INFLUX_PASSWORD=pwd
EOF

curl -G http://localhost:8086/query --data-urlencode "q=SHOW DATABASES"
curl -G http://localhost:8086/query -u influxwrite:pwd   --data-urlencode "q=SHOW DATABASES"
influx -precision rfc3339 -database smarthomev3
```

Если InfluxDB не работает, проверьте, что путь к `types.db` корректен:

```text
Failed to connect to http://localhost:8086: Get "http://localhost:8086/ping": dial tcp [::1]:8086: connect: connection refused
Please check your connection settings and ensure 'influxd' is running.
```

Обновите DNS:

```text
set system static-host-mapping host-name mqtt.lan.vanwerkhoven.org inet 172.17.10.7
set system static-host-mapping host-name influxdb.lan.vanwerkhoven.org inet 172.17.10.7
```

Проверьте, что все метрики поступают:

  1. Из Home Assistant -> да, nibe поступает
  2. Из zigbee2mqtt -> всегда через HA
  3. Из kaifa -> через HA

Выведите из строя на старой системе:

```bash
sudo systemctl disable influxdb.service
```

## Рабочие скрипты

Сначала подчистите версии, синхронизируйте между сервером и репозиторием (я не был так аккуратен в синхронизации версий на своём сервере).

### mkwebdata

```bash
sudo install -m 660 -o tim -g www-data -d /var/www/html/smarthome-197da5
sudo install -m 660 -o tim -g www-data -d /var/www/html/smarthome-9084e7
sudo install -m 660 -o tim -g www-data -d /var/www/www
sudo install -m 660 -o tim -g www-data -d /var/www/isboudewijnretired.nl
rsync -avzAXH --exclude=".git/" /var/www/ proteus2:/var/www/

## Oops, python3-pandas is a 1,599MB / 222 package dependency... Next time try without pandas?
sudo apt install jq python3-pandas python3-influxdb
```

Тестовый запуск:

```bash
/home/tim/workers/mkwebdata/influx2web.py --outputdir /var/www/html/smarthome-9084e7/data/
/home/tim/workers/mkwebdata/mkwebdata_minutely-knaus.sh
```

### epexspot

Установите epexspot в Python venv с собственными pip-зависимостями (entsoe-py и pyyaml):

```bash
python3 -m venv epex-venv
epex-venv/bin/pip install entsoe-py pyyaml
source /home/tim/workers/epexspot/epex-venv/bin/activate && python3 /home/tim/workers/epexspot/epexspot2influx2b.py && deactivate
```

Установите crontab.

### knmi

Установите зависимости и crontab:

```bash
sudo apt install python3-netcdf4
```

```bash
# Get verified historical KNMI data daily around noon (but +-1hr), this is when data from previous day becomes available
0 12 * * * /home/tim/workers/knmi2influxdb/knmi2influxdb-wrapper_historical.sh
# Get real-time KNMI data hourly at 10min past
10 * * * * /home/tim/workers/knmi2influxdb/knmi2influxdb-wrapper_actual.sh
```

### smeter / dsmr

Два варианта на выбор:

  1. [https://dsmr-reader.readthedocs.io/en/latest/ (readthedocs.io)](https://dsmr-reader.readthedocs.io/en/latest/) + push в influxdb по mqtt или
  2. Pro: выделенный интерфейс
  3. Con: дополнительная настройка для поддержки
  4. Плагин Home Assistant + автоматизация push в mqtt и influxdb
  5. Pro: только одна настройка
  6. Con: зависит от HA

Я выбрал второе из-за меньшего числа движущихся частей.

  1. Остановить текущий cronjob smeter — OK
  2. Добавить USB в VM — OK через веб-интерфейс PVE
  3. Перезагрузить VM — OK
  4. Установить [интеграцию DSMR (home-assistant.io)](https://www.home-assistant.io/integrations/dsmr/), используя DSMR v5 — OK
  5. Автоматизировать значения в influxdb через mqtt — OK
  6. Демонтировать USB-монтирование в LXC proteus — OK
  7. Перезагрузить кластер, чтобы убедиться, что железо работает — OK

### co2signal

Cron-задания:

```bash
45 * * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3.sh NL
45 * * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3.sh DE
45 * * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3.sh BE
45 0,12 * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3-history.sh NL
45 0,12 * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3-history.sh DE
45 0,12 * * * /home/tim/workers/co2signal2influxdb/co2signal2influxdbv3-history.sh BE
```

## Автоматические резервные копии

### Grafana

Из [документации Grafana (grafana.com)](https://grafana.com/docs/grafana/latest/administration/back-up-grafana/) при использовании SQLite:

```bash
usermod -aG grafana tim
mkdir -p /home/tim/backup/grafana/
tar -cvzf /home/tim/backup/grafana/grafana_snapshot.tar.gz /var/lib/grafana/ && ln /home/tim/backup/grafana/grafana_snapshot.tar.gz /home/tim/backup/grafana/grafana_snapshot-monthly.tar.gz
```

### InfluxDB

```bash
/usr/bin/influxd backup -portable /home/tim/backup/influx/influx_snapshot && tar --remove-files -cvzf /home/tim/backup/influx/influx_snapshot.tar.gz -C /home/tim/backup/influx/ influx_snapshot && ln /home/tim/backup/influx/influx_snapshot.tar.gz /home/tim/backup/influx/influx_snapshot-monthly.tar.gz
```

```bash
cat << 'EOF' | sudo tee /etc/logrotate.d/tim-backups
/home/tim/backup/influx/influx_snapshot.tar.gz {
    su tim tim
    daily
    rotate 5
    copy
    nocompress
    ifempty
    missingok
    nocreate
    extension .tar.gz
}
/home/tim/backup/influx/influx_snapshot-monthly.tar.gz {
    su tim tim
    monthly
    rotate 5
    copy
    nocompress
    ifempty
    missingok
    extension .tar.gz
}
/home/tim/backup/grafana/grafana_snapshot.tar.gz {
    su tim tim
    daily
    rotate 5
    copy
    nocompress
    ifempty
    missingok
    nocreate
    extension .tar.gz
}
/home/tim/backup/grafana/grafana_snapshot-monthly.tar.gz {
    su tim tim
    monthly
    rotate 12
    copy
    nocompress
    ifempty
    missingok
    extension .tar.gz
}
EOF
```

### Home Assistant — TODO

Создавайте ежедневные бэкапы из HAOS, удаляйте старые. Не уверен, как запускать cron-скрипт в HA OS.

```bash
#!/bin/sh

# Register older backup by slug name
OLD_BACKUPS=$(ls /mnt/data/supervisor/backup/)

# Stop Home Assistant
ha core stop

# Create Backup
ha backups new --name "Automated backup $(date +%Y-%m-%d)"

# Start Home Assistant
ha core start

# Remove old backups
for filename in $OLD_BACKUPS; do slug=$(echo $filename | cut -f1 -d.); echo ha backups remove $slug; done
```

Опционально / в будущем: скомбинировать с `logrotate`, чтобы [создавать многоуровневые бэкапы (vanwerkhoven.org)](https://www.vanwerkhoven.org/blog/2024/using-logrotate-to-maintain-backups/).

## zigbee2mqtt

Установите как аддон Home Assistant:

  1. Как часть HA он должен бэкапиться
  2. Интерфейс доступен через HA
  3. Альтернативно, установка на Debian напрямую требует закреплённых не-apt пакетов (например, nodejs 20.0)

Для установки см. [README zigbee2mqtt (github.com)](https://github.com/zigbee2mqtt/hassio-zigbee2mqtt#installation). Для миграции см. [эту главу (github.com)](https://github.com/zigbee2mqtt/hassio-zigbee2mqtt#restoring-data-from-a-standalone-installation).

Сначала [настройте SSH-доступ к самому HAOS (home-assistant.io)](https://community.home-assistant.io/t/howto-how-to-access-the-home-assistant-os-host-itself-over-ssh/263352), что нам нужно для миграции нашей конфигурации:

```bash
# Login to VM
qm set 101 -serial0 socket
sudo qm terminal 101
# enter root / no password to enter the system
install -m 600 -o root -g root /dev/null /root/.ssh/authorized_keys
# Paste in SSH key
vi /root/.ssh/authorized_keys
systemctl start dropbear
```

Остановите zigbee2mqtt на исходном хосте:

```bash
sudo systemctl stop zigbee2mqtt.service
```

Теперь запустите сервис один раз с фейковым tty-устройством, чтобы создать `/mnt/data/supervisor/homeassistant/zigbee2mqtt/`, затем скопируйте данные. Файлы логов не переносите.

```bash
scp -P 22222 /opt/zigbee2mqtt/data/* root@homeassistant.lan.vanwerkhoven.org:/mnt/data/supervisor/homeassistant/zigbee2mqtt/
```

Теперь подключите USB-устройство к HAOS через веб-GUI proxmox, настройте и запустите zigbee2mqtt — будем надеяться, что сеть выживет :p

```yaml
server: mqtt://mqtt.lan.vanwerkhoven.org:1883
user: user
password: pass
```

Выведите из строя оригинальный сервер и запретите ему запускаться снова:

```bash
sudo systemctl disable zigbee2mqtt.service
```

## smokeping

```bash
sudo apt install smokeping fcgiwrap

# Review /etc/smokeping/config.d
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/smokeping/dns root@proteus2:/var/lib/smokeping/

# Update nginx conf
# e.g. https://github.com/vazhnov/smokeping_nginx/blob/main/simple.conf

# Tweak /usr/share/smokeping/www/smokeping.fcgi
#!/bin/sh
#exec /usr/sbin/smokeping_cgi /usr/share/doc/smokeping/config
exec /usr/share/smokeping/smokeping.cgi /etc/smokeping/config

# Migrate history
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/smokeping/dns root@proteus2:/var/lib/smokeping/
sudo --preserve-env=SSH_AUTH_SOCK rsync -Aax --progress /var/lib/smokeping/network root@proteus2:/var/lib/smokeping/
```

## Медиасервер

Варианты сервера:

  1. Plex: хороший сервер, закрытый исходный код, не умеет HW-ускорение, нельзя использовать без аккаунта
  2. Emby: хороший сервер, закрытый исходный код, не умеет HW-ускорение (текущий)
  3. Jellyfin: хороший сервер, открытый исходный код, умеет HW-ускорение -> OK

Варианты клиента

  1. Swiftfin - лагующее приложение, NOK
  2. Emby - OK-приложение, организация эпизодов иногда запутанная, не показывает имена / нет списка (текущий)
  3. Plex - вероятно, хорошо, нельзя использовать без
  4. MrMC - спартанское, но очень функциональное и быстрое, может подключаться к массе источников, разовая покупка, больше не разрабатывается -> OK
  5. Infuse - OK-приложение, но годовая платная подписка
  6. Kodi - возможно, если собрать самому, но требуется трудоёмкий процесс каждые 7 дней ИЛИ джейлбрейк (доступен только semi-tethered)

Варианты:

  1. Сервер Jellyfin + клиент MrMC
  2. Сервер Plex + клиент Plex
  3. Сервер Emby + клиент Emby

### Jellyfin с MrMC

```bash
sudo apt install extrepo
sudo extrepo enable jellyfin
```

Установите [плагин метаданных YouTube (github.com)](https://github.com/ankenyr/jellyfin-youtube-metadata-plugin):

```bash
sudo apt-get install yt-dlp
```

Следуйте инструкциям на [https://github.com/ankenyr/jellyfin-youtube-metadata-plugin (github.com)](https://github.com/ankenyr/jellyfin-youtube-metadata-plugin):

  1. Добавьте репозиторий `https://raw.githubusercontent.com/ankenyr/jellyfin-plugin-repo/master/manifest.json`
  2. Установите плагин `YoutubeMetadata`
  3. Перезапустите Jellyfin
  4. Убедитесь, что имена файлов содержат YouTube ID в квадратных скобках
  5. Добавьте как провайдера в соответствующие библиотеки
  6. Обновите метаданные

Получите автоматические субтитры, зарегистрировавшись на [OpenSubtitles.com (opensubtitles.com)](https://www.opensubtitles.com/en) (преемник .org) и настроив этот аккаунт в Jellyfin. Бесплатные аккаунты получают 20 субтитров/день.

### Plex

Установите как Docker-образ или [через apt-источник (plex.tv)](https://support.plex.tv/articles/235974187-enable-repository-updating-for-supported-linux-server-distributions/) (я выбрал apt install, потому что меньше зависимостей):

```bash
echo deb https://downloads.plex.tv/repo/deb public main | sudo tee /etc/apt/sources.list.d/plexmediaserver.list
curl https://downloads.plex.tv/plex-keys/PlexSign.key | sudo apt-key add -
sudo apt install plexmediaserver
```

[Отключите аутентификацию локальной сети (plex.tv)](https://support.plex.tv/articles/200890058-authentication-for-local-network-access/?mobile_site=true) в [расширенных настройках (plex.tv)](https://support.plex.tv/articles/201105343-advanced-hidden-server-settings/), в моём случае `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml`

См. также [пост на Reddit (reddit.com)](https://www.reddit.com/r/PleX/comments/18vi8at/setting_up_without_account/) и этот [пост на форуме Plex (plex.tv)](https://forums.plex.tv/t/new-server-claiming-requirement-for-macos/816337):

```xml
<Preferences allowedNetworks="172.17.0.0/255.255.0.0" enableLocalSecurity="False" />
```

Для первого входа войдите через localhost, используя ssh-туннель, например:

```bash
ssh -L 32400:localhost:32400 proteus
open http://localhost:32400/web
```

### Проброс хранилища

На хосте (pve) сделайте:

```bash
sudo mkdir /tank/bulk
sudo chown bulkdata:bulkdata -R /tank/bulk
sudo chmod g+w /tank/bulk

sudo chown backupmbp:backupmbp -R /tank/backups/data-tim /tank/backups/backupsmbp
sudo chmod g+w /tank/backups/data-tim /tank/backups/backupsmbp

sudo chown backupmba:backupmba -R /tank/backups/data-helene /tank/backups/backupsmba
sudo chmod g+w /tank/backups/data-helene /tank/backups/backupsmba
```

Создайте пользователя на хосте (`bulkdata:bulkdata`), UID/GID которого мы пробросим в гостя:

```bash
/sbin/adduser --home /tank/bulk --no-create-home --shell /usr/sbin/nologin --disabled-password --uid 1010 bulkdata
/sbin/adduser --home /tank/backups/mbp --no-create-home --shell /usr/sbin/nologin --disabled-password --uid 1011 backupmbp
/sbin/adduser --home /tank/backups/mba --no-create-home --shell /usr/sbin/nologin --disabled-password --uid 1012 backupmba
/sbin/usermod -aG bulkdata,backupmbp,backupmba tim
```

Настройте отображение UID/GID, чтобы пробросить пользователей 1010-1020 в те же uid на хосте (например, с помощью [этого инструмента (github.com)](https://github.com/ddimick/proxmox-lxc-idmapper)). N.B. это требуется только если вы хотите писать и с хоста, и с гостя. Если вы пишете только в (нескольких) гостях, вам нужно лишь убедиться, что пользователь/группа, пишущая из разных гостей, имеет одинаковые UID/GID.

```text
cat << 'EOF' >>/etc/pve/lxc/201.conf
# uid map: from uid 0 map 1010 uids (in the ct) to the range starting 100000 (on the host), so 0..1010 (ct) → 100000..101010 (host)
lxc.idmap = u 0 100000 1010
lxc.idmap = g 0 100000 1010
# we map 10 uids starting from uid 1010 onto 1010, so 1010 → 1010
lxc.idmap = u 1010 1010 10
lxc.idmap = g 1010 1010 10
# we map the rest of 65535 from 1020 upto 101020, so 1020..65535 → 101020..165535
lxc.idmap = u 1020 101020 64516
lxc.idmap = g 1020 101020 64516
EOF
```

Добавьте следующее в `/etc/subuid` и `/etc/subgid` (в файле уже могут быть записи, в том числе для `root`):

```bash
cat << 'EOF' >>/etc/subuid
root:1010:10
EOF
cat << 'EOF' >>/etc/subgid
root:1010:10
EOF
```

На клиенте добавьте пользователя с id 1010:

```bash
sudo groupadd -g 1010 bulkdata
sudo useradd bulkdata --uid 1010 --gid 1010 --no-create-home --shell /usr/sbin/nologin
sudo groupmod -aU jellyfin,tim,debian-transmission bulkdata
sudo groupadd -g 1011 backupmbp
sudo useradd backupmbp --uid 1011 --gid 1011 --no-create-home --shell /usr/sbin/nologin
sudo groupadd -g 1012 backupmba
sudo useradd backupmba --uid 1012 --gid 1012 --no-create-home --shell /usr/sbin/nologin

usermod -aG backupmbp,backupmba tim
```

Теперь смонтируйте собственно точки монтирования (на хосте):

```bash
sudo pct shutdown 203
sudo pct set 203 -mp0 /mnt/bulk,mp=/mnt/bulk
sudo pct set 203 -mp1 /mnt/backup/mbp,mp=/mnt/backup/mbp
sudo pct set 203 -mp2 /mnt/backup/mba,mp=/mnt/backup/mba
sudo pct set 203 -mp3 /mnt/backup/data-tim,mp=/mnt/backup/data-tim
sudo pct set 203 -mp4 /mnt/backup/data-helene,mp=/mnt/backup/data-helene
sudo pct start 203
```

## Transmission

```bash
sudo --preserve-env=SSH_AUTH_SOCK scp settings.json tim@proteus2:migrate/
```

## Ente photos

Звучит хорошо, но мне не нужно

  1. Мне всё ещё нравится nextcloud для лёгкого обмена файлами и директориями (в основном фотоальбомы, с чем Ente мог бы справиться, но и другие файлы тоже)
  2. Pigallery2 супер-прост, что мне нравится

Из [документации самостоятельного хостинга Ente (ente.io)](https://help.ente.io/self-hosting/):

```bash
git clone --depth 1 --branch photos-v0.9.58 https://github.com/ente-io/ente
mv ente ente-photos-v0.9.58
cd ente-photos-v0.9.58/server
sudo docker compose up --build

sudo apt update
sudo apt install nodejs npm
sudo npm install -g yarn // to install yarn globally

cd ente/web
git submodule update --init --recursive
yarn install
NEXT_PUBLIC_ENTE_ENDPOINT=http://localhost:8092 yarn dev
```

**********

[vyos](/tags/vyos.md)
[proxmox](/tags/proxmox.md)
[homelab](/tags/homelab.md)