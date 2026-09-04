# Копаем глубже в Flatpak с NVIDIA

Источник: [Digging further into Flatpak with NVIDIA](https://blogs.igalia.com/vjaquez/digging-further-into-flatpak-with-nvidia/)

17 января 2022 · теги: flatpak, nvidia, opengl

Как вы, возможно, знаете, среда разработки, используемая WebKitGTK и WPE, основана на Flatpak. Мне кажется, что работа с софтом внутри Flatpak похожа на дистанционное управление марсоходом: чтобы выполнить нужные мне команды, я вынужден проходить через команды Flatpak. Кривая обучения более крутая, зато в обмен мы получаем единую среду разработки. Я начал работать над ещё одним проектом, где требуется использовать GPU NVIDIA, не прекращая работу над WebKitGTK/WPE. Значит, мне нужно было использовать видеокарту внутри Flatpak, а, как известно, сейчас такая настройка не работает «из коробки». Более того, для Vulkan мне нужно использовать очень конкретную версию драйвера видеокарты.

Вот история о том, как я заставил это работать.

Моя главная опора — это, конечно, пост моего коллеги TingPing: [Using host Nvidia driver with Flatpak](https://blog.tingping.se/2018/08/26/flatpak-host-extensions.html), а также [Flatpak for NVIDIA GL runtime platform](https://github.com/flathub/org.freedesktop.Platform.GL.nvidia).

Как объяснил TingPing, Flatpak _не использует библиотеки хост-системы_, поэтому для специфических аппаратных конфигураций могут понадобиться [среды выполнения и расширения (runtimes and extensions)](https://docs.flatpak.org/en/latest/available-runtimes.html) с библиотеками для userspace, например среда выполнения NVIDIA GL platform. И _она должна иметь ту же версию, что и работающая в ядре_.

[Расширение NVIDIA GL platform](https://github.com/flathub/org.freedesktop.Platform.GL.nvidia) — небольшой проект, который генерирует среды выполнения Flatpak для _каждого_ публичного драйвера NVIDIA. Интересно то, что эти среды выполнения создаются не во время сборки, а во время установки. Когда пользователь устанавливает среду выполнения, блоб (blob) драйвера скачивается с серверов NVIDIA (см. `--extra-data` в `flatpak build-finish` для справки), после чего запускается маленькая программа, которая извлекает встроенный в блоб tarball, а из него уже достаёт нужные библиотеки. Иначе говоря, изначально среда выполнения состоит только из определения файла, который нужно скачать, и маленькой программы, которая заполняет файловую систему Flatpak в момент установки.

Тонкость, о которой я долго не догадывался, в том, что эта маленькая программа _должна быть скомпилирована статически (statically compiled)_, поскольку она должна запускаться независимо от того, какая среда выполнения доступна.

Эта маленькая программа использует [libarchive](https://www.libarchive.org/) для извлечения библиотек из tarball-а NVIDIA, но статическая версия `libarchive` недоступна ни в одном SDK Flatpak. Более того, наше использование `libarchive` будет зависеть от `libz` и `liblzma`, которые тоже должны быть скомпилированы статически. К счастью, есть единственная, очень старая и устаревшая версия SDK freedesktop, которая предлагает статические версии `libz` и `liblzma`: 1.6. _Вот почему org.freedesktop.Platform.GL.nvidia требует именно эту старую версию SDK_. Поэтому манифест расширения фактически содержит статическую компиляцию `libarchive` и статическую компиляцию будущего `apply_extra`.

_Обновление:_ есть [merge request о переходе на текущий freedesktop SDK 21.08](https://github.com/flathub/org.freedesktop.Platform.GL.nvidia/pull/71), который, по сути, статически собирает `libz` и `liblzma` в дополнение к `libarchive`.

Мне пришлось немного модифицировать исходники `org.freedesktop.Platform.GL.nvidia`, потому что по умолчанию они представляют собой большой цикл из скачивания, хеширования, генерирования по шаблону json-манифеста и сборки для каждого поддерживаемого драйвера. Но в моём случае нужен всего один кастомный драйвер, и я не хотел тратить время на этот цикл. Хак для этого довольно прост:

```diff
diff --git a/versions.sh b/versions.sh
index 8b72664..86686c0 100755
--- a/versions.sh
+++ b/versions.sh
@@ -15,4 +15,5 @@ TESLA_VERSIONS="450.142.00 450.119.04 450.51.06 450.51.05 440.118.02 440.95.01 4
# Probably never: https://ahayzen.com/direct/flathub_downloads_only_nvidia_runtimes.txt
UNSUPPORTED_VERSIONS="390.147 390.144 390.143 390.141 390.138 390.132 390.129 390.116 390.87 390.77 390.67 390.59 390.48 390.42 390.25 390.12 387.34 387.22 387.12 384.130 384.111 384.98 384.90 384.69 384.59 384.47 381.22 381.09 378.13 375.82 375.66 375.39 375.26 370.28 367.57"

-DRIVER_VERSIONS="$BETA_VERSIONS $VULKAN_VERSIONS $NEW_FEATURE_VERSIONS $PRODUCTION_VERSIONS $LEGACY_VERSIONS $TESLA_VERSIONS $UNSUPPORTED_VERSIONS"
+#DRIVER_VERSIONS="$BETA_VERSIONS $VULKAN_VERSIONS $NEW_FEATURE_VERSIONS $PRODUCTION_VERSIONS $LEGACY_VERSIONS $TESLA_VERSIONS $UNSUPPORTED_VERSIONS"
+DRIVER_VERSIONS="470.XX.XX"
```

Но чтобы это заработало, нужен файл в каталоге `data/` со спецификацией файла для скачивания в формате: `NAME:SHA256:DOWNLOAD-SIZE:INSTALL-SIZE:URL`.

```diff
--- /dev/null
+++ b/data/nvidia-470.XX.XX-x86_64.data
@@ -0,0 +1 @@
+:34...checksum-sha264...:123456789::http://compu.home.arpa/NVIDIA/NVIDIA-Linux-x86_64-470.XX.XX.run
```

Последний параметр — это URL, откуда должен скачиваться драйвер. В моём случае это локальный сервер для упрощения тестирования.

Если коротко, команды для выполнения таковы.

Настройка окружения для сборки:

```bash
flatpak install org.freedesktop.Sdk//1.6 org.freedesktop.Platform//1.6
```

Сборка репозитория Flatpak и пакета:

```bash
make
```

Команда создаст каталог `repo` в текущем. Именно там хранится сгенерированный пакет Flatpak.

Установка локального репозитория и расширения:

```bash
flatpak --user remote-add --no-gpg-verify nvidia-local repo
flatpak -v install nvidia-local org.freedesktop.Platform.GL.nvidia-470-XX-XX
```

Удаление устаревших SDK и платформы после сборки:

```bash
flatpak uninstall org.freedesktop.Sdk//1.6 org.freedesktop.Platform//1.6
```

Удаление локального репозитория и расширения, если что-то пошло не так:

```bash
flatpak -v uninstall org.freedesktop.Platform.GL.nvidia-470-62-15
flatpak --user remote-delete nvidia-local
```

Один из способов проверить, корректно ли установлены библиотеки и совпадают ли они с драйвером, работающим в ядре хоста, — установить и запустить [`GreenWithEnvy`](https://gitlab.com/leinardi/gwe):

```bash
flatpak install com.leinardi.gwe
flatpak run com.leinardi.gwe
```

Если вы хотите установить драйвер в свою среду разработки WebKit, достаточно установить переменную окружения `FLATPAK_USER_DIR`:

```bash
FLATPAK_USER_DIR=~/WebKit/WebKitBuild/UserFlatpak flatpak --user remote-add --no-gpg-verify nvidia-local repo
FLATPAK_USER_DIR=~/WebKit/WebKitBuild/UserFlatpak flatpak -v install nvidia-local org.freedesktop.Platform.GL.nvidia-470-XX-XX
```

**********

[linux](/tags/linux.md)
[networking](/tags/networking.md)