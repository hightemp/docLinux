# docLinux

- Основы Linux и ядро
  - Системные интерфейсы
    - Файловые дескрипторы
      - [Как проверить все открытые файлы пользователем или процессом в Linux](/articles/kak_proverit_vse_otkrytye_faily_polzovatelem_ili_protsessom_v_linux.md)
      - [Куда делись файловые дескрипторы?](/articles/kuda_delis_failovye_deskriptory.md)
      - [Файловые дескрипторы](/articles/file_descriptors.md)
      - [dup, dup2, dup3 — дублирование файлового дескриптора](/articles/dup_dup2_dup3_-_duplicate_a_file_descriptor.md)
    - inotify
      - [Inotify в bash: ловим изменения файловой системы](/articles/inotify_v_bash_lovim_izmeneniya_failovoi_sistemy.md)
    - Время и таймеры
      - [Учёт времени и часы в Linux](/articles/linux_timekeeping_and_clocks.md)
    - vDSO
      - [vdso(7) — справочная страница Linux](/articles/vdso7_linux_manual_page.md)
      - [Загадка Linux: linux-vdso.so.1](/articles/linux_mystery_linux-vdsoso1.md)
      - [Понимание linux-vDSO](/articles/understanding_linux-vdsoso1.md)
      - [vdso](/articles/vdso.md)
      - [Как работает clock_gettime](/articles/how_does_clock_gettime_work.md)
    - Системные вызовы
      - [eventfd(2) — man-страница Linux](/articles/eventfd2_linux_manual_page.md)
      - [Создание процессов и потоков в Linux: архитектура системных вызовов](/articles/linux_process_and_thread_creation_system_call_architecture.md)
  - Основы Linux
    - [Основы Linux: пользовательское пространство, пространство ядра и системные вызовы](/articles/linux_fundamentals_user_kernel_space.md)
    - [Режим сна Linux](/articles/linux_bedtime_routine.md)
  - Архитектура ядра
    - Namespaces
      - [Глубокое погружение в Linux namespaces](/articles/glubokoe_pogruzhenie_v_linux_namespaces.md)
      - [Глубокое погружение в Linux namespaces, часть 2](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_2.md)
      - [Глубокое погружение в Linux namespaces, часть 3](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_3.md)
      - [Глубокое погружение в Linux namespaces, часть 4](/articles/glubokoe_pogruzhenie_v_linux_namespaces_chast_4.md)
  - Ввод-вывод
    - io_uring
      - [io_uring против epoll: что лучше в сетевом программировании?](/articles/io_uring_vs_epoll_which_is_better_in_network_programming.md)
      - [io_uring снова здесь — на этот раз в виде руткита](/articles/io_uring_is_back_this_time_as_a_rootkit.md)
      - [Революция в бэкенде, или Почему io_uring так важен](/articles/the_backend_revolution_or_why_io_uring_is_so_important.md)
      - [Стремительный рост io_uring](/articles/the_rapid_growth_of_io_uring.md)
      - [Что такое io_uring? Высокопроизводительный ввод-вывод в Linux](/articles/what_is_io_uring_highperformance_io_in_linux.md)
      - [Проблема в Linux io_uring ведет к скрытым атакам руткитов](/articles/problema_v_linux_io_uring_vedet_k_skrytym_atakam_rutkitov.md)
    - Мультиплексирование
      - epoll
        - [Epoll принципиально сломан 1/2](/articles/epoll_is_fundamentally_broken_12.md)
        - [Epoll фундаментально сломан — часть 2](/articles/epoll_is_fundamentally_broken_2.md)
        - [Что такое epoll](/articles/what_is_epoll.md)
        - [Метод безумия epoll](/articles/the_method_to_epolls_madness.md)
        - [epoll(7) — справочная страница Linux](/articles/epoll7_linux_manual_page.md)
        - [epoll: API, на котором работает современный интернет](/articles/epoll_the_api_that_powers_the_modern_internet.md)
      - select
        - [select фундаментально сломан](/articles/select_is_fundamentally_broken.md)
      - Обзор
        - [Асинхронный ввод-вывод в Linux: select, poll и epoll](/articles/io_multiplexing_select_vs_poll_vs_epollkqueue.md)
        - [Масштабируемое мультиплексирование событий: epoll против kqueue](/articles/scalable_event_multiplexing_epoll_vs_kqueue.md)
  - Релизы ядра
    - [Linux 6.4: новые возможности ядра — что изменилось в релизе](/articles/linux_64_novye_vozmozhnosti_yadra_chto_izmenilos_v_relize.md)
    - [Linux Kernel 6.0: что нового «выросло» в ядре?](/articles/linux_kernel_60_chto_novogo_vyroslo_v_yadre.md)
    - [Релиз Linux 6.13](/articles/reliz_linux_613.md)
    - [Релиз Linux 7.2](/articles/reliz_linux_72.md)
  - Разработка ядра
    - Модули и драйверы
      - [Внутренности ядра и разработка модулей ядра в Fedora Linux](/articles/kernel_internals_and_kernel_module_development_in_fedora_linux.md)
      - [План обучения написанию драйверов устройств для Linux](/articles/roadmap_to_learning_linux_device_drivers.md)
    - Сборка ядра
      - [Собираем и запускаем минимальное ядро Linux](/articles/sobiraem_i_zapuskaem_minimalnoe_yadro_linux.md)
    - Планировщик CPU
      - [Cache Aware Scheduling: анонс v3-серии из 21 патча](/articles/cache_aware_scheduling_anons_v3_serii_iz_21_patcha_dlya_cache_aware_balansirovki_n.md)
      - [Характеризация Cache-Aware Scheduling в Linux](/articles/characterization_of_cache_aware_scheduling_on_linux_issledovanie_eevdf_i_ebpf_pl.md)
    - Практикумы
      - [Linux Kernel Labs: сетевая подсистема](/articles/linux_kernel_labs_networking_lab.md)
  - Сопровождение ядра
    - Livepatch
      - [Livepatch: runtime-патчинг функций ядра без перезагрузки](/articles/livepatch_ofitsialnaya_dokumentatsiya_yadra_linux_o_runtime-patchinge_funktsiy_bez_reb.md)
