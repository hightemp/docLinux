# Как оптимизировать и сжать JPEG или PNG изображений в Linux командная строка

У вас много изображений, и вы хотите оптимизировать и сжать изображения, не теряя при этом исходного качества, прежде чем загружать их в какое-либо облачное или локальное хранилище? Существует множество приложений с графическим интерфейсом, которые помогут вам оптимизировать изображения. Тем не менее, вот две простые утилиты командной строки для оптимизации изображений:

1. **jpegoptim** - это утилита для оптимизации / сжатия файлов JPEG без потери качества.
2. **OptiPNG** - небольшая программа, которая оптимизирует изображения PNG до меньшего размера без потери какой-либо информации.

### Сжатие или оптимизация изображений JPEG из командной строки

 **jpegoptim** - инструмент командной строки, который можно использовать для оптимизации и сжатия файлов JPEG, JPG и JFIF без потери его фактического качества. Этот инструмент поддерживает оптимизацию без потерь, которая основана на оптимизации таблиц Хаффмана.

#### Установите jpegoptim в Linux

Чтобы установить **jpegoptim** в своих системах Linux, выполните следующую команду на своем терминале.

##### Debian и его производных

```console
# apt-get install jpegoptim
$ sudo apt-get install jpegoptim
```

##### В системах на основе RedHat

