# [Пошагово] Клонирование диска Clonezilla с большего на меньший

Источник: [[Пошагово] Клонирование диска Clonezilla с большего на меньший](https://www.diskpart.com/ru/articles/clonezilla-clone-larger-disk-to-smaller-disk-1503.html)

Иногда вам может понадобиться клонирование большого жесткого диска на меньший по каким-то причинам. Здесь мы покажем вам, как использовать Clonezilla для клонирования большего диска на меньший, а, что более важно, представим вам более простую альтернативу - программу для клонирования диска AOMEI Partition Assistant.

![Tracy](/assets/images/author/tracy.png)

К [Tracy](https://www.diskpart.com/author/aomei.html) / Обновление February 12, 2025

Поделись этим: [ ![facebook](/resource/images/dp-theme/dp-article-ab-ic-share-fb-24.svg) ]() [ ![twitter](/resource/images/dp-theme/dp-article-ic-tw-12.png) ]() [ ![instagram](/resource/images/dp-theme/dp-article-ab-ic-share-in-24.svg) ]() [ ![reddit](/resource/images/dp-theme/dp-article-ab-ic-share-reddit-24.svg) ]()

![]()

**Содержание**

  1. Почему использовать Clonezilla для клонирования большого диска на меньший?

```text
 1. ◙ Может ли Clonezilla клонировать на меньший диск?
```

  2. Пошаговое руководство по клонированию большого диска на меньший с помощью Clonezilla

```text
 1. Часть 1. Уменьшение объема
 2. Часть 2. Создание загрузочной флешки Clonezilla
 3. Часть 3. Клонирование с помощью Clonezilla на меньший диск
```

  3. Ошибка: Clonezilla не клонирует на меньший диск
  4. Более простой альтернативный способ клонирования более крупного жесткого диска на меньший
  5. Вывод

## Почему использовать Clonezilla для клонирования большого диска на меньший?

Когда речь идет о клонировании диска, ваша первая мысль, возможно, будет [клонирование жесткого диска на более большой диск](https://www.diskpart.com/articles/clone-hard-drive-to-larger-drive-0310.html). Но вы также можете выбрать клонирование большого диска на меньший диск или SSD из-за проблем с медленной производительностью, ограничений на пространство и оптимизации диска.

Многие пользователи рассматривают использование Clonezilla для клонирования большого диска на меньший. Clonezilla является бесплатной и свободно распространяемой программой для образов и клонирования дисков. Она поддерживает резервное копирование системы, клонирование диска, разработку системы и многое другое. Кроме того, он совместим с несколькими устройствами, такими как Linux, macOS, Chrome OS и Windows. Вот почему многие люди любят использовать Clonezilla для клонирования на меньший диск.

[![clonezilla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/articles/images/clone-hdd-to-ssd-clonezilla-3889/Clonezilla.gif)

### ◙ Может ли Clonezilla клонировать на меньший диск?

Однако Clonezilla может клонировать большой диск на меньший диск только в том случае, если исходный жесткий диск соответствует целевому диску, поскольку Clonezilla клонирует только используемое пространство на второй жесткий диск. Например, если вы хотите клонировать диск, который занимает 100 ГБ, целевой диск должен иметь как минимум 100 ГБ свободного места для успешного клонирования.

**Совет:** Из-за отличной производительности и все более доступной цены на SSD, мы рекомендуем вам [клонировать HDD на SSD с помощью Clonezilla](https://www.diskpart.com/articles/clone-hdd-to-ssd-clonezilla-3889.html) (независимо от того, большего ли на меньший или меньшего ли на больший).

## Пошаговое руководство по клонированию большого диска на меньший с помощью Clonezilla

Признаюсь, что использование Clonezilla для клонирования с большего на меньший диск является чрезвычайно сложным, поэтому внимательно прочитайте, что вы будете читать. Чтобы сделать процесс более понятным, мы разделили его на три части. Начнем.

### Часть 1. Уменьшение объема

Как мы уже описали выше, для того чтобы Clonezilla работала, раздел назначения должен быть равен или больше исходного. Если у вас не заполнен исходный диск, вы можете [сначала уменьшить разделы в Диспетчере дисков](https://www.diskpart.com/disk-management/shrink-volume-6289.html), чтобы подогнать их под целевой диск.

Шаг 1. Нажмите «Windows R», введите «diskmgmt.msc» и нажмите «OK», чтобы открыть Диспетчер дисков.

Шаг 2. На главной странице Диспетчера дисков щелкните правой кнопкой мыши том, который вы хотите уменьшить, а затем выберите «Уменьшить объем». Следуйте указаниям, чтобы завершить оставшиеся операции.

**Совет:** Диспетчер дисков может только уменьшить раздел NTFS. Если файловая система раздела - FAT32, перед уменьшением вам нужно [преобразовать FAT32 в NTFS](https://www.diskpart.com/information/fat32-to-ntfs-converter.html).

[![shrink](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/windows-10/shrink-create/shrink.png)

### Часть 2. Создание загрузочной флешки Clonezilla

Затем вам нужно скачать файл ISO Clonezilla и использовать USB-флешку или CD/DVD для создания загрузочного диска Clonezilla. Здесь мы возьмем за пример создание загрузочной USB-флешки.

Шаг 1. Перейдите на страницу [скачивания Clonezilla](https://clonezilla.org/downloads/download.php?branch=stable). Установите параметры, как показано на картинке ниже, и нажмите кнопку Загрузка на вашем компьютере.

[![download-clonezilla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/others/download-clonezilla.png)

Шаг 2. Подготовьте 1 ГБ USB-флешку (или больше) и найдите программу для создания загрузочной USB-флешки, например, AOMEI Partition Assistant, чтобы [создать загрузочную флешку Clonezilla](https://www.diskpart.com/help/make-bootable-cd-wizard.html).

### Часть 3. Клонирование с помощью Clonezilla на меньший диск

После создания загрузочной USB-флешки Clonezilla следуйте этим инструкциям для начала клонирования с большего диска на меньший с помощью Clonezilla.

**Внимание:** Убедитесь, что вы [установили второй жесткий диск](https://www.diskpart.com/windows-10/how-to-install-a-second-hard-drive-windows-10-1503.html) на вашем компьютере или подключили его к ПК с помощью USB-кабеля.

Шаг 1. Перезагрузите компьютер, нажмите функциональную клавишу, чтобы войти в меню BIOS, и измените порядок загрузки на USB-устройство.

Шаг 2. В меню загрузки выберите "Other modes of Clonezilla live". В следующем интерфейсе вы можете выбрать "To RAM", чтобы освободить раздел загрузки.

Шаг 2. Выберите язык и раскладку клавиатуры, а затем "Start Clonezilla".

[![start-clonezilla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/others/start-clonezilla.png)

Шаг 3. Выберите "Работать с устройством-устройством напрямую с диска или раздела на диск или раздел". Затем выберите "Начальный режим: принять значения по умолчанию" > "disk_to_local_disk local_disk_to_local_disk_clone".

[![disk-local-to-disk-clone-clonezillla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/others/disk-local-to-disk-clonezilla.png)

Шаг 4. Теперь поочередно выберите исходный диск и целевой диск. Здесь вам могут предложить проверить файловую систему исходного диска. Пропустите это или проверьте в зависимости от ваших нужд.

[![select-source-disk-clonezilla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/others/select-source-disk-clonezilla.png)

[![target-disk-clonezilla](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/others/others/target-disk-clonezilla.png)

Шаг 5. Выберите РЕЖИМ ЭКСПЕРТА и включите опцию "-icds". В одном из следующих меню необходимо также выбрать опцию "Изменить размер таблицы разделов пропорционально".

Шаг 6. Затем введите "y" для подтверждения и начните клонирование. Дождитесь завершения процесса клонирования.

## Ошибка: Clonezilla не клонирует на меньший диск

Однако многие пользователи жалуются, что им не удалось использовать Clonezilla для клонирования с более крупного диска на менее крупный. Вот пример пользователя из форума:

"У меня есть большой диск Диск А и маленький диск Диск Б. Диск А содержит несколько разделов, но общий размер всех разделов меньше объема диска Б.

Я попытался использовать Clonezilla в экспертном режиме и выбрал опцию icds, но при начале процесса клонирования клонирование останавливается с ошибкой:

Размер целевого раздела (163830 МБ) меньше размера источника (209716 МБ). Используйте опцию -C для отключения проверки размера (Опасно). Не удалось скопировать /dev/sda1 на /dev/sdb1

Есть ли способ сделать это работающим?"

Проблема с неудачным клонированием при использовании Clonezilla на меньший диск может быть вызвана множеством факторов. Например, если сумма размеров разделов на исходном диске больше, чем у целевого диска, Clonezilla завершится неудачей, или если вы пропустите какой-либо шаг, Clonezilla не выполнится успешно.

Если у вас возникла такая же проблема или вы считаете, что использование Clonezilla для клонирования с более крупного на менее крупный диск довольно сложное, можно попробовать более простой способ. Продолжайте.

## Более простой альтернативный способ клонирования более крупного жесткого диска на меньший

Мощный и практичный инструмент для миграции диска с названием [AOMEI Partition Assistant Professional](https://www.diskpart.com/partition-manager-pro-edition.html) должен быть лучшей альтернативой Clonezilla в Windows 11/10/8/7/XP и Vista, который широко используется для клонирования дисков между большими и меньшими или между HDD и SSD.

Он помогает вам перенести текущую установку Windows, ваши приложения, настройки, файлы и многое другое на новый диск без переустановки или перезагрузки операционной системы. Кроме того, интерфейс программного обеспечения AOMEI прост в использовании, и вы можете следовать простым шагам для завершения процесса клонирования.

Вы можете выбрать клонирование всего жесткого диска или [клонирование только ОС](https://www.diskpart.com/resource/clone-os-to-new-hard-drive.html) с большего жесткого диска на меньший диск. Вот демоверсия, загрузите ее и попробуйте.

[Скачать бесплатноWin 11/10/8.1/8/7/XP](https://www.diskpart.com/ss/download/pa/PAssist_ProDemo.exe)

Безопасный скачивание

Шаг 1. Подключите второй жесткий диск к вашему компьютеру. Установите и откройте AOMEI Partition Assistant Professional. Нажмите "Клонировать" в главном интерфейсе и выберите "Клонировать диск".

[![clone-disk](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/clone-disk.png)

Шаг 2. Выберите более крупный жесткий диск в качестве исходного диска и нажмите "Далее".

[![select-source-disk](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/select-source-disk.png)

Шаг 3. Выберите меньший диск в качестве целевого диска и нажмите "Далее".

[![select-destination-disk](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/select-destination-disk.png)

Шаг 4. Затем вы можете проверить исходный и целевой диск в следующем окне или изменить на "[Клонирование сектора на сектор](https://www.diskpart.com/clone/sector-by-sector-clone-ssd-7201.html)", и нажмите кнопку "Подтвердить", чтобы продолжить, если нет проблем.

[![confirm](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/confirm.png)

Здесь вы также можете нажать кнопку "Настройки", чтобы настроить размер раздела на целевом диске или установить флажок "[4k выравнивание](https://www.diskpart.com/articles/ssd-4k-alignment.html)" для повышения скорости чтения и записи на SSD.

[![edit-disk](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/edit-disk.png)

**△[Копирование без изменения размеров разделов](https://www.diskpart.com/articles/copy-partitions-without-resize-1503.html):** Конфигурация исходного диска будет скопирована на новый диск с тем же размером раздела.
**△ Вписать разделы весь диск:** Разделы на исходном диске займут весь целевой диск.
**△ Редактировать разделы на этом диске:** Позволяет вручную настроить размеры разделов и установить нужный размер.

Шаг 5. Вернувшись на главный экран, проверьте ожидающую операцию и нажмите "Применить" и "Выполнить", чтобы выполнить операцию.

[![apply](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](https://www.diskpart.com/screenshot/en/pro/clone-disk/apply.png)

## Вывод

В этом тексте вы узнали, как использовать Clonezilla для клонирования большого диска на меньший и получить альтернативу Clonezilla - AOMEI Partition Assistant Professional.

Если вы опытный пользователь, можете скачать Clonezilla, создать загрузочный USB-накопитель с Clonezilla и начать клонирование на меньший диск с помощью Clonezilla. Но если вы новичок или столкнулись с проблемой остановки клонирования в Clonezilla, вы можете воспользоваться программным обеспечением AOMEI для завершения клонирования.

Кроме того, AOMEI Partition Assistant имеет множество функций, которые вас могут заинтересовать: [удаление больших файлов](https://www.diskpart.com/free-up-space/how-to-delete-big-files-in-windows-11-1503.html) для освобождения места, перемещение приложений/папок с одного диска на другой, [расширение диска C](https://www.diskpart.com/windows-10/extend-c-drive-windows-10-0528.html) для повышения производительности и многое другое.

![Tracy](/assets/images/author/tracy.png)

[Tracy](https://www.diskpart.com/author/aomei.html) · Штатный редактор

Tracy является членом команды писателей AOMEI. Будучи техническим писателем, она с энтузиазмом делится советами, чтобы помочь читателям в решении сложных вопросов управления дисками, передачи файлов, оптимизации производительности ПК с Windows и т.д., как эксперт.

**********

[диски](/tags/diski.md)
