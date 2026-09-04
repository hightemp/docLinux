# docLinux

- Ядро и внутренности Linux
  - File Descriptors Файловые дескрипторы
    - [Как проверить все открытые файлы пользователем или процессом в Linux](/articles/kak_proverit_vse_otkrytye_faily_polzovatelem_ili_protsessom_v_linux.md)
    - [Куда делись файловые дескрипторы?](/articles/kuda_delis_failovye_deskriptory.md)
    - [Файловые дескрипторы](/articles/file_descriptors.md)
  - find
    - [Поиск больших файлов в Linux/macOS](/articles/find_large_files_linuxmacos.md)
  - Git
    - [О красивых диффах в git](/articles/beautiful_git_diffs.md)
  - Inotify
    - [Inotify в bash: ловим изменения файловой системы](/articles/inotify_v_bash_lovim_izmeneniya_failovoi_sistemy.md)
  - Linux
    - Основы
      - Введение и Общие концепции
        - [Основы Linux: пользовательское пространство, пространство ядра и системные вызовы](/articles/linux_fundamentals_user_kernel_space.md)
        - [Режим сна Linux](/articles/linux_bedtime_routine.md)
      - Время и Таймеры
        - [Учёт времени и часы в Linux](/articles/linux_timekeeping_and_clocks.md)
    - Архитектура
      - ELF Файлы и Библиотеки
        - ELF Файлы
          - [Рецепты для ELFов](/articles/retsepty_dlya_elfov.md)
        - Библиотеки
          - [musl FAQ — официальный FAQ по musl libc](/articles/musl_faq_ofitsialnyy_faq_po_musl_libc_chto_delaet_c-biblioteka_v_linux_userspace.md)
      - Namespaces
        - [Глубокое погружение в Linux namespaces](/articles/glubokoe_pogruzhenie_v_linux_namespaces.md)
        - [Глубокое погружение в Linux namespaces, часть 2](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_2.md)
        - [Глубокое погружение в Linux namespaces, часть 3](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_3.md)
        - [Глубокое погружение в Linux namespaces, часть 4](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_4.md)
      - Потоки
        - [Потоки в Linux: подробное руководство](/articles/threads_in_linux_a_comprehensive_guide.md)
      - Управление памятью
        - Общие концепции
          - Адресные пространства процессов
            - ASLR
              - [ASLR в деталях](/articles/aslr_in_depth.md)
          - Виртуальная и Физическая память
            - [Что такое виртуальная память в Linux?](/articles/virtual_memory_in_linux.md)
          - Основное
            - [Управление памятью в Linux](/articles/linux_memory_management.md)
            - [Числа и байты: как работает память в Linux?](/articles/linux_memory_numbers_and_bytes.md)
        - Отладка и профилирование
          - [Шпаргалка по поиску узких мест в Linux: топ утилит на все случаи жизни](/articles/shpargalka_po_poisku_uzkikh_mest_v_linux_top_utilit_na_vse_sluchai_zhi.md)
        - Специфические возможности
          - vDSO
            - [Загадка Linux: linux-vdso.so.1](/articles/linux_mystery_linux-vdsoso1.md)
            - [Понимание linux-vDSO](/articles/understanding_linux-vdsoso1.md)
          - vDSO
            - [vdso](/articles/vdso.md)
            - [Как работает clock_gettime](/articles/how_does_clock_gettime_work.md)
    - Ввод-Вывод
      - Асинхронный ввод-вывод
        - io_uring
          - [Проблема в Linux io_uring ведет к скрытым атакам руткитов](/articles/problema_v_linux_io_uring_vedet_k_skrytym_atakam_rutkitov.md)
      - Мультиплексирование
        - epoll
          - [Epoll фундаментально сломан — часть 2](/articles/epoll_is_fundamentally_broken_2.md)
          - [epoll: API, на котором работает современный интернет](/articles/epoll_the_api_that_powers_the_modern_internet.md)
        - select
          - [select фундаментально сломан](/articles/select_is_fundamentally_broken.md)
        - Общее
          - [Асинхронный ввод-вывод в Linux: select, poll и epoll](/articles/io_multiplexing_select_vs_poll_vs_epollkqueue.md)
          - [Масштабируемое мультиплексирование событий: epoll против kqueue](/articles/scalable_event_multiplexing_epoll_vs_kqueue.md)
      - Сокеты
        - SO_REUSEPORT
          - [Когда один TCP-порт может быть поделён](/articles/kogda_odin_tcp_port_mozhet_byt_podelen.md)
          - [Увеличиваем производительность с помощью SO_REUSEPORT в NGINX 1.9.1](/articles/uvelichivaem_proizvoditelnost_s_pomoshchyu_so_reuseport_v_nginx_191.md)
          - [Балансировка TCP-соединений в ядре Linux](/articles/loadbalancing_tcp_connections_in_the_linux_kernel.md)
        - SO_REUSEPORT
          - [Linux TCP SO_REUSEPORT: использование и реализация](/articles/linux_tcp_so_reuseport_usage_and_implementation.md)
        - Общее
          - [Что такое сокет?](/articles/what_is_a_socket.md)      - Остальное
        - [Отладка блочного ввода-вывода в Linux](/articles/linux_block_io_debugging.md)

    - Пакетирование и распространение приложений
      - Flatpak
        - [Копаем глубже в Flatpak с NVIDIA](/articles/digging_further_into_flatpak_with_nvidia.md)
        - [Использование хостового NVIDIA-драйвера с Flatpak](/articles/using_host_nvidia_driver_with_flatpak_podrobnyy_razbor_rasshireniy_gl-drayverov_f.md)
    - Сетевые технологии
      - Высокопроизводительные
        - BPF eBPF
          - [BPF для самых маленьких, часть нулевая: classic BPF](/articles/bpf_dlya_samykh_malenkikh_chast_nulevaya_classic_bpf.md)
        - RDMA
          - [Infiniband](/articles/infiniband.md)
      - Общее
        - DNS
          - gaiconf
            - [/etc/gai.conf — это совсем не то, что вы думаете](/articles/etcgaiconf_it_aint_what_you_think_it_is.md)
            - [Какие правила добавить в /etc/gai.conf](/articles/finding_out_what_rules_to_add_to_etcgaiconf_prakticheskiy_razbor_nastroyki_etcgai.md)
          - Основное
            - [Resolve IP адресов в Linux: понятное и детальное описание](/articles/resolve_ip_adresov_v_linux_ponyatnoe_i_detalnoe_opisanie.md)
            - [Анатомия DNS-запроса в Linux — часть IV](/articles/anatomy_of_a_linux_dns_lookup_part_iv.md)
            - [Анатомия DNS-запроса в Linux. Часть III](/articles/anatomy_of_a_linux_dns_lookup_part_iii.md)
            - [Как работает DNS в Linux. Часть 1: от getaddrinfo до resolv.conf](/articles/kak_rabotaet_dns_v_linux_chast_1_ot_getaddrinfo_do_resolvconf.md)          - Default Address Selection
            - [RFC 3484 в Linux — выбор адресов по Ульриху Дрепперу](/articles/rfc_3484_on_linux.md)

      - Протоколы
        - TCP
          - TCP Congestion Control
            - [Внутреннее устройство управления перегрузкой TCP в Linux](/articles/linux_tcp_congestion_control_internals.md)
          - TCP Congestion Control
            - [TCP Congestion Control или Почему скорость прыгает](/articles/tcp_congestion_control_ili_pochemu_skorost_prygaet.md)
            - [Как работает TCP congestion control: Reno, Cubic, BBR простыми словами](/articles/kak_rabotaet_tcp_congestion_control_reno_cubic_bbr_prostymi_slovami.md)
          - Алгоритмы управления перегрузками
            - BBR
              - [TCP BBR: быстрый и простой способ ускорения загрузки страниц. Доклад Яндекса](/articles/tcp_bbr_bystryi_i_prostoi_sposob_uskoreniya_zagruzki_stranits_doklad_y.md)
              - [Как включить и настроить TCP BBR в Linux](/articles/how_to_enable_and_configure_tcp_bbr_on_linux.md)
          - Планировщики пакетов
            - fq
              - [FQ - Fair Queuing](/articles/fq_fair_queuing.md)
    - Системное администрирование и утилиты
      - Блокировки flock
        - [flock](/articles/flock_blokirovki_v_shell_skriptakh_russkoyazychnaya_statya_o_zashchite.md)
      - Быстрые клавиши
        - Терминал
          - [Горячие клавиши терминала Linux](/articles/goryachie_klavishi_terminala_linux.md)
      - Планировщики задач
        - cron
          - [Почему cron](/articles/pochemu_cron_samyi_opasnyi_instrument_v_linux_prakticheskii_razbor_ris.md)
        - systemd timers
          - [systemd/Timers](/articles/systemdtimers_russkoyazychnaya_stranitsa_archwiki_po_systemd_taimeram_.md)
          - [Использование таймеров systemd вместо заданий cron](/articles/ispolzovanie_taimerov_systemd_vmesto_zadanii_cron_perevod_stati_david_.md)
          - [Что такое systemd timers и как заменить ими cron для планирования задач](/articles/chto_takoe_systemd_timers_i_kak_zamenit_imi_cron_dlya_planirovaniya_za.md)
      - Права пользователя
        - ACL
          - [Linux — работа с ACL](/articles/linux_rabota_s_acl.md)
          - [Быть или не быть ACL в администрировании Linux](/articles/byt_ili_ne_byt_acl_v_administrirovanii_linux.md)
          - [Совместное использование файлов с помощью ACL](/articles/sharing_files_with_acls.md)
      - Утилиты командной строки
        - logger
          - [Команда logger: опции, ключи и примеры использования](/articles/komanda_logger_optsii_klyuchi_i_primery_ispolzovaniya_russkoyazychnaya.md)
        - ncat
          - [Ncat, Netcat, nc](/articles/ncat_netcat_nc.md)
        - nproc
          - [Введение в команду nproc в Linux](/articles/intro_to_nproc_command_in_linux.md)
      - Блокировки flock
        - [Продолжение: блокировка bash-скриптов с flock](/articles/follow_up_bash_script_locking_with_flock.md)
      - Логирование
        - syslog
          - [Руководство для начинающих по syslog в Linux](/articles/beginners_guide_to_syslogs_in_linux.md)        - Общее
          - [Системное логирование в Linux](/articles/linux_system_logging.md)

      - Утилиты командной строки
        - killall
          - [killall(1) — справочная страница Linux](/articles/killall1_linux_manual_page.md)
        - logger
          - [Команда logger в Linux: подробное руководство](/articles/master_the_linux_logger_command.md)
    - Файловая система
      - btrfs
        - [BTRFS для самых маленьких](/articles/btrfs_dlya_samykh_malenkikh.md)
      - sshfs
        - [Как с помощью SSHFS подключать удалённые файловые системы по SSH](/articles/how_to_use_sshfs_to_mount_remote_file_systems_over_ssh.md)
      - zfs
        - [ZFS: архитектура, особенности и отличия от других файловых систем](/articles/zfs_arkhitektura_osobennosti_i_otlichiya_ot_drugikh_failovykh_sistem.md)
        - [Основы ZFS: система хранения и производительность](/articles/osnovy_zfs_sistema_khraneniya_i_proizvoditelnost.md)
        - [Что такое ZFS? И почему люди от неё без ума?](/articles/chto_takoe_zfs_i_pochemu_lyudi_ot_nee_bez_uma.md)
      - Общее
        - [FHS (Filesystem Hierarchy Standard); стандарт иерархии файловой системы](/articles/fhs_filesystem_hierarchy_standard_standart_ierarkhii_failovoi_sistemy.md)
      - Специальные ФС (dev, proc)
        - dev
          - [Каталог /dev в Linux](/articles/understanding_the_dev_directory_in_linux.md)
      - Специальные ФС (dev, proc)
        - proc
          - [Изучаем файловую систему proc](/articles/izuchaem_failovuyu_sistemu_proc.md)
          - [Каталог /proc в Linux](/articles/katalog_proc_v_linux.md)
          - [Файловые системы /dev и /proc в Linux 2.4](/articles/failovye_sistemy_dev_i_proc_v_linux_24.md)
    - Что нового
      - [Linux 6.4: новые возможности ядра — что изменилось в релизе](/articles/linux_64_novye_vozmozhnosti_yadra_chto_izmenilos_v_relize.md)
      - [Linux Kernel 6.0: что нового «выросло» в ядре?](/articles/linux_kernel_60_chto_novogo_vyroslo_v_yadre.md)
      - [Релиз Linux 6.13](/articles/reliz_linux_613.md)
    - Ядро и Разработка
      - Разработка модулей и драйверов
        - [План обучения написанию драйверов устройств для Linux](/articles/roadmap_to_learning_linux_device_drivers.md)
      - Сборка ядра
        - [Собираем и запускаем минимальное ядро Linux](/articles/sobiraem_i_zapuskaem_minimalnoe_yadro_linux.md)
  - Nix
    - NixOS
      - [Nix: воспроизводимая сборка](/articles/nix_vosproizvodimaya_sborka.md)
      - [NixOS — установка и настройка](/articles/nixos_ustanovka_i_nastroika.md)
      - [Воспроизводимая среда разработки с Nix](/articles/vosproizvodimaya_sreda_razrabotki_s_nix.md)
      - [Как создать песочницу и опакетить программу в NixOS?](/articles/kak_sozdat_pesochnitsu_i_opaketit_programmu_v_nixos.md)
      - [Мои приключения с NixOS, часть 1: начало работы](/articles/moi_priklyucheniya_s_nixos_chast_1_nachalo_raboty.md)
      - [Немного о NixOS. Часть 1. Общая информация и установка](/articles/nemnogo_o_nixos_chast_1_obshchaya_informatsiya_i_ustanovka.md)
      - [Сборка пакета для Nix](/articles/sborka_paketa_dlya_nix.md)
    - NixOS
      - [Запуск и автообновление Docker-контейнеров на NixOS](/articles/run_and_auto-update_docker_containers_on_nixos.md)
    - Остальное
      - [Изолированные окружения для разработки с помощью Nix](/articles/isolated_development_environment_using_nix.md)
  - POSIX
    - Сигналы
      - [Сигналы (signal)](/articles/signaly_signal_konspekt_hse_caos_po_posix_signalam_signal_sigaction_ki.md)
    - Потоки
      - [Что такое поток?](/articles/what_is_a_thread.md)
  - RDP
    - xrdp
      - [Как установить Xrdp Server (удалённый рабочий стол) на Ubuntu 20.04](/articles/how_to_install_xrdp_on_ubuntu.md)
  - SSH
    - Fail2Ban
      - [fail2ban ssh i bruteforce attack](/articles/fail2ban_ssh_i_bruteforce_attack.md)
    - GUI-клиенты
      - [SSH Pilot - Современный менеджер SSH сессий для Linux](/articles/ssh_pilot_sovremennyi_menedzher_ssh_sessii_dlya_linux_russkoyazychnyi_.md)
    - tunnels
      - [SSH: локальная переадресация портов](/articles/ssh_local_port_forwarding.md)
    - Остальное
      - [Почему перенос SSH на порт, отличный от 22, — плохая идея](/articles/why_putting_ssh_on_another_port_than_22_is_bad_idea.md)
  - systemd
    - healthcheck
      - [Настройка самовосстанавливающихся служб с systemd](/articles/set_up_self-healing_services_with_systemd.md)
    - journald
      - [Journalctl — анализ логов Linux](/articles/journalctl_analiz_logov_linux.md)
      - [Использование journalctl для просмотра и анализа логов: подробный гайд](/articles/ispolzovanie_journalctl_dlya_prosmotra_i_analiza_logov_podrobnyi_gaid.md)
    - systemd-nspawn
      - machinectl
        - [Из дневника разработчика: автологин в machinectl](/articles/machinectl_auto_login.md)
      - Основное
        - [Systemd и контейнеры: знакомство с systemd-nspawn](/articles/systemd_i_konteinery_znakomstvo_s_systemd_nspawn.md)
      - [systemd-nspawn](/articles/systemd_nspawn_jimmyg.md)      - Остальное
        - [Запуск контейнеров systemd-nspawn с VPN-интерфейсом](/articles/running_systemd-nspawn_containers_with_a_vpn_interface.md)

    - Основное
      - [Systemd для начинающих: разбор юнитов и их функций](/articles/systemd_dlya_nachinayushchikh_razbor_yunitov_i_ikh_funktsii.md)
      - [systemd десять лет спустя. Историческая и техническая ретроспектива](/articles/systemd_desyat_let_spustya_istoricheskaya_i_tekhnicheskaya_retrospekti.md)
    - Остальное
      - [systemd Watchdog для любого сервиса](/articles/systemd_watchdog_for_any_service.md)
      - [systemd для администраторов, часть XXI: интеграция с контейнерами](/articles/systemd_for_administrators_part_xxi.md)
  - VyOS
    - Основное
      - [VyOS](/articles/vyos.md)
    - Остальное
      - [VPN-туннель между маршрутизаторами Cisco и VyOS с использованием VTI](/articles/vpn_tunnel_between_cisco_and_vyos_routers_using_vtis.md)
      - [VyOS OpenSource Router](/articles/vyos_opensource_router.md)
      - [Программная маршрутизация с VyOS](/articles/programmnaya_marshrutizatsiya_s_vyos.md)
      - [Программная маршрутизация с VyOS в условиях санкций](/articles/programmnaya_marshrutizatsiya_s_vyos_v_usloviyakh_sanktsii.md)
      - [Создание отказоустойчивой ИТ инфраструктуры. Часть 3. Организация маршрутизации на роутерах VyOS](/articles/sozdanie_otkazoustoichivoi_it_infrastruktury_chast_3_organizatsiya_mar.md)
    - [Rolling-релизы VyOS](/articles/vyos_rolling_release.md)
  - ZRAM
    - [Включаем zRAM в Linux для лучшей производительности системы](/articles/enable_zram_on_linux_for_better_system_performance.md)
    - [Как использовать ZRAM в Ubuntu 24.04](/articles/how_to_use_zram_on_ubuntu_2404.md)
    - [Сжатие RAM в Linux](/articles/ram_compression_on_linux.md)
    - [Сжатие памяти](/articles/memory_compression.md)
  - Аудит
    - auditd
      - [auditd](/articles/auditd.md)
      - [Настройка аудита системы Linux с помощью auditd](/articles/auditd_configure_linux_system_auditing.md)
    - etckeeper
      - [Etckeeper: Git-история для /etc и быстрый аудит изменений конфигурации](/articles/etckeeper_git_istoriya_dlya_etc_i_bystryi_audit_izmenenii_konfiguratsi.md)
      - [Власть над конфигурацией. Etckeeper и Git](/articles/vlast_nad_konfiguratsiei_etckeeper_i_git_prakticheskaya_statya_po_etck.md)
      - [Упрощаем администрирование с etckeeper. Настройка контроля версий конфигов в /etc](/articles/uproshchaem_administrirovanie_s_etckeeper_nastroika_kontrolya_versii_k.md)
  - Восстановление данных
    - [Утилиты для восстановления потерянных данных в Linux](/articles/utility_dlya_vosstanovleniya_poteryannykh_dannykh_v_linux.md)
  - ГОСТ
    - [v1.24_ЕСИА и ГОСТ Р 34.10-2012 сертификаты](/articles/v124_esia_i_gost_r_3410_2012_sertifikaty.md)
  - Диски
    - [[Пошагово] Клонирование диска Clonezilla с большего на меньший](/articles/poshagovo_klonirovanie_diska_clonezilla_s_bolshego_na_menshii.md)
  - Подборки
    - [Руководство по мониторингу системы в Linux: top, htop, btop и glances](/articles/a_guide_to_linux_system_monitoring_top_htop_btop_and_glances.md)
  - Привилегии и capabilities
    - setcap и getcap
      - [Capabilities (Русский)](/articles/capabilities_russkii.md)
      - [setcap](/articles/setcap.md)
      - [Замена setuid-бита на capabilities для системных программ в Linux](/articles/zamena_setuid_bita_na_capabilities_dlya_sistemnykh_programm_v_linux.md)
      - [Лишение пользователя root привилегий](/articles/lishenie_polzovatelya_root_privilegii.md)
    - Остальное
      - [В двух словах о привилегиях Linux (capabilities)](/articles/v_dvukh_slovakh_o_privilegiyakh_linux_capabilities.md)
    - capsh
      - [Команда capsh](/articles/capsh_command.md)
  - Сеть
    - Количество соединений
      - [Что ограничивает максимальное число соединений на Linux-сервере?](/articles/what_limits_max_connections_on_linux_server.md)
  - Системы мониторинга
    - Zabbix
      - [Развертывание Zabbix 4.4 с nginx, php-fpm и MySQL Percona в Docker](/articles/razvertyvanie_zabbix_44_s_nginx_php_fpm_i_mysql_percona_v_docker.md)
  - Служба доменных имен
    - resolv.conf
      - [Resolv.conf](/articles/resolvconf.md)
      - [Взаимоотношения dhcpclient и resolv.conf'а в Linux](/articles/vzaimootnosheniya_dhcpclient_i_resolvconfa_v_linux.md)
    - Основное
      - [Служба доменных имен (DNS)](/articles/sluzhba_domennykh_imen_dns.md)
  - Утилиты
    - proxychains
  - rsync
    - [rsync, статья 2: окружение (2022)](/articles/rsync_article_2_surroundings_2022.md)
      - [Настройка proxychains](/articles/nastroika_proxychains.md)
    - rsync
      - [rsync, статья 3: как работает rsync? (2022)](/articles/rsync_article_3_how_does_rsync_work_2022.md)
  - Файрволы
    - ufw
      - [Как настроить файрвол с UFW в Ubuntu](/articles/kak_nastroit_fairvol_s_ufw_v_ubuntu.md)
  - Остальное
    - [Linux-телефоны сейчас важнее, чем когда-либо](/articles/linux_telefony_seichas_vazhnee_chem_kogda_libo.md)
    - [Как вывести список файлов каталога с 8 миллионами файлов (но не с помощью ls)](/articles/you_can_list_a_directory_containing_8_million_files_but_not_with_ls.md)
    - [Мой первый контейнер без Docker](/articles/moi_pervyi_konteiner_bez_docker.md)

- Системное администрирование
  - Загрузка и восстановление
    - [GRUB2 конфигурация](/articles/grub2_configuration.md)
    - [6 шагов загрузки Linux на пальцах](/articles/linux_boot_in_6_steps.md)
    - [Почему Linux допускает "init=/bin/bash"?](/articles/linux_init_bin_bash.md)
    - [Восстановление пароля root](/articles/root_password_recovery.md)
    - [Как сбросить забытый пароль root на серверах CentOS 7](/articles/reset_root_password_centos_7.md)
    - [Быстрая перезагрузка Linux на примере CentOS](/articles/fast_linux_reboot_with_kexec.md)
  - Службы systemd
    - [Systemd за пять минут](/articles/systemd_in_five_minutes.md)
    - [Как создать сервисный модуль systemd в Linux](/articles/create_systemd_service_unit.md)
    - [Создание службы Linux с помощью systemd](/articles/create_linux_service_with_systemd.md)
    - [Как написать systemd unit-файл для автозагрузки своего сервиса](/articles/systemd_service_autostart_unit.md)
    - [Как настроить службу systemd для периодического перезапуска?](/articles/systemd_periodic_service_restart.md)
    - [Перезапуск Systemd = всегда не соблюдается](/articles/systemd_restart_always_behavior.md)
  - Пакеты и репозитории
    - [Руководство по упаковке RPM](/articles/rpm_packaging_guide.md)
    - [Сборка RPM - быстрый старт](/articles/rpm_build_quick_start.md)
    - [Создание собственных RPM репозитариев](/articles/create_rpm_repositories.md)
    - [Пакеты Linux по умолчанию](/articles/default_linux_packages.md)
    - [Ubuntu Make — разработчику в помощь](/articles/ubuntu_make_for_developers.md)
  - Рабочее окружение
    - [Как проверить версию плазмы?](/articles/check_kde_plasma_version.md)
    - [IT пейзаж для сисадминов](/articles/sysadmin_it_landscape.md)
- Хранилище и файловая система
  - Диски и монтирование
    - [Изменение размера root lvm раздела](/articles/resize_root_lvm_partition.md)
    - [mount - примеры](/articles/mount_examples.md)
  - Иерархия и размещение данных
    - [Значение каталогов в Unix и Unix-подобных системах](/articles/unix_directory_structure.md)
    - [Стандартные каталоги Linux](/articles/linux_standard_directories.md)
    - [Стандарт иерархии файловой системы](/articles/filesystem_hierarchy_standard.md)
    - [Где сохранить файлы конфигурации / данных в GNU / Linux?](/articles/linux_configuration_and_data_locations.md)
    - [Где хранить данные приложения (не для пользователя) в Linux](/articles/linux_application_data_location.md)
    - [Можно ли использовать косую черту в имени файла?](/articles/slash_in_filename.md)
    - [Как мне создать имя файла с недопустимыми символами, такими как:?>?](/articles/filenames_with_invalid_characters.md)
  - Файлы и архивы
    - [18 примеров команды tar в Linux](/articles/tar_command_18_examples.md)
    - [Хаки при работе с большим числом мелких файлов](/articles/handling_many_small_files.md)
    - [Как оптимизировать и сжать JPEG или PNG изображений в Linux командная строка](/articles/optimize_jpeg_png_cli.md)
- Процессы и системные ресурсы
  - Процессы
    - [Как просмотреть активные процессы в Linux](/articles/view_active_linux_processes.md)
    - [htop объясненный](/articles/htop_explained.md)
    - [Форкинг против потоков](/articles/forking_vs_threads.md)
  - Управление ресурсами
    - [Ограничение использования процессора с помощью nice, cpulimit и cgroups](/articles/limit_cpu_with_nice_cpulimit_cgroups.md)
    - [Как ограничить использование процессора и памяти с помощью групп в Debian/Ubuntu](/articles/cgroups_resource_limits_debian_ubuntu.md)
    - [Механизмы контейнеризации: cgroups](/articles/containerization_with_cgroups.md)
    - [Перенос процесса в контрольную группу](/articles/move_process_to_cgroup.md)
    - [Борьба за ресурсы](/articles/linux_resource_contention.md)
  - Память, swap и OOM
    - [OOM killer](/articles/oom_killer.md)
    - [Linux OOM killer - выживание](/articles/linux_oom_killer_survival.md)
    - [Заставить «OOM killer'а» игнорировать процесс](/articles/protect_process_from_oom_killer.md)
    - [Демон подкачки ядра (kswapd)](/articles/kswapd_kernel_swap_daemon.md)
    - [Как очистить своп при наличии свободной оперативной памяти?](/articles/clear_swap_with_free_memory.md)
    - [Файл подкачки, ограничения памяти и cgroups](/articles/swap_memory_limits_cgroups.md)
- Диагностика и наблюдаемость
  - Логи и аудит
    - [Логирование вывода консоли](/articles/console_output_logging.md)
    - [Лог файлы Linux по порядку](/articles/linux_log_files_overview.md)
    - [ЧТЕНИЕ И НАСТРОЙКА ЛОГОВ LINUX В UBUNTU И CENTOS](/articles/linux_log_configuration_ubuntu_centos.md)
    - [man logger](/articles/logger_man_page.md)
    - [Как использовать logger в Linux](/articles/linux_logger_usage.md)
    - [Логгируем все команды на сервере](/articles/log_all_server_commands.md)
    - [Аудит системных событий в Linux](/articles/linux_system_event_audit.md)
  - Трассировка и профилирование
    - [Как strace подключается к уже запущенному процессу?](/articles/strace_attach_to_running_process.md)
    - [Есть ли способ использовать strace для отслеживания различных частей командного конвейера?](/articles/strace_command_pipelines.md)
    - [Производительность Linux](/articles/linux_performance.md)
    - [Механизмы профилирования Linux](/articles/linux_profiling_mechanisms.md)
    - [Профилирование кода на C/C++ в Linux и FreeBSD](/articles/c_cpp_profiling_linux_freebsd.md)
    - [Как получить общее использование ЦП приложения из /proc/pid/stat?](/articles/process_cpu_usage_from_proc_stat.md)
    - [Как рассчитывается время и процент использования ЦП Linux](/articles/linux_cpu_time_and_usage_calculation.md)
  - Терминальные сессии
    - [Как использовать команду «Script» для записи терминальной сессии Linux](/articles/record_terminal_session_with_script.md)
    - [Screen](/articles/screen.md)
- Командная строка и разработка
  - Bash-скрипты
    - [Bash-скрипты](/articles/bash_scripts.md)
    - [Шпаргалка по Bash-скриптингу](/articles/bash_scripting_cheat_sheet.md)
    - [Условия в скриптах bash (условные операторы)](/articles/bash_conditional_operators.md)
    - [Операции сравнения в bash](/articles/bash_comparison_operators.md)
    - [Взаимодействие bash-скриптов с пользователем](/articles/bash_user_interaction.md)
    - [Взаимодействие bash-скриптов с пользователем. Часть 2](/articles/bash_user_interaction_part_2.md)
    - [Перенаправления](/articles/shell_redirections.md)
  - Утилиты командной строки
    - [Примеры sed](/articles/sed_examples.md)
  - Разработка ПО
    - [Отступ исходного кода](/articles/source_code_indentation.md)
    - [БИБЛИОТЕКИ LINUX](/articles/linux_libraries.md)
- Контейнеры и виртуализация
  - Dockerfile и образы
    - [КАК РАБОТАТЬ С DOCKERFILE?](/articles/dockerfile_guide.md)
    - [ENTRYPOINT vs CMD: назад к основам](/articles/entrypoint_vs_cmd.md)
    - [Создание собственных образов](/articles/docker_custom_images.md)
    - [Создание базового изображения](/articles/docker_base_image.md)
    - [Dockerfile и коммуникация между контейнерами](/articles/dockerfile_container_communication.md)
    - [Java и Docker: это должен знать каждый](/articles/java_and_docker.md)
  - Администрирование Docker
    - [Полное практическое руководство по Docker: с нуля до кластера на AWS](/articles/docker_practical_guide.md)
    - [Автоматически запускать контейнеры](/articles/docker_container_autostart.md)
    - [Ограничение ресурсов контейнера](/articles/docker_container_resource_limits.md)
    - [Как смонтировать каталог хоста в Docker-контейнере](/articles/docker_bind_mount_host_directory.md)
    - [Как переместить докер по умолчанию /var/lib/docker в другой каталог в Ubuntu / Debian Linux](/articles/move_docker_data_directory.md)
  - Виртуализация
    - [Вложенная виртуализация](/articles/nested_virtualization.md)
    - [Установка последней версии Virtualbox с помощью PPA на Ubuntu](/articles/install_virtualbox_ppa_ubuntu.md)
    - [vagrant: добавить еще диск](/articles/vagrant_add_disk.md)
- Сети
  - Беспроводные сети
    - [DFS (динамический выбор частоты)](/articles/dfs_dynamic_frequency_selection.md)
  - TCP/IP и порты
    - [Приложения TCP/IP на примерах](/articles/tcp_ip_applications_examples.md)
    - [Привязка Портов](/articles/port_binding.md)
    - [Могут ли два приложения прослушивать один и тот же порт?](/articles/multiple_apps_same_port.md)
    - [И еще о специальном файле устройства /dev/tcp (TCP/IP), встроенном в bash](/articles/bash_dev_tcp.md)
    - [Как открыть TCP-/UDP-сокет средствами командной оболочки bash](/articles/bash_tcp_udp_sockets.md)
    - [Как мне разрешить имя хоста в IP-адрес в скрипте Bash?](/articles/resolve_hostname_in_bash.md)
  - SSH и прокси
    - [Прокси через SSH-туннель](/articles/ssh_tunnel_proxy.md)
    - [Как надежно поддерживать открытый туннель SSH?](/articles/persistent_ssh_tunnel.md)
    - [github ssh proxy](/articles/github_ssh_proxy.md)
- Безопасность и доступ
  - Аутентификация и авторизация
    - [Основы и настройка PAM](/articles/pam_configuration.md)
    - [Начала PAM.](/articles/pam_introduction.md)
    - [AAA](/articles/aaa.md)
  - Защита системы
    - [Двенадцать советов по повышению безопасности Linux](/articles/linux_security_tips.md)
    - [TCP SACK PANIC - Уязвимости ядра - CVE-2019-11477, CVE-2019-11478 и CVE-2019-11479](/articles/tcp_sack_panic_vulnerabilities.md)
- Базы данных
  - Основы
    - [Реляционная база данных](/articles/relational_database.md)
  - MySQL
    - [Mysqld_multi, программа для управления множеством серверов MySQL](/articles/mysqld_multi_management.md)
    - [mysqld_multi: как запустить несколько экземпляров MySQL](/articles/mysqld_multi_instances.md)
    - [Можно ли ограничить ресурсы MySQL, такие как память и процессор, на пользователя?](/articles/mysql_user_resource_limits.md)
    - [Оптимизация настроек Mysql с помощью Mysqltuner](/articles/mysql_optimization_with_mysqltuner.md)

---
[LVM](/tags/lvm.md)
[root](/tags/root.md)
[bash](/tags/bash.md)
[CentOS](/tags/centos.md)
[OOM killer](/tags/oom_killer.md)
[cgroups](/tags/cgroups.md)
[cpulimit](/tags/cpulimit.md)
[kswapd](/tags/kswapd.md)
[mount](/tags/mount.md)
[nice](/tags/nice.md)
[rpm](/tags/rpm.md)
[swap](/tags/swap.md)
[репозиторий](/tags/repository.md)
[файловая система](/tags/filesystem.md)
[логи](/tags/logs.md)
[lnav](/tags/lnav.md)
[syslog](/tags/syslog.md)
[tar](/tags/tar.md)
[архивирование](/tags/archiving.md)
[auditd](/tags/auditd.md)
[Ubuntu](/tags/ubuntu.md)
[аудит](/tags/audit.md)
[strace](/tags/strace.md)
[perf](/tags/perf.md)
[kprobes](/tags/kprobes.md)
[kernel tracepoints](/tags/kernel_tracepoints.md)
[профилирование](/tags/profiling.md)
[logger](/tags/logger.md)
[rsyslog](/tags/rsyslog.md)
[service](/tags/service.md)
[systemd](/tags/systemd.md)
[Debian](/tags/debian.md)
[MySQL](/tags/mysql.md)
[cpu](/tags/cpu.md)
[dialog](/tags/dialog.md)
[fork](/tags/fork.md)
[grub](/tags/grub.md)
[mysqld_multi](/tags/mysqld_multi.md)
[mysqltuner](/tags/mysqltuner.md)
[proc](/tags/proc.md)
[sed](/tags/sed.md)
[select](/tags/select.md)
[tcp](/tags/tcp.md)
[thread](/tags/thread.md)
[tput](/tags/tput.md)
[udp](/tags/udp.md)
[vagrant](/tags/vagrant.md)
[vim](/tags/vim.md)
[сеть](/tags/networking.md)
[docker](/tags/docker.md)
[Dockerfile](/tags/dockerfile.md)
[BIOS](/tags/bios.md)
[init](/tags/init.md)
[загрузка](/tags/boot.md)
[htop](/tags/htop.md)
[virtualbox](/tags/virtualbox.md)
[виртуализация](/tags/virtualization.md)
[память](/tags/memory.md)
[ядро](/tags/kernel.md)
[базы данных](/tags/databases.md)
[процессы](/tags/processes.md)
[ps](/tags/ps.md)
[top](/tags/top.md)
[flame graph](/tags/flame_graph.md)
[трассировка](/tags/tracing.md)
[RedHat](/tags/red_hat.md)
[Cygwin](/tags/cygwin.md)
[PAM](/tags/pam.md)
[уязвимости](/tags/vulnerabilities.md)
[KDE](/tags/kde.md)
[systemctl](/tags/systemctl.md)
[unit](/tags/unit.md)
[НЕ ПЕРЕВЕДЕНО](/tags/untranslated.md)
[script](/tags/script.md)
[библиотеки](/tags/libraries.md)
[lib](/tags/lib.md)
[proxy](/tags/proxy.md)
[ssh](/tags/ssh.md)
[ncat](/tags/ncat.md)
[AAA](/tags/aaa.md)
[jpegoptim](/tags/jpegoptim.md)
[OptiPNG](/tags/optipng.md)
[epel](/tags/epel.md)
[RHEL](/tags/rhel.md)
[Fedora](/tags/fedora.md)
[sudo](/tags/sudo.md)
[sealert](/tags/sealert.md)
[aureport](/tags/aureport.md)
[chattr](/tags/chattr.md)
[firewalld](/tags/firewalld.md)
[iptables](/tags/iptables.md)
[tripwire](/tags/tripwire.md)
[Java](/tags/java.md)
[sysctl](/tags/sysctl.md)
[screen](/tags/screen.md)
[kexec](/tags/kexec.md)
[github](/tags/github.md)
[git](/tags/git.md)
[getent](/tags/getent.md)
[dig](/tags/dig.md)
[Flatpak](/tags/flatpak.md)