В системах на основе RPM, таких как **RHEL**, **CentOS**, **Fedora** и т. Д., Вам необходимо [установить и включить репозиторий EPEL](https://www.tecmint.com/how-to- enable-epel-repository-for-rhel-centos-6-5 /) или, альтернативно, вы можете установить репозиторий epel непосредственно из командной строки, как показано ниже:

```console
# yum install epel-release
# dnf install epel-release    \[On  **Fedora 22+**  versions\]
```

Затем установите программу jpegoptim из репозитория, как показано ниже:

```console
# yum install jpegoptim
# dnf install jpegoptim    \[On  **Fedora 22+**  versions\]
```

#### Как использовать Jpegoptim Image Optimizer

Синтаксис jpegoptm:

```console
$ jpegoptim filename.jpeg
$ jpegoptim \[options\] filename.jpeg
```

Теперь давайте сжимаем следующее изображение `tecmint.jpeg`, но прежде чем оптимизировать изображение, сначала узнайте фактический размер изображения с помощью команды [du command](https://www.tecmint.com/check-linux- использование диска и файлов / каталогов /), как показано на рисунке.

```console
$ du -sh tecmint.jpeg 

6.2M	tecmint.jpeg
```

Здесь фактический размер файла **6,2 МБ**, теперь сожмите этот файл, выполнив:

```console
$ jpegoptim tecmint.jpeg 
```

 [ ![Оптимизируйте изображение JPEG в Linux](/images/e747ec58ecc03bef96d6faf8c8e3ff8d.png) ](https://www.tecmint.com/wp-content/uploads/2016/01/Optimize-JPEG-Image-in-Linux.png) 

Оптимизируйте изображение JPEG в Linux

Откройте сжатое изображение в любом приложении для просмотра изображений, вы не найдете каких-либо серьезных отличий. Исходное и сжатое изображения будут иметь одинаковое качество.

Приведенная выше команда оптимизирует изображения до максимально возможного размера. Тем не менее, вы можете сжать данное изображение до определенного размера, но это отключает оптимизацию без потерь.

Например, давайте сжимаем выше изображения с **5,6 МБ** до **250k**.

```console
$ jpegoptim --size=250k tecmint.jpeg
```

 [ ![Оптимизировать размер изображения Fix](/images/66b123f55ebecd423d377c5dba495fcd.png) ](https://www.tecmint.com/wp-content/uploads/2016/01/Optimize-Image-Fix-Size.png) 

Оптимизировать размер изображения Fix

#### Пакетное сжатие и оптимизация изображений JPEG

Вы можете спросить, как сжать изображения во всем каталоге, это тоже не сложно. Перейдите в каталог, где у вас есть изображения.

```console
tecmint@tecmint \~ $ cd img/
tecmint@tecmint \~/img $ ls -l
total 65184
-rwxr----- 1 tecmint tecmint 6680532 Jan 19 12:21 DSC\_0310.JPG
-rwxr----- 1 tecmint tecmint 6846248 Jan 19 12:21 DSC\_0311.JPG
-rwxr----- 1 tecmint tecmint 7174430 Jan 19 12:21 DSC\_0312.JPG
-rwxr----- 1 tecmint tecmint 6514309 Jan 19 12:21 DSC\_0313.JPG
-rwxr----- 1 tecmint tecmint 6755589 Jan 19 12:21 DSC\_0314.JPG
-rwxr----- 1 tecmint tecmint 6789763 Jan 19 12:21 DSC\_0315.JPG
-rwxr----- 1 tecmint tecmint 6958387 Jan 19 12:21 DSC\_0316.JPG
-rwxr----- 1 tecmint tecmint 6463855 Jan 19 12:21 DSC\_0317.JPG
-rwxr----- 1 tecmint tecmint 6614855 Jan 19 12:21 DSC\_0318.JPG
-rwxr----- 1 tecmint tecmint 5931738 Jan 19 12:21 DSC\_0319.JPG
```

А затем выполните следующую команду, чтобы сжать все изображения одновременно.

```console
tecmint@tecmint \~/img $ jpegoptim \*.JPG
DSC\_0310.JPG 6000x4000 24bit N Exif  \[OK\] 6680532 --> 5987094 bytes (10.38%), optimized.
DSC\_0311.JPG 6000x4000 24bit N Exif  \[OK\] 6846248 --> 6167842 bytes (9.91%), optimized.
DSC\_0312.JPG 6000x4000 24bit N Exif  \[OK\] 7174430 --> 6536500 bytes (8.89%), optimized.
DSC\_0313.JPG 6000x4000 24bit N Exif  \[OK\] 6514309 --> 5909840 bytes (9.28%), optimized.
DSC\_0314.JPG 6000x4000 24bit N Exif  \[OK\] 6755589 --> 6144165 bytes (9.05%), optimized.
DSC\_0315.JPG 6000x4000 24bit N Exif  \[OK\] 6789763 --> 6090645 bytes (10.30%), optimized.
DSC\_0316.JPG 6000x4000 24bit N Exif  \[OK\] 6958387 --> 6354320 bytes (8.68%), optimized.
DSC\_0317.JPG 6000x4000 24bit N Exif  \[OK\] 6463855 --> 5909298 bytes (8.58%), optimized.
DSC\_0318.JPG 6000x4000 24bit N Exif  \[OK\] 6614855 --> 6016006 bytes (9.05%), optimized.
DSC\_0319.JPG 6000x4000 24bit N Exif  \[OK\] 5931738 --> 5337023 bytes (10.03%), optimized.
```

Вы также можете сжать несколько выбранных изображений одновременно:

```console
$ jpegoptim DSC\_0310.JPG DSC\_0311.JPG DSC\_0312.JPG
DSC\_0310.JPG 6000x4000 24bit N Exif  \[OK\] 6680532 --> 5987094 bytes (10.38%), optimized.
DSC\_0311.JPG 6000x4000 24bit N Exif  \[OK\] 6846248 --> 6167842 bytes (9.91%), optimized.
DSC\_0312.JPG 6000x4000 24bit N Exif  \[OK\] 7174430 --> 6536500 bytes (8.89%), optimized.
```

Более подробную информацию об инструменте **jpegoptim** можно найти на страницах руководства.

```console
$ man jpegoptim 
```

### Сжатие или оптимизация изображений PNG из командной строки

 **OptiPNG** - инструмент командной строки, используемый для оптимизации и сжатия файлов PNG (переносимая сетевая графика) без потери исходного качества.

Установка и использование **OptiPNG** очень похожи на **jpegoptim**.

#### Установите OptiPNG в Linux

Чтобы установить **OptiPNG** в своих системах Linux, выполните следующую команду на своем терминале.

##### Debian и его производных

```console
# apt-get install optipng
$ sudo apt-get install optipng
```

##### В системах на основе RedHat

```console
# yum install optipng
# dnf install optipng    \[On Fedora  **22+**  versions\]
```

**Примечание**: Для установки программы **optipng** у вас должно быть включено **хранилище epel** в ваших системах на основе **RHEL / CentOS**.

#### Как использовать Оптимизатор изображений OptiPNG

Общий синтаксис **optipng**:

```console
$ optipng filename.png
$ optipng \[options\] filename.png
```

Давайте сжимаем изображение `tecmint.png`, но перед оптимизацией сначала проверим фактический размер изображения, как показано:

```console
tecmint@tecmint \~/img $ ls -lh tecmint.png 
-rw------- 1 tecmint tecmint  **350K**  Jan 19 12:54 tecmint.png
```

Здесь фактический размер файла выше изображения **350K**, теперь сожмите этот файл, запустив:

```console
tecmint@tecmint \~/img $ optipng tecmint.png
OptiPNG 0.6.4: Advanced PNG optimizer.
Copyright (C) 2001-2010 Cosmin Truta.

** Processing: tecmint.png
1493x914 pixels, 4x8 bits/pixel, RGB+alpha
Reducing image to 3x8 bits/pixel, RGB
Input IDAT size = 357525 bytes
Input file size = 358098 bytes

Trying:
  zc = 9  zm = 8  zs = 0  f = 0		IDAT size = 249211
                               
Selecting parameters:
  zc = 9  zm = 8  zs = 0  f = 0		IDAT size = 249211

Output IDAT size = 249211 bytes (108314 bytes decrease)
Output file size = 249268 bytes (108830 bytes = 30.39% decrease)
```

Как видно из вышеприведенного вывода, размер файла **tecmint.png** был уменьшен до **30,39%**. Теперь проверьте размер файла еще раз, используя:

```console
tecmint@tecmint \~/img $ ls -lh tecmint.png
-rw-r--r-- 1 tecmint tecmint  **244K**  Jan 19 12:56 tecmint.png
```

Откройте сжатое изображение в любом приложении для просмотра изображений, вы не найдете каких-либо существенных различий между исходным и сжатым файлами. Исходное и сжатое изображения будут иметь одинаковое качество.

#### Пакетное сжатие и оптимизация изображений PNG

Чтобы сжать пакетные или несколько изображений PNG одновременно, просто перейдите в каталог, в котором находятся все изображения, и выполните следующую команду для сжатия.

```console
tecmint@tecmint \~ $ cd img/
tecmint@tecmint \~/img $ optipng \*.png

OptiPNG 0.6.4: Advanced PNG optimizer.
Copyright (C) 2001-2010 Cosmin Truta.

** Processing: Debian-8.png
720x345 pixels, 3x8 bits/pixel, RGB
Input IDAT size = 95151 bytes
Input file size = 95429 bytes

Trying:
  zc = 9  zm = 8  zs = 0  f = 0		IDAT size = 81388
                               
Selecting parameters:
  zc = 9  zm = 8  zs = 0  f = 0		IDAT size = 81388

Output IDAT size = 81388 bytes (13763 bytes decrease)
Output file size = 81642 bytes (13787 bytes = 14.45% decrease)

** Processing: Fedora-22.png
720x345 pixels, 4x8 bits/pixel, RGB+alpha
Reducing image to 3x8 bits/pixel, RGB
Input IDAT size = 259678 bytes
Input file size = 260053 bytes

Trying:
  zc = 9  zm = 8  zs = 0  f = 5		IDAT size = 222479
  zc = 9  zm = 8  zs = 1  f = 5		IDAT size = 220311
  zc = 1  zm = 8  zs = 2  f = 5		IDAT size = 216744
                               
Selecting parameters:
  zc = 1  zm = 8  zs = 2  f = 5		IDAT size = 216744

Output IDAT size = 216744 bytes (42934 bytes decrease)
Output file size = 217035 bytes (43018 bytes = 16.54% decrease)
....
```

Для получения более подробной информации о **optipng** проверьте справочные страницы.

```console
$ man optipng
```


**********
[CentOS](/tags/CentOS.md)
[Ubuntu](/tags/Ubuntu.md)
[jpegoptim](/tags/jpegoptim.md)
[OptiPNG](/tags/OptiPNG.md)
[epel](/tags/epel.md)
[RHEL](/tags/RHEL.md)