- Процессы, память и IPC
  - Управление ресурсами
    - [Linux cgroup с нуля](/articles/linux_cgroup_from_first_principles.md)
    - [Практика cgroup v2](/articles/practicing_cgroup_v2.md)
    - [Ограничение использования процессора с помощью nice, cpulimit и cgroups](/articles/limit_cpu_with_nice_cpulimit_cgroups.md)
    - [Как ограничить использование процессора и памяти с помощью групп в Debian/Ubuntu](/articles/cgroups_resource_limits_debian_ubuntu.md)
    - [Механизмы контейнеризации: cgroups](/articles/containerization_with_cgroups.md)
    - [Перенос процесса в контрольную группу](/articles/move_process_to_cgroup.md)
    - [Борьба за ресурсы](/articles/linux_resource_contention.md)
  - Потоки
    - Linux
      - [Как работают потоки и конкурентность в системах Linux](/articles/how_threads_and_concurrency_work_in_linux_systems.md)
      - [Потоки в Linux: подробное руководство](/articles/threads_in_linux_a_comprehensive_guide.md)
      - [Разница между процессом и потоком в Linux](/articles/difference_between_process_and_thread_in_linux.md)
    - POSIX
      - [Что такое поток?](/articles/what_is_a_thread.md)
      - [Библиотеки потоков POSIX (pthread)](/articles/posix_thread_pthread_libraries.md)
      - [Многопоточное программирование: учебник по POSIX pthreads](/articles/multithreaded_programming_posix_pthreads_tutorial.md)
      - [Потоки POSIX](/articles/posix_threads.md)
  - Управление памятью
    - [Как работает блок управления памятью (MMU)](/articles/how_does_the_memory_management_unit_mmu_work.md)
    - [Understanding the Linux Virtual Memory Manager — Глава 2: Описание физической памяти](/articles/understanding_the_linux_virtual_memory_manager_chapter_2_describing_ph.md)
    - [Что такое виртуальная память в Linux?](/articles/virtual_memory_in_linux.md)
    - [Управление памятью в Linux](/articles/linux_memory_management.md)
    - [Числа и байты: как работает память в Linux?](/articles/linux_memory_numbers_and_bytes.md)
  - Сигналы
    - [Сигналы (signal)](/articles/signaly_signal_konspekt_hse_caos_po_posix_signalam_signal_sigaction_ki.md)
  - ZRAM
    - [Включаем zRAM в Linux для лучшей производительности системы](/articles/enable_zram_on_linux_for_better_system_performance.md)
    - [Как использовать ZRAM в Ubuntu 24.04](/articles/how_to_use_zram_on_ubuntu_2404.md)
    - [Сжатие RAM в Linux](/articles/ram_compression_on_linux.md)
    - [Сжатие памяти](/articles/memory_compression.md)
    - [zram: сжатые блочные устройства в оперативной памяти](/articles/zram_compressed_ram-based_block_devices.md)
  - Межпроцессное взаимодействие
    - [Unix domain sockets: локальный IPC через AF_UNIX](/articles/unix_domain_sockets_razbor_lokalnogo_ipc_cherez_af_unix_sock_streamsock_dgramsoc.md)
  - Процессы
    - [Как просмотреть активные процессы в Linux](/articles/view_active_linux_processes.md)
    - [htop объясненный](/articles/htop_explained.md)
    - [Форкинг против потоков](/articles/forking_vs_threads.md)
  - Память, swap и OOM
    - [OOM killer](/articles/oom_killer.md)
    - [Linux OOM killer - выживание](/articles/linux_oom_killer_survival.md)
    - [Заставить «OOM killer'а» игнорировать процесс](/articles/protect_process_from_oom_killer.md)
    - [Демон подкачки ядра (kswapd)](/articles/kswapd_kernel_swap_daemon.md)
    - [Как очистить своп при наличии свободной оперативной памяти?](/articles/clear_swap_with_free_memory.md)
    - [Файл подкачки, ограничения памяти и cgroups](/articles/swap_memory_limits_cgroups.md)
- Хранилище и файловые системы
  - Файловые системы
    - btrfs
      - [BTRFS для самых маленьких](/articles/btrfs_dlya_samykh_malenkikh.md)
    - sshfs
      - [Как с помощью SSHFS подключать удалённые файловые системы по SSH](/articles/how_to_use_sshfs_to_mount_remote_file_systems_over_ssh.md)
    - ZFS
      - [ZFS: архитектура, особенности и отличия от других файловых систем](/articles/zfs_arkhitektura_osobennosti_i_otlichiya_ot_drugikh_failovykh_sistem.md)
      - [Основы ZFS: система хранения и производительность](/articles/osnovy_zfs_sistema_khraneniya_i_proizvoditelnost.md)
      - [Что такое ZFS? И почему люди от неё без ума?](/articles/chto_takoe_zfs_i_pochemu_lyudi_ot_nee_bez_uma.md)
    - dev
      - [Каталог /dev в Linux](/articles/understanding_the_dev_directory_in_linux.md)
    - proc
      - [Изучаем файловую систему proc](/articles/izuchaem_failovuyu_sistemu_proc.md)
      - [Каталог /proc в Linux](/articles/katalog_proc_v_linux.md)
      - [Файловые системы /dev и /proc в Linux 2.4](/articles/failovye_sistemy_dev_i_proc_v_linux_24.md)
  - Основы файловых систем
    - [FHS (Filesystem Hierarchy Standard); стандарт иерархии файловой системы](/articles/fhs_filesystem_hierarchy_standard_standart_ierarkhii_failovoi_sistemy.md)
    - [Файлы и файловые системы](/articles/files_and_filesystems.md)
  - Восстановление данных
    - [Утилиты для восстановления потерянных данных в Linux](/articles/utility_dlya_vosstanovleniya_poteryannykh_dannykh_v_linux.md)
  - Диски и монтирование
    - [[Пошагово] Клонирование диска Clonezilla с большего на меньший](/articles/poshagovo_klonirovanie_diska_clonezilla_s_bolshego_na_menshii.md)
    - [Изменение размера root lvm раздела](/articles/resize_root_lvm_partition.md)
    - [mount - примеры](/articles/mount_examples.md)
  - Синхронизация данных
    - rsync
      - [rsync, статья 1: сценарии использования (2022)](/articles/rsync_article_1_scenarios_2022.md)
      - [rsync, статья 2: окружение (2022)](/articles/rsync_article_2_surroundings_2022.md)
      - [rsync, статья 3: как работает rsync? (2022)](/articles/rsync_article_3_how_does_rsync_work_2022.md)
  - Файлы и архивы
    - [Как вывести список файлов каталога с 8 миллионами файлов (но не с помощью ls)](/articles/you_can_list_a_directory_containing_8_million_files_but_not_with_ls.md)
    - [18 примеров команды tar в Linux](/articles/tar_command_18_examples.md)
    - [Хаки при работе с большим числом мелких файлов](/articles/handling_many_small_files.md)
    - [Как оптимизировать и сжать JPEG или PNG изображений в Linux командная строка](/articles/optimize_jpeg_png_cli.md)
  - Иерархия и размещение данных
    - [Значение каталогов в Unix и Unix-подобных системах](/articles/unix_directory_structure.md)
    - [Стандартные каталоги Linux](/articles/linux_standard_directories.md)
    - [Стандарт иерархии файловой системы](/articles/filesystem_hierarchy_standard.md)
    - [Где сохранить файлы конфигурации / данных в GNU / Linux?](/articles/linux_configuration_and_data_locations.md)
    - [Где хранить данные приложения (не для пользователя) в Linux](/articles/linux_application_data_location.md)
    - [Можно ли использовать косую черту в имени файла?](/articles/slash_in_filename.md)
    - [Как мне создать имя файла с недопустимыми символами, такими как:?>?](/articles/filenames_with_invalid_characters.md)
- Системное администрирование
  - Дата и время
    - [Clock Mini-HOWTO: как Linux отслеживает время](/articles/how_linux_keeps_track_of_time.md)
  - Планировщики задач
    - cron
      - [Почему cron](/articles/pochemu_cron_samyi_opasnyi_instrument_v_linux_prakticheskii_razbor_ris.md)
      - [crontab в Linux](/articles/crontab_in_linux.md)
    - systemd timers
      - [systemd/Timers](/articles/systemdtimers_russkoyazychnaya_stranitsa_archwiki_po_systemd_taimeram_.md)
      - [Использование таймеров systemd вместо заданий cron](/articles/ispolzovanie_taimerov_systemd_vmesto_zadanii_cron_perevod_stati_david_.md)
      - [Что такое systemd timers и как заменить ими cron для планирования задач](/articles/chto_takoe_systemd_timers_i_kak_zamenit_imi_cron_dlya_planirovaniya_za.md)
  - systemd
    - Контроль и восстановление служб
      - [Настройка самовосстанавливающихся служб с systemd](/articles/set_up_self-healing_services_with_systemd.md)
      - [systemd Watchdog для любого сервиса](/articles/systemd_watchdog_for_any_service.md)
    - Основы
      - [Systemd для начинающих: разбор юнитов и их функций](/articles/systemd_dlya_nachinayushchikh_razbor_yunitov_i_ikh_funktsii.md)
      - [systemd десять лет спустя. Историческая и техническая ретроспектива](/articles/systemd_desyat_let_spustya_istoricheskaya_i_tekhnicheskaya_retrospekti.md)
      - [systemd и cgroup](/articles/systemd_and_cgroup.md)
      - [Как просмотреть статус службы с помощью systemctl](/articles/how_to_view_status_of_a_service_using_systemctl.md)
      - [systemd: хорошие части](/articles/systemd_the_good_parts.md)
    - Службы
      - [Systemd за пять минут](/articles/systemd_in_five_minutes.md)
      - [Как создать сервисный модуль systemd в Linux](/articles/create_systemd_service_unit.md)
      - [Создание службы Linux с помощью systemd](/articles/create_linux_service_with_systemd.md)
      - [Как написать systemd unit-файл для автозагрузки своего сервиса](/articles/systemd_service_autostart_unit.md)
      - [Как настроить службу systemd для периодического перезапуска?](/articles/systemd_periodic_service_restart.md)
      - [Перезапуск Systemd = всегда не соблюдается](/articles/systemd_restart_always_behavior.md)
  - Управление конфигурацией
    - etckeeper
      - [Etckeeper: Git-история для /etc и быстрый аудит изменений конфигурации](/articles/etckeeper_git_istoriya_dlya_etc_i_bystryi_audit_izmenenii_konfiguratsi.md)
      - [Власть над конфигурацией. Etckeeper и Git](/articles/vlast_nad_konfiguratsiei_etckeeper_i_git_prakticheskaya_statya_po_etck.md)
      - [Упрощаем администрирование с etckeeper. Настройка контроля версий конфигов в /etc](/articles/uproshchaem_administrirovanie_s_etckeeper_nastroika_kontrolya_versii_k.md)
    - Drop-in-каталоги
      - [Drop-in (.d) каталоги в Linux: более безопасный способ управления конфигурационными файлами](/articles/drop-in_d_directories_in_linux_explained_a_safer_way_to_manage_config_files.md)
  - Пользовательское окружение
    - [Linux-телефоны сейчас важнее, чем когда-либо](/articles/linux_telefony_seichas_vazhnee_chem_kogda_libo.md)
    - [Как проверить версию плазмы?](/articles/check_kde_plasma_version.md)
    - [IT пейзаж для сисадминов](/articles/sysadmin_it_landscape.md)
  - Загрузка и восстановление
    - [GRUB2 конфигурация](/articles/grub2_configuration.md)
    - [6 шагов загрузки Linux на пальцах](/articles/linux_boot_in_6_steps.md)
    - [Почему Linux допускает "init=/bin/bash"?](/articles/linux_init_bin_bash.md)
    - [Восстановление пароля root](/articles/root_password_recovery.md)
    - [Как сбросить забытый пароль root на серверах CentOS 7](/articles/reset_root_password_centos_7.md)
    - [Быстрая перезагрузка Linux на примере CentOS](/articles/fast_linux_reboot_with_kexec.md)
  - Пакеты и репозитории
    - [Руководство по упаковке RPM](/articles/rpm_packaging_guide.md)
    - [Сборка RPM - быстрый старт](/articles/rpm_build_quick_start.md)
    - [Создание собственных RPM репозитариев](/articles/create_rpm_repositories.md)
    - [Пакеты Linux по умолчанию](/articles/default_linux_packages.md)
    - [Ubuntu Make — разработчику в помощь](/articles/ubuntu_make_for_developers.md)
- Диагностика и наблюдаемость
  - Трассировка и профилирование
    - [Шпаргалка по поиску узких мест в Linux: топ утилит на все случаи жизни](/articles/shpargalka_po_poisku_uzkikh_mest_v_linux_top_utilit_na_vse_sluchai_zhi.md)
    - [Как strace подключается к уже запущенному процессу?](/articles/strace_attach_to_running_process.md)
    - [Есть ли способ использовать strace для отслеживания различных частей командного конвейера?](/articles/strace_command_pipelines.md)
    - [Производительность Linux](/articles/linux_performance.md)
    - [Механизмы профилирования Linux](/articles/linux_profiling_mechanisms.md)
    - [Профилирование кода на C/C++ в Linux и FreeBSD](/articles/c_cpp_profiling_linux_freebsd.md)
    - [Как получить общее использование ЦП приложения из /proc/pid/stat?](/articles/process_cpu_usage_from_proc_stat.md)
    - [Как рассчитывается время и процент использования ЦП Linux](/articles/linux_cpu_time_and_usage_calculation.md)
  - Диагностика ввода-вывода
    - [Отладка блочного ввода-вывода в Linux](/articles/linux_block_io_debugging.md)
  - Логи и аудит
    - logger
      - [Команда logger: опции, ключи и примеры использования](/articles/komanda_logger_optsii_klyuchi_i_primery_ispolzovaniya_russkoyazychnaya.md)
      - [Команда logger в Linux: подробное руководство](/articles/master_the_linux_logger_command.md)
      - [Команда logger (IBM AIX)](/articles/logger_command_ibm_aix.md)
      - [Команда logger: руководство по системному администрированию Linux](/articles/the_logger_command_linux_system_administration_guide.md)
    - syslog
      - [Как настроить централизованное логирование в Linux с помощью Rsyslog](/articles/how_to_set_up_centralized_logging_on_linux_with_rsyslog.md)
      - [Как собирать, обрабатывать и пересылать логи с помощью Rsyslog](/articles/how_to_collect_process_and_ship_log_data_with_rsyslog.md)
      - [Руководство для начинающих по syslog в Linux](/articles/beginners_guide_to_syslogs_in_linux.md)
      - [syslog-ng](/articles/syslog-ng.md)
    - Общие вопросы
      - [Основы логирования в Linux](/articles/linux_logging_basics.md)
      - [Системное логирование в Linux](/articles/linux_system_logging.md)
      - [Файлы журналов, джоналы и системы логирования](/articles/log_files_journals_and_logging_systems.md)
      - [Логирование вывода консоли](/articles/console_output_logging.md)
      - [Лог файлы Linux по порядку](/articles/linux_log_files_overview.md)
      - [ЧТЕНИЕ И НАСТРОЙКА ЛОГОВ LINUX В UBUNTU И CENTOS](/articles/linux_log_configuration_ubuntu_centos.md)
      - [man logger](/articles/logger_man_page.md)
      - [Как использовать logger в Linux](/articles/linux_logger_usage.md)
      - [Логгируем все команды на сервере](/articles/log_all_server_commands.md)
      - [Аудит системных событий в Linux](/articles/linux_system_event_audit.md)
    - journald
      - [Journalctl — анализ логов Linux](/articles/journalctl_analiz_logov_linux.md)
      - [Использование journalctl для просмотра и анализа логов: подробный гайд](/articles/ispolzovanie_journalctl_dlya_prosmotra_i_analiza_logov_podrobnyi_gaid.md)
      - [Мини-руководство по journalctl](/articles/a_journalctl_mini_tutorial.md)
      - [Как использовать journalctl для просмотра логов сервера](/articles/how_to_use_journalctl_to_consult_server_logs.md)
      - [Как использовать journalctl для просмотра и обработки журналов systemd](/articles/how_to_use_journalctl_to_view_and_manipulate_systemd_logs.md)
    - auditd
      - [auditd](/articles/auditd.md)
      - [Настройка аудита системы Linux с помощью auditd](/articles/auditd_configure_linux_system_auditing.md)
  - Мониторинг
    - Системные мониторы
      - [Руководство по мониторингу системы в Linux: top, htop, btop и glances](/articles/a_guide_to_linux_system_monitoring_top_htop_btop_and_glances.md)
    - Zabbix
      - [Развертывание Zabbix 4.4 с nginx, php-fpm и MySQL Percona в Docker](/articles/razvertyvanie_zabbix_44_s_nginx_php_fpm_i_mysql_percona_v_docker.md)
- Командная строка и разработка
  - Утилиты командной строки
    - [Поиск больших файлов в Linux/macOS](/articles/find_large_files_linuxmacos.md)
    - [Введение в команду nproc в Linux](/articles/intro_to_nproc_command_in_linux.md)
    - [killall(1) — справочная страница Linux](/articles/killall1_linux_manual_page.md)
    - [Примеры sed](/articles/sed_examples.md)
  - Инструменты разработки
    - [О красивых диффах в git](/articles/beautiful_git_diffs.md)
  - Системное программирование
    - ELF
      - [Рецепты для ELFов](/articles/retsepty_dlya_elfov.md)
      - [Эволюция формата объектных файлов ELF](/articles/evolution_of_the_elf_object_file_format.md)
    - Библиотеки
      - [musl FAQ — официальный FAQ по musl libc](/articles/musl_faq_ofitsialnyy_faq_po_musl_libc_chto_delaet_c-biblioteka_v_linux_userspace.md)
      - [Что такое файл разделяемых объектов](/articles/what_is_a_shared_object_file.md)
  - Bash-скрипты
    - [flock](/articles/flock_blokirovki_v_shell_skriptakh_russkoyazychnaya_statya_o_zashchite.md)
    - [Продолжение: блокировка bash-скриптов с flock](/articles/follow_up_bash_script_locking_with_flock.md)
    - [Блокировка критических секций в shell-скриптах](/articles/locking_critical_sections_in_shell_scripts_prakticheskaya_statya_o_zashchite_kritiches.md)
    - [Использование lock-файлов для управления заданиями в bash-скриптах](/articles/using_lock_files_for_job_control_in_bash_scripts_obzor_lock_files_dlya_shell-skri.md)
    - [Bash-скрипты](/articles/bash_scripts.md)
    - [Шпаргалка по Bash-скриптингу](/articles/bash_scripting_cheat_sheet.md)
    - [Условия в скриптах bash (условные операторы)](/articles/bash_conditional_operators.md)
    - [Операции сравнения в bash](/articles/bash_comparison_operators.md)
    - [Взаимодействие bash-скриптов с пользователем](/articles/bash_user_interaction.md)
    - [Взаимодействие bash-скриптов с пользователем. Часть 2](/articles/bash_user_interaction_part_2.md)
    - [Перенаправления](/articles/shell_redirections.md)
  - Терминал
    - [Горячие клавиши терминала Linux](/articles/goryachie_klavishi_terminala_linux.md)
    - [30 эмуляторов терминала для Linux](/articles/30_linux_terminal_emulators.md)
    - [Как использовать команду «Script» для записи терминальной сессии Linux](/articles/record_terminal_session_with_script.md)
    - [Screen](/articles/screen.md)
  - Разработка ПО
    - [Отступ исходного кода](/articles/source_code_indentation.md)
    - [БИБЛИОТЕКИ LINUX](/articles/linux_libraries.md)
- Контейнеры и виртуализация
  - Flatpak
    - [Использование хостового NVIDIA-драйвера с Flatpak](/articles/using_host_nvidia_driver_with_flatpak_podrobnyy_razbor_rasshireniy_gl-drayverov_f.md)
    - [Копаем глубже в Flatpak с NVIDIA](/articles/digging_further_into_flatpak_with_nvidia.md)
    - [Песочница — вики Flatpak](/articles/sandbox_wiki_flatpak_s_razborom_realizatsii_pesochnits.md)
    - [Сборка кросс-дистрибутивных Linux-приложений с Flatpak — практическое руководство: среды выполнения и SDK, `flatpak-builder`, манифест, `finish-args`, права песочницы и публикация подписанного репозитория](/articles/building_cross-distribution_linux_applications_with_flatpak.md)
  - Nix и NixOS
    - [Nix: воспроизводимая сборка](/articles/nix_vosproizvodimaya_sborka.md)
    - [NixOS — установка и настройка](/articles/nixos_ustanovka_i_nastroika.md)
    - [Воспроизводимая среда разработки с Nix](/articles/vosproizvodimaya_sreda_razrabotki_s_nix.md)
    - [Как создать песочницу и опакетить программу в NixOS?](/articles/kak_sozdat_pesochnitsu_i_opaketit_programmu_v_nixos.md)
    - [Мои приключения с NixOS, часть 1: начало работы](/articles/moi_priklyucheniya_s_nixos_chast_1_nachalo_raboty.md)
    - [Немного о NixOS. Часть 1. Общая информация и установка](/articles/nemnogo_o_nixos_chast_1_obshchaya_informatsiya_i_ustanovka.md)
    - [NixOS — хорошая серверная ОС, кроме случаев, когда это не так](/articles/nixos_is_a_good_server_os_except_when_it_isnt.md)
    - [Сборка пакета для Nix](/articles/sborka_paketa_dlya_nix.md)
    - [Запуск и автообновление Docker-контейнеров на NixOS](/articles/run_and_auto-update_docker_containers_on_nixos.md)
    - [Дешёвые Docker-образы с Nix](/articles/cheap_docker_images_with_nix.md)
    - [Изолированные окружения для разработки с помощью Nix](/articles/isolated_development_environment_using_nix.md)
    - [Шаг в будущее управления конфигурацией и инфраструктурой с Nix](/articles/a_step_towards_the_future_of_configuration_and_infrastructure_management_with_ni.md)
  - systemd-nspawn
    - [Из дневника разработчика: автологин в machinectl](/articles/machinectl_auto_login.md)
    - [Systemd и контейнеры: знакомство с systemd-nspawn](/articles/systemd_i_konteinery_znakomstvo_s_systemd_nspawn.md)
    - [Запуск контейнеров systemd-nspawn с VPN-интерфейсом](/articles/running_systemd-nspawn_containers_with_a_vpn_interface.md)
    - [systemd-nspawn](/articles/systemd_nspawn_jimmyg.md)
    - [systemd для администраторов, часть XXI: интеграция с контейнерами](/articles/systemd_for_administrators_part_xxi.md)
    - [Запуск NixOS из любого дистрибутива Linux в контейнерах systemd-nspawn](/articles/running_nixos_from_any_linux_distro_in_systemd-nspawn_containers.md)
    - [Настройка контейнеров с systemd-nspawn](/articles/setting_up_containers_with_systemd-nspawn.md)
  - Podman
    - [Podman на edge: поддержание жизни сервисов с помощью пользовательских действий healthcheck](/articles/podman_at_the_edge_keeping_services_alive_with_custom_healthcheck_actions.md)
  - Контейнеры Linux
    - [Мой первый контейнер без Docker](/articles/moi_pervyi_konteiner_bez_docker.md)
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
  - TCP/IP и транспортные протоколы
    - SO_REUSEPORT
      - [Когда один TCP-порт может быть поделён](/articles/kogda_odin_tcp_port_mozhet_byt_podelen.md)
      - [Увеличиваем производительность с помощью SO_REUSEPORT в NGINX 1.9.1](/articles/uvelichivaem_proizvoditelnost_s_pomoshchyu_so_reuseport_v_nginx_191.md)
      - [Linux TCP SO_REUSEPORT: использование и реализация](/articles/linux_tcp_so_reuseport_usage_and_implementation.md)
      - [Балансировка TCP-соединений в ядре Linux](/articles/loadbalancing_tcp_connections_in_the_linux_kernel.md)
      - [Оптимизация производительности с SO_REUSEPORT](/articles/performance_optimisation_using_so_reuseport.md)
      - [Идеальная локальность и три эпичных SystemTap-скрипта](/articles/perfect_locality_and_three_epic_systemtap_scripts.md)
      - [Квантовое состояние TCP-порта](/articles/the_quantum_state_of_a_tcp_port.md)
    - Поиск сокетов в ядре
      - [Сокеты в ядре Linux — Часть 3: поиск TCP-сокета на приёме](/articles/sockets_in_the_linux_kernel_-_part_3_tcp_socket_lookup_on_rx_razbor_poiska_soketa.md)
      - [Сокеты в ядре Linux — Часть 2: поиск UDP-сокета на приёме](/articles/sockets_in_the_linux_kernel_part_2_udp_socket_lookup_on_rx.md)
      - [Сокеты в ядре Linux. Часть 1: демультиплексирование L4-протоколов на приёме](/articles/sockets_in_the_linux_kernel_-_part_1_l4_protocol_demultiplexing_on_rx_razbor_vyb.md)
    - Управление перегрузкой
      - [Внутреннее устройство управления перегрузкой TCP в Linux](/articles/linux_tcp_congestion_control_internals.md)
      - [Как переключать алгоритмы контроля перегрузки TCP в Linux](/articles/how_to_switch_tcp_congestion_control_algorithms_on_linux.md)
      - [TCP Congestion Control или Почему скорость прыгает](/articles/tcp_congestion_control_ili_pochemu_skorost_prygaet.md)
      - [Как работает TCP congestion control: Reno, Cubic, BBR простыми словами](/articles/kak_rabotaet_tcp_congestion_control_reno_cubic_bbr_prostymi_slovami.md)
      - [TCP BBR: быстрый и простой способ ускорения загрузки страниц. Доклад Яндекса](/articles/tcp_bbr_bystryi_i_prostoi_sposob_uskoreniya_zagruzki_stranits_doklad_y.md)
      - [Увеличение скорости интернета в Linux с TCP BBR](/articles/increase_linux_internet_speed_with_tcp_bbr.md)
      - [Как включить и настроить TCP BBR в Linux](/articles/how_to_enable_and_configure_tcp_bbr_on_linux.md)
    - Планирование и пейсинг пакетов
      - [FQ - Fair Queuing](/articles/fq_fair_queuing.md)
      - [pkt_sched: fq: планировщик пакетов Fair Queue](/articles/pkt_sched_fq_fair_queue_packet_scheduler.md)
      - [Пейсинг пакетов в Linux: fq против tbf](/articles/packet_pacing_on_linux_fq_vs_tbf.md)
    - Порты и соединения
      - [Что ограничивает максимальное число соединений на Linux-сервере?](/articles/what_limits_max_connections_on_linux_server.md)
      - [Максимизируем число одновременных подключений к веб-серверу](/articles/maximize_your_concurrent_web_server_connections.md)
      - [Приложения TCP/IP на примерах](/articles/tcp_ip_applications_examples.md)
      - [Привязка Портов](/articles/port_binding.md)
      - [Могут ли два приложения прослушивать один и тот же порт?](/articles/multiple_apps_same_port.md)
      - [И еще о специальном файле устройства /dev/tcp (TCP/IP), встроенном в bash](/articles/bash_dev_tcp.md)
      - [Как открыть TCP-/UDP-сокет средствами командной оболочки bash](/articles/bash_tcp_udp_sockets.md)
  - Сокетный API
    - [Что такое сокет?](/articles/what_is_a_socket.md)
  - Высокопроизводительные сети
    - BPF и eBPF
      - [BPF для самых маленьких, часть нулевая: classic BPF](/articles/bpf_dlya_samykh_malenkikh_chast_nulevaya_classic_bpf.md)
    - RDMA
      - [Глубокое понимание механизма взаимодействия RDMA между программным и аппаратным обеспечением](/articles/an_in-depth_understanding_of_rdma_interaction_mechanism.md)
  - IP-адресация
    - Выбор адреса по умолчанию
      - [RFC 3484 в Linux — выбор адресов по Ульриху Дрепперу](/articles/rfc_3484_on_linux.md)
      - [Выбор адреса по умолчанию. Часть 1](/articles/default_address_selection_part_1_vvodnaya_statya_pro_vybor_ipv6-adresov_v_linux_r.md)
      - [Выбор адреса по умолчанию. Часть 2](/articles/default_address_selection_part_2_razbor_vybora_adresa_istochnika_v_yadre_linux_mar.md)
  - DNS и разрешение имён
    - Настройка resolver
      - [/etc/gai.conf — это совсем не то, что вы думаете](/articles/etcgaiconf_it_aint_what_you_think_it_is.md)
      - [Какие правила добавить в /etc/gai.conf](/articles/finding_out_what_rules_to_add_to_etcgaiconf_prakticheskiy_razbor_nastroyki_etcgai.md)
      - [Resolv.conf](/articles/resolvconf.md)
      - [Взаимоотношения dhcpclient и resolv.conf'а в Linux](/articles/vzaimootnosheniya_dhcpclient_i_resolvconfa_v_linux.md)
      - [resolv.conf](/articles/resolv_conf_wikipedia.md)
      - [Настройка хоста для применения сервера имен](/articles/nastroika_hosta_dlya_primeneniya_servera_imen.md)
    - Разрешение имён
      - [Resolve IP адресов в Linux: понятное и детальное описание](/articles/resolve_ip_adresov_v_linux_ponyatnoe_i_detalnoe_opisanie.md)
      - [Анатомия DNS-запроса в Linux — часть IV](/articles/anatomy_of_a_linux_dns_lookup_part_iv.md)
      - [Анатомия DNS-запроса в Linux. Часть I](/articles/anatomy_of_a_linux_dns_lookup_part_i.md)
      - [Анатомия DNS-запроса в Linux. Часть II](/articles/anatomy_of_a_linux_dns_lookup_part_ii.md)
      - [Анатомия DNS-запроса в Linux. Часть III](/articles/anatomy_of_a_linux_dns_lookup_part_iii.md)
      - [Как работает DNS в Linux. Часть 1: от getaddrinfo до resolv.conf](/articles/kak_rabotaet_dns_v_linux_chast_1_ot_getaddrinfo_do_resolvconf.md)
      - [Трассировка разрешения имён хостов в Linux](/articles/tracing_linux_hostname_resolution.md)
      - [Как мне разрешить имя хоста в IP-адрес в скрипте Bash?](/articles/resolve_hostname_in_bash.md)
    - Основы DNS
      - [Служба доменных имен (DNS)](/articles/sluzhba_domennykh_imen_dns.md)
  - Сетевая диагностика
    - Netcat
      - [Ncat, Netcat, nc](/articles/ncat_netcat_nc.md)
      - [Лучшие альтернативы Netcat-листенеру](/articles/hacking_articles.md)
    - MTR
      - [Команда MTR в Linux](/articles/linux_mtr_command.md)
      - [Продвинутая диагностика сети: My Traceroute (MTR)](/articles/advanced_network_troubleshooting_using_my_traceroute_mtr.md)
  - Удалённый доступ
    - RDP
      - [Как установить Xrdp Server (удалённый рабочий стол) на Ubuntu 20.04](/articles/how_to_install_xrdp_on_ubuntu.md)
    - SSH
      - Клиенты
        - [SSH Pilot - Современный менеджер SSH сессий для Linux](/articles/ssh_pilot_sovremennyi_menedzher_ssh_sessii_dlya_linux_russkoyazychnyi_.md)
      - Настройка
        - [Как использовать файл конфигурации SSH](/articles/how_to_use_the_ssh_config_file.md)
      - Туннели и прокси
        - [SSH: локальная переадресация портов](/articles/ssh_local_port_forwarding.md)
        - [SSH port forwarding для начинающих](/articles/ssh_port_forwarding_for_beginners.md)
        - [Наглядное руководство по SSH-туннелям: локальная и удалённая переадресация портов](/articles/a_visual_guide_to_ssh_tunnels_local_and_remote_port_forwarding.md)
        - [Прокси через SSH-туннель](/articles/ssh_tunnel_proxy.md)
        - [Как надежно поддерживать открытый туннель SSH?](/articles/persistent_ssh_tunnel.md)
        - [github ssh proxy](/articles/github_ssh_proxy.md)
      - Практика использования
        - [Мультиплексирование в OpenSSH](/articles/opensshcookbookmultiplexing.md)
        - [Почему перенос SSH на порт, отличный от 22, — плохая идея](/articles/why_putting_ssh_on_another_port_than_22_is_bad_idea.md)
  - Маршрутизация и роутеры
    - VyOS
      - [Homelab: миграция и обновление Proxmox + Debian + VyOS](/articles/homelab_proxmox_debian_vyos_upgrade_migration.md)
      - [VyOS с нуля: маршрутизация и VPS](/articles/vyos_from_scratch_routing_and_vps_edition.md)
      - [VyOS](/articles/vyos.md)
      - [VPN-туннель между маршрутизаторами Cisco и VyOS с использованием VTI](/articles/vpn_tunnel_between_cisco_and_vyos_routers_using_vtis.md)
      - [VyOS OpenSource Router](/articles/vyos_opensource_router.md)
      - [Программная маршрутизация с VyOS](/articles/programmnaya_marshrutizatsiya_s_vyos.md)
      - [Программная маршрутизация с VyOS в условиях санкций](/articles/programmnaya_marshrutizatsiya_s_vyos_v_usloviyakh_sanktsii.md)
      - [Создание отказоустойчивой ИТ инфраструктуры. Часть 3. Организация маршрутизации на роутерах VyOS](/articles/sozdanie_otkazoustoichivoi_it_infrastruktury_chast_3_organizatsiya_mar.md)
      - [Rolling-релизы VyOS](/articles/vyos_rolling_release.md)
  - Прокси
    - [Настройка proxychains](/articles/nastroika_proxychains.md)
  - Беспроводные сети
    - [DFS (динамический выбор частоты)](/articles/dfs_dynamic_frequency_selection.md)
- Безопасность и доступ
  - Защита от эксплуатации
    - ASLR
      - [ASLR в деталях](/articles/aslr_in_depth.md)
      - [Методы смягчения эксплойтов — Часть 3: рандомизация раскладки адресного пространства (ASLR)](/articles/exploit_mitigation_techniques_part_3_address_space_layout_randomization.md)
      - [Как обойти базовые механизмы защиты от эксплойтов — Часть 0x03: ASLR](/articles/how_to_bypass_basic_exploit_mitigation_part_0x03_aslr_prakticheskiy_x86-64_razbor.md)
  - Права доступа
    - ACL
      - [Linux — работа с ACL](/articles/linux_rabota_s_acl.md)
      - [Быть или не быть ACL в администрировании Linux](/articles/byt_ili_ne_byt_acl_v_administrirovanii_linux.md)
      - [Совместное использование файлов с помощью ACL](/articles/sharing_files_with_acls.md)
      - [Глава 20. Списки контроля доступа (ACL)](/articles/chapter_20_access_control_lists.md)
    - Пользователи и группы
      - [Группы и права пользователей в Linux](/articles/linux_user_groups_and_permissions_guide.md)
  - Защита сетевого доступа
    - [fail2ban ssh i bruteforce attack](/articles/fail2ban_ssh_i_bruteforce_attack.md)
    - [Как настроить файрвол с UFW в Ubuntu](/articles/kak_nastroit_fairvol_s_ufw_v_ubuntu.md)
    - [nftables](/articles/nftables.md)
  - Криптография и сертификаты
    - [v1.24_ЕСИА и ГОСТ Р 34.10-2012 сертификаты](/articles/v124_esia_i_gost_r_3410_2012_sertifikaty.md)
  - Привилегии и capabilities
    - [Capabilities (Русский)](/articles/capabilities_russkii.md)
    - [setcap](/articles/setcap.md)
    - [Замена setuid-бита на capabilities для системных программ в Linux](/articles/zamena_setuid_bita_na_capabilities_dlya_sistemnykh_programm_v_linux.md)
    - [Лишение пользователя root привилегий](/articles/lishenie_polzovatelya_root_privilegii.md)
    - [В двух словах о привилегиях Linux (capabilities)](/articles/v_dvukh_slovakh_o_privilegiyakh_linux_capabilities.md)
    - [В чём суть Linux Capabilities? (Часть 2)](/articles/whats_the_big_deal_with_linux_capabilities_part_2.md)
    - [Что такого особенного в Linux Capabilities?](/articles/whats_the_big_deal_with_linux_capabilities.md)
    - [Команда capsh](/articles/capsh_command.md)
  - Аутентификация и авторизация
    - [Основы и настройка PAM](/articles/pam_configuration.md)
    - [Начала PAM.](/articles/pam_introduction.md)
    - [AAA](/articles/aaa.md)
  - Защита системы
    - [Двенадцать советов по повышению безопасности Linux](/articles/linux_security_tips.md)
    - [TCP SACK PANIC - Уязвимости ядра - CVE-2019-11477, CVE-2019-11478 и CVE-2019-11479](/articles/tcp_sack_panic_vulnerabilities.md)
- Серверное ПО и базы данных
  - Брокеры сообщений
    - RabbitMQ
      - [Как установить сервер RabbitMQ в Linux (краткое руководство)](/articles/how_to_install_rabbitmq_server_on_linux_quick_guide.md)
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
[firewall](/tags/firewall.md)
[nftables](/tags/nftables.md)
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
[linux](/tags/linux.md)
[epoll](/tags/epoll.md)
[unix](/tags/unix.md)
[journald](/tags/journald.md)
[nixos](/tags/nixos.md)
[nix](/tags/nix.md)
[sockets](/tags/sockets.md)
[dns](/tags/dns.md)
