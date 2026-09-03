# NixOS — установка и настройка

Источник: [NixOS — установка и настройка](https://vk.com/@linuxsovet-nixos-ustanovka-i-nastroika)

### P. S. статья не моя, оригинальный автор — Сергей Мункин, публикую с разрешения автора

  1. **Вступление и основы.**

Всем привет! Сегодня хочу поговорить об установке и настройке дистрибутива NixOS с позиции обывателя. Несколько лет назад я уже пытался познакомиться с данным дситрибутивом, очень не похожим на всё, что я использовал до него. Более или менее это прошло удачно. Сейчас, посмотрев на неприятные изменения в пакетной базе Ubuntu 20.04, понял что надо искать какую то альтернативу на будущее, для использования в качестве основной системы (нет-нет, не надо мне предлагать Рач!). Вспомнил про NixOS и решил еще раз попытать счастье, так как опыта стало немного больше чем было тогда (хотя может и сомнительное высказывание). Нашел старый ноутбучный жесткий диск на 160гб, проработавший уже достаточно приличное время (точнее ему давно пора на покой), установил его в домашний компьютер и принялся за дело.
И так, что же собственно такое этот NixOS:

> NixOS — дистрибутив Linux, созданный поверх менеджера пакетов Nix. Он использует декларативную конфигурацию и позволяет надёжно обновлять систему.

Декларативная конфигурация - это описание состояния системы в одном конфигурационном файле. Что мы опишем в файле конфигурации, то у нас и будет установлено. По моему мнению это замечательный подход к созданию операционной системы. Создав конфиг единожды, его можно просто переносить между системами и создавать полные клоны системы-источника. Ну и когда все собрано в одном файле, пользователю не нужно мотыляться по всей системе конфигурируя разные файлы. Так же в систему встроен откат до предыдущих конфигураций. Это очень удобно. Вся информация о настройках хранится в конфигурационном файле **/etc/nixos/configuration.nix**. Информация об установленном у вас железе хранится в **/etc/nixos/hardware-configuration.nix.**

**2\. Установщик пакетов.**

NixOS использует пакетный менеджер NIX, у которого достаточно много возможностей (в которых мне еще предстоит разобраться). Все пакеты ставятся в один каталог /nix/store/папка_программы и не растаскиваются по всей системе. Здесь Вы можете поставить несколько версий одного и того же пакета, не боясь что то сломать. Сама установка установка пакетов достаточно проста. К примеру нам нужно установить текстовый редактор Pluma, который входит в окружение MATE. Для этого для начала узнаем как у NixOS называется этот пакет. Идем по ссылке:
[https://search.nixos.org/packages
](https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key= "https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key=")В поиске вводим **pluma** и выбираем версию ОС. Посковая система находит нам пакет **mate.pluma** , нажимаем на него и видим версию пакета, для каких систем он собран и подсказку для его установки:

> **$ nix-env -iA nixos.mate.pluma**

Копируем в терминал и устанавливаем. Программа установится в папку **/nix/store/qxis4j1sr9q34ypwkg1pp5xz7rngyhdz-pluma-1.22.2.
** Для удаления используем следующую команду:

> **$ nix-env --uninstall pluma**

Эта команда по сути не удалит программу а отсоеденит ее от системы. Чтобы полностью удалить программу можно вырубить ее топором:

> **# rm -rf /nix/store/*pluma***

Но лучше запустить так называемый сборщик мусора:

> **$ nix-collect-garbage**

Функционал пакетного менеджера очень богат, там есть и установка программ с Github и сборка пакетов из исходников и много чего еще. Программы можно устанавливать как от обычного пользователя, так и от root. В первом случае программа будет доступна только для текущего пользователя, во втором случае для всех пользователей. **Приятный сюрприз, что пакетный менеджер NIX можно использовать даже в Ubuntu.** Для этого в Ubuntu нужно выполнить:

> **$ curl -L https://nixos.org/nix/install | sh**

Установочный скрипт создаст нужные ссылки и установит пакетный менеджер. После этого нужно перезагрузить систему и можно пользоваться. Единственное что немного непонятно при использовании его в Ubuntu, так это то, что установленные программы не отображаются в меню пользователя. Возможно понадобиться создать какие то симлинки, чтобы система их видела.

**3\. Скачивание и подготовка образа.**

Для начала нам потребуется скачать образ системы с официального сайта и записать его на флешку. Образы пристутствуют двух видов: в виде Minimal ISO image и Graphical ISO image. Первый установщик для консольной установки, второй включает в себя окружение KDE для более удобного процесса. Пусть вас не пугает что он на KDE. По аналогии с Ubuntu я так же думал что я не хочу ставить систему с окружением KDE и потому всегда брал консольный установщик, что в принципе зря. После завершения установки системы у вас не будет в системе ни одного пакета от KDE, если конечно вы сами этого не захотите, а будет ровно то, что вы опишите в конфигурации. Советую брать установщик на KDE, так как в нем есть файл с полным мануалом по установке, правда на английском языке, а так же утилита Gparted, для более удобной разметки диска. Ну и немаловажно что можно подключиться к wi-fi и почитать ответы на какие либо вопросы в интернете. Далее переходим на страницу загрузки и качаем тот образ который вы выбрали:
[https://nixos.org/download.html
](https://vk.com/away.php?to=https://nixos.org/download.html&cc_key= "https://vk.com/away.php?to=https://nixos.org/download.html&cc_key=")После скачивания, записываем образ на флешку и загружаемся с нее.

**4\. Подготовка разделов.**

Я буду описывать установку с использованием окружения KDE. Для консольной версии, вместо утилиты Gparted нужно будет использовать fdisk для создания разделов, mkfs.ext4 для их форматирования, mkswap и swapon для подключения файла подкачки.
Создадим разделы на жестком диске. Для этого открываем Gparted, удаляем существующие разделы на нашем жестком диске и создаем те разделы, которые вы обычно используете в ваших системах. Я сделал разбивку следующим образом:
**/dev/sda1 30G primary ext4 /
/dev/sda2 4G swap
/dev/sda3 120G primary ext4 /home
**Когда разделы размечены и отформатированы, здесь же в Gparted тыкнув правой кнопкой на раздел swap подключаем его.
Открываем терминал и монтируем разделы:

> **# mount /dev/sda1 /mnt**

Если вы хотите чтобы раздел /home был у вас на отдельном разделе диска то для начала создаем папку:

> **# mkdir -p /mnt/home**

И монтируем туда /home:

> **# mount /dev/sda3 /mnt/home**

Пришло время сгенерировать начальные конфигурационные файлы, для этого выполняем:

> **# nixos-generate-config --root /mnt**

Система, на основании вашей конфигурации сгенерирует два конфигурационных файла **configuration.nix** и **hardware-configuration.nix** и поместит их в папку **/mnt/etc/nixos/**. Можно было было бы на этом этапе приступить к установке, но если запустить nixos-install то система вывалит ошибку о том, что мы не указали куда нам нужно установить загрузчик. Так как нам все равно придется лезть в файл конфигурации то сразу и настроим всю систему.

**5\. Начальное конфигурирование.**

И так, после генерации конфигов у нас в папке **/mnt/etc/nixos/** лежат два файла **configuration.nix** и **hardware-configuration.nix.** **hardware-configuration.nix** нам пока не нужен, так как в нем описано наше железо. Приступим к редактированию второго файла, отвечающего за конфигурацию нашей системы **configuration.nix** :

> **# nano /mnt/etc/nixos/configuration.nix**

В начале файла мы видим закомментировнные строки отвечающие за установку загрузчика:

> # Use the GRUB 2 boot loader.
> # boot.loader.grub.enable = true;# boot.loader.grub.version = 2;# boot.loader.grub.efiSupport = true;# boot.loader.grub.efiInstallAsRemovable = true;# boot.loader.efi.efiSysMountPoint = "/boot/efi";# Define on which hard drive you want to install Grub.# boot.loader.grub.device = "/dev/sda"; # or "nodev" for efi only

Если вы так же как я используете загрузчик GRUB 2 и MBR, то раскомментируем следующие строки:

> # Use the GRUB 2 boot loader.
> # boot.loader.grub.efiSupport = true;# boot.loader.grub.efiInstallAsRemovable = true;# boot.loader.efi.efiSysMountPoint = "/boot/efi";# Define on which hard drive you want to install Grub.# or "nodev" for efi only

> **boot.loader.grub.device = "/dev/sda";**

> **boot.loader.grub.enable = true;
>  boot.loader.grub.version = 2;**

Если вы хотите использовать загрузчик system-boot на основе systemd то советую попробовать добавить эти строчки:

> # Use the systemd-boot EFI boot loader.

> **boot.loader.systemd-boot.enable = true;
>  boot.loader.efi.canTouchEfiVariables = true;
> boot.loader.grub.fsIdentifier = "provided";**

Другие варианты не пробовал, поэтому описывать их не буду. Возможно информация есть в официальном мануале, сслыку на который я приложу ниже.

Дальше в конфиге идет блок с настройками сетевых соединений, раскомментируем:

> **networking.hostName = "имя компа";**

Cтрока

> #networking.wireless.enable = true;

Как понял, включает поддержку wi-fi через wpa_supplicant, но при этом ругается на Network-Manager.
Кое где в конфигах видел что пользователи включают networkmanager, но после установки, в Gnome-Shell, у меня он и так включен и работает. Включение Network-Manager'а можно произвести так:

> **networking.networkmanager.enable = true;**

Включение L2TP (IPSec так и не завел):

> **services.xl2tpd.enable = true;
>  services.strongswan.enable = true;**

Все остальное не трогал и приступил настройкам локалей:

> # Select internationalisation properties.

> **i18n.defaultLocale = "ru_RU.UTF-8";
>  console = {
> font = "Lat2-Terminus16";
> keyMap = "us";
> };**

Думаю затруднений возникнуть не должно.

Настройки временной зоны:

> # Set your time zone.

> **time.timeZone = "Europe/Samara";**

Дальше самое интересное, настройка софта, который будет установлен во время установки системы:

> # List packages installed in system profile. To search, run:
> # $ nix search wget

> **environment.systemPackages = with pkgs; [
>  wget
> nmap
> htop
> mate.pluma
> firefox
> ];**

Просто перечисляете все программы которые хотите видеть после загрузки системы. Естественно нужно соотносить имена программ с тем, как они называются в репозиториях NixOS. Для этого опять же нужно сходить по ссылке [https://search.nixos.org/packages](https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key= "https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key=") и поискать названия пакетов или ввести в терминале:

> **$ nix search pluma**

**Но есть одно небольшое НО!** Если вы хотите включить возможность установки проприетарных пакетов, то вам нужно до этой секции добавить секцию с правилом, разрешающую их установку:

> **nixpkgs.config = {
>  allowUnfree = true;
> **# allowBroken = true;

> **};**

Теперь, в переменной **environment.systemPackages** можно перечислять проприетарные пакеты (skypeforlinux, viber и прочее).

Так же, чтобы разрешить установку проприетарных пакетов с помощью пакетного менеджера nix, после установки системы нужно добавить строку в файл **~/.config/nixpkgs/config.nix:**

> **{ allowUnfree = true; }**

Для некоторых программ возможно понадобиться включить сервис, например:

> **services.teamviewer.enable = true;**

> **services.yandex-disk.enable = true;**

> **services.cron.enable = true;**

Дальше идут настройки SSH, включаем что нужно:

> # Some programs need SUID wrappers, can be configured further or are
> # started in user sessions.# programs.mtr.enable = true;# programs.gnupg.agent = {# enable = true;# enableSSHSupport = true;# pinentryFlavor = "gnome3";# };

> # List services that you want to enable:

> # Enable the OpenSSH daemon.

> **services.openssh.enable = true;**

Файрвол, мне пока не нужен:

> # Open ports in the firewall.
> # networking.firewall.allowedTCPPorts = [ ... ];# networking.firewall.allowedUDPPorts = [ ... ];# Or disable the firewall altogether.# networking.firewall.enable = false;

Если есть принтер, то советую включить поддержку CUPS:

> # Enable CUPS to print documents.
> # services.printing.enable = true;

Звук и аппаратная поддержка pulseaudio:

> # Enable sound.

> **sound.enable = true;
>  hardware.pulseaudio.enable = true;**

xserver и раскладка для него по умолчанию:

> # Enable the X11 windowing system.
> # services.xserver.xkbOptions = "eurosign:e";

> **services.xserver.enable = true;
>  services.xserver.layout = "us";**

Поддержка тачпада:

> # Enable touchpad support.
> # services.xserver.libinput.enable = true;

Настройка окружения и менеджера входа:

> # Enable the KDE Desktop Environment.

> **services.xserver.displayManager.gdm.enable = true;
>  services.xserver.desktopManager.gnome3.enable = true;**

Доступные окружения можете посмотреть тут:

[https://search.nixos.org/options?query=services.xserver.desktopManager.&from;=0&size;=30&sort;=relevance&channel;=unstable](https://vk.com/away.php?to=https://search.nixos.org/options?query=services.xserver.desktopManager.&from=0&size=30&sort=relevance&channel=unstable&cc_key= "https://vk.com/away.php?to=https://search.nixos.org/options?query=services.xserver.desktopManager.&from=0&size=30&sort=relevance&channel=unstable&cc_key=")

Если хотите то можете использовать как менеджер входа **lightdm** или **sddm** , а вместо **gnome3** к примеру **lxqt** , **plasma5** или **xfce**.

Настройки пользователя. По умолчанию они другие, но я все таки посоветую использовать такую конструкцию:

> # Define a user account. Don't forget to set a password with ‘passwd’.
> пользовательпапка_пользователяпарольЕсли пароль здесь не задан, то после установки задаем через passwd # Включаем ‘sudo’ для пользователя.

> **};**

> **uid = 1000;
>  isNormalUser = true;
> group = "users";
> extraGroups = [ "wheel" "networkmanager" "libvirtd" "vboxusers" "dialout" "docker" ];**

> **"; #**

> **";
>  createHome = true;
> useDefaultShell = true;
> password = "**

> **= {
>  home = "/home/**

> **users.users.**

После установки системы, проверьте пароль пользователя root, возможно нужно будет установить его через **passwd**.

Ну и последнее это установленная текущая версия и проверка обновлений для нее:

> # This value determines the NixOS release from which the default
> # settings for stateful data, like file locations and database versions# on your system were taken. It‘s perfectly fine and recommended to leave# this value at the release version of the first install of this system.# Before changing this value read the documentation for this option# (e.g. man configuration.nix or on https://nixos.org/nixos/options.html). # Did you read the comment?

> **system.stateVersion = "20.03";**

Можно так же включить автоообновление системы:

> **system.autoUpgrade.enable**

> **= true;**

От себя хочу добавить:

Включение службы питания:

> **powerManagement.enable = true;**

Это как понимаю задание переменных окружения:

> **environment = {
>  shells = [
> "${pkgs.bash}/bin/bash"
> "${pkgs.fish}/bin/fish"
> ];
> variables = {
> BROWSER = pkgs.lib.mkOverride 0 "chromium";
> EDITOR = pkgs.lib.mkOverride 0 "vim";
> };**

Шрифты:

> **fonts = {
> ** # enableCoreFonts = true; # так не хочет, ругается

> **enableFontDir = true;
>  enableGhostscriptFonts = false;
> fonts = [
> pkgs.terminus_font_ttf
> pkgs.tewi-font
> pkgs.kochi-substitute-naga10
> pkgs.source-code-pro
> ];
> };**

Виртуализция:

> **virtualisation = {
>  libvirtd.enable = true;
> docker.enable = true;
> virtualbox.host.enable = true;
> };**

Zram:

> # Enable zram swapping
> почитайте о приоритетах swap# алгоритм сжатия# количество виртуальных swap# процент занимаемой памяти

> **zramSwap.memoryPercent = 50;**

> **zramSwap.numDevices = 1;
>  zramSwap.swapDevices = 1; **

> **zramSwap.algorithm = "lzo";**

> **zramSwap.enable = true;
>  zramSwap.priority = -2; # **

Монтирование /tmp в tmpfs при загрузке системы:

> **boot.tmpOnTmpfs = true;**

**6\. Установка системы.**

Ну если все настроили и уверены в правильности то можно проверить текущий конфиг на ошибки:

> **# nixos-rebuild test --show-trace**

Приступаем к установке системы:

> **# nixos-install**

Ставится довольно долго, особенно если включили в установку проприетарные пакеты. После установки система занимает порядка 6-7гб на жестком диске. Если все хорошо система напишет:

> Installation complete!

Перезагружаемся и пользуемся!

**7\. Модульность.**

NixOS модульная система.

Список всех доступных в системе модулей можно посмотреть так:

> **cat /nix/var/nix/profiles/per-user/root/channels/nixos/nixos/modules/module-list.nix**

**8\. Существующие на данный момент проблемы, пока не решенные мной:**

— Не работает IPSec;

— При установке nomachine-client не хватает каких то зависимостей;

— Не запускаются бинарные пакеты, ни из окружения, ни из терминала (как мне подсказали возможно раздел смонтирован как noexec. Fstab здесь автогенерируется, потому, что то править в нем смысла нет);

— Непонятки с переменными окружения. (.bashrc пользователя пуст);

— После удаления приложения через nix-env --uninstall и запуска nix-collect-garbage -d приложения порой все так же остаются в работе. Тестировал на удалении Pitivi, входящего в пакет окружения Gnome3. Есть вероятность что так происходит потому, что все окружение ставится как один сервис services.xserver.desktopManager.gnome3.enable**** = true;

**Вывод.**

По личным ощущениям хочу сказать так — это единственная система, которая не подтормаживает у меня на домашнем компе. И дело вовсе не в железе. Я пробовал кучу окружений и дистрибутивов, переставлял различные версии драйверов Nvidia, но даже самые легкие окружения, типа IceWM и openbox выдавали мне по 17-20 фпс, при этом совсем не нагружая проц, память и видеокарту. В NixOS для теста поставил gnome3 — так бысто он у меня нигде и никогда не работал. Даже KDE с лайв сиди самого NixOS ведет себя очень плавно. Это подтверждают и другие пользователи.

Буду рад если кому то помог. Статья будет мной дополняться, по мере изучения системы. Всем удачи в экспериментах!

**P.S. Поезные ссылки:**

[https://nixos.org/](https://vk.com/away.php?to=https://nixos.org/&cc_key= "https://vk.com/away.php?to=https://nixos.org/&cc_key=") — официальный сайт проекта.

[https://ru.wikipedia.org/wiki/NixOS](https://vk.com/away.php?to=https://ru.wikipedia.org/wiki/NixOS&cc_key= "https://vk.com/away.php?to=https://ru.wikipedia.org/wiki/NixOS&cc_key=") — Страница на Wiki.

[https://nixos.org/download.html](https://vk.com/away.php?to=https://nixos.org/download.html&cc_key= "https://vk.com/away.php?to=https://nixos.org/download.html&cc_key=") — Страница загрузки дистрибутива NixOS и пакетного менеджера nix.

[https://search.nixos.org/packages](https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key= "https://vk.com/away.php?to=https://search.nixos.org/packages&cc_key=") — Поиск пакетов (там же поиск параметров конфигов на вкладке Options).

[https://nixos.wiki/wiki/NixOS_Installation_Guide#Alternative_installation_media_instructions](https://vk.com/away.php?to=https://nixos.wiki/wiki/NixOS_Installation_Guide%23Alternative_installation_media_instructions&cc_key= "https://vk.com/away.php?to=https://nixos.wiki/wiki/NixOS_Installation_Guide#Alternative_installation_media_instructions&cc_key=") — гайд по подготовке к установке NixOS (eng).

[https://nixos.org/manual/nixos/stable/](https://vk.com/away.php?to=https://nixos.org/manual/nixos/stable/&cc_key= "https://vk.com/away.php?to=https://nixos.org/manual/nixos/stable/&cc_key=") — Официальный мануал по установке NixOS (eng).

[https://nixos.org/manual/nix/stable/](https://vk.com/away.php?to=https://nixos.org/manual/nix/stable/&cc_key= "https://vk.com/away.php?to=https://nixos.org/manual/nix/stable/&cc_key=") — Официальный мануал по пакетному менеджеру nix (eng).

[https://search.nixos.org/options](https://vk.com/away.php?to=https://search.nixos.org/options&cc_key= "https://vk.com/away.php?to=https://search.nixos.org/options&cc_key=") — Официально описание всех опций

[https://nixos.wiki/wiki/Cheatsheet](https://vk.com/away.php?to=https://nixos.wiki/wiki/Cheatsheet&cc_key= "https://vk.com/away.php?to=https://nixos.wiki/wiki/Cheatsheet&cc_key=") — Шпаргалка и грубое сравнение пакетных менеджеров Ubuntu и NixOS (eng).

[https://nixos.wiki/wiki/Configuration_Collection](https://vk.com/away.php?to=https://nixos.wiki/wiki/Configuration_Collection&cc_key= "https://vk.com/away.php?to=https://nixos.wiki/wiki/Configuration_Collection&cc_key=") — Примеры конфигураций от различных пользователей.

[https://github.com/kragniz/configuration.nix/blob/master/configuration.nix](https://vk.com/away.php?to=https://github.com/kragniz/configuration.nix/blob/master/configuration.nix&cc_key= "https://vk.com/away.php?to=https://github.com/kragniz/configuration.nix/blob/master/configuration.nix&cc_key=") — Пример конфигурации с Github.

[http://illumium.org/node/125](https://vk.com/away.php?to=http://illumium.org/node/125&cc_key= "https://vk.com/away.php?to=http://illumium.org/node/125&cc_key=") — один из русскоязычных неофициальных мануалов по установке и настройке NixOS.

[https://tech-geek.ru/nixos/](https://vk.com/away.php?to=https://tech-geek.ru/nixos/&cc_key= "https://vk.com/away.php?to=https://tech-geek.ru/nixos/&cc_key=") — еще один из русскоязычных неофициальных мануалов по установке и настройке NixOS.

1538 просмотров

**********

[nix](/tags/nix.md)
[nixos](/tags/nixos.md)
