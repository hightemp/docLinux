# Как оптимизировать и сжать JPEG или PNG изображений в Linux командная строка

You have a lot of images, and want to optimize and compress the images without losing its original quality before uploading them to any cloud or local storages? There are plenty of GUI applications available which will help you to optimize the images. However, here are two simple command line utilities to optimize images and they are:

1.   **jpegoptim** – is a utility to optimize/compress JPEG files without loosing quality.
2.   **OptiPNG** – is a small program that optimize PNG images to smaller size without losing any information.

### Compress or Optimize JPEG Images from Command Line

 **jpegoptim** is a command line tool that can be used to optimize and compress JPEG, JPG and JFIF files without losing its actual quality. This tool supports lossless optimization, which is based on optimizing the Huffman tables.

#### Install jpegoptim in Linux

To install **jpegoptim** on your Linux systems, run the following command from your terminal.

##### On Debian and it’s Derivatives

```console
# apt-get install jpegoptim
$ sudo apt-get install jpegoptim
```

##### On RedHat based Systems

On RPM based systems like **RHEL** , **CentOS** , **Fedora** etc., you need to [install and enable EPEL repository](https://www.tecmint.com/how-to-enable-epel-repository-for-rhel-centos-6-5/) or alternatively, you can install the epel repository directly from the commandline as shown:

```console
# yum install epel-release
# dnf install epel-release    \[On  **Fedora 22+**  versions\]
```

Next install jpegoptim program from the repository as shown:

```console
# yum install jpegoptim
# dnf install jpegoptim    \[On  **Fedora 22+**  versions\]
```

#### How to Use Jpegoptim Image Optimizer

The syntax of jpegoptm is:

```console
$ jpegoptim filename.jpeg
$ jpegoptim \[options\] filename.jpeg
```

Let’s now compress the following `tecmint.jpeg` image, but before optimizing the image, first find out the actual size of the image using [du command](https://www.tecmint.com/check-linux-disk-usage-of-files-and-directories/) as shown.

```console
$ du -sh tecmint.jpeg 
```

 **6.2M	tecmint.jpeg** 

Here the actual file size is **6.2MB** , now compress this file by running:

```console
$ jpegoptim tecmint.jpeg 
```

 [ ![Optimize JPEG Image in Linux](/images/e747ec58ecc03bef96d6faf8c8e3ff8d.png) ](https://www.tecmint.com/wp-content/uploads/2016/01/Optimize-JPEG-Image-in-Linux.png) 

Optimize JPEG Image in Linux

Open the compressed image in any image viewer application, you will not find any major differences. The source and compressed images will have the same quality.

The above command optimizes the images to the maximum possible size. However, you can compress the given image to a specific size to, but it disables the lossless optimization.

For example, let us compress above the image from **5.6MB** to around **250k** .

```console
$ jpegoptim --size=250k tecmint.jpeg
```

 [ ![Optimize Image Fix Size](/images/66b123f55ebecd423d377c5dba495fcd.png) ](https://www.tecmint.com/wp-content/uploads/2016/01/Optimize-Image-Fix-Size.png) 

Optimize Image Fix Size

#### Batch JPEG Image Compression and Optimization

You might ask how to compress the images in the entire directory, that’s not difficult too. Go to the directory where you have the images.

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

And then run the following command to compress all images at once.

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

You can also compress multiple selected images at once:

```console
$ jpegoptim DSC\_0310.JPG DSC\_0311.JPG DSC\_0312.JPG
DSC\_0310.JPG 6000x4000 24bit N Exif  \[OK\] 6680532 --> 5987094 bytes (10.38%), optimized.
DSC\_0311.JPG 6000x4000 24bit N Exif  \[OK\] 6846248 --> 6167842 bytes (9.91%), optimized.
DSC\_0312.JPG 6000x4000 24bit N Exif  \[OK\] 7174430 --> 6536500 bytes (8.89%), optimized.
```

For more details about **jpegoptim** tool, check out the man pages.

```console
$ man jpegoptim 
```

### Compress or Optimize PNG Images from Command Line

 **OptiPNG** is a command line tool used to optimize and compress PNG (portable network graphics) files without losing its original quality.

The installation and usage of **OptiPNG** is very similar to **jpegoptim** .

#### Install OptiPNG in Linux

To install **OptiPNG** on your Linux systems, run the following command from your terminal.

##### On Debian and it’s Derivatives

```console
# apt-get install optipng
$ sudo apt-get install optipng
```

##### On RedHat based Systems

```console
# yum install optipng
# dnf install optipng    \[On Fedora  **22+**  versions\]
```

 **Note** : You must have **epel repository** enabled on your **RHEL/CentOS** based systems to install **optipng** program.

#### How to Use OptiPNG Image Optimizer

The general syntax of **optipng** is:

```console
$ optipng filename.png
$ optipng \[options\] filename.png
```

Let us compress the `tecmint.png` image, but before optimizing, first check the actual size of the image as shown:

```console
tecmint@tecmint \~/img $ ls -lh tecmint.png 
-rw------- 1 tecmint tecmint  **350K**  Jan 19 12:54 tecmint.png
```

Here the actual file size of above image is **350K** , now compress this file by running:

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

As you see in the above output, the size of the **tecmint.png** file has been reduced up to **30.39%** . Now verify the file size again using:

```console
tecmint@tecmint \~/img $ ls -lh tecmint.png
-rw-r--r-- 1 tecmint tecmint  **244K**  Jan 19 12:56 tecmint.png
```

Open the compressed image in any image viewer application, you will not find any major differences between the original and compressed files. The source and compressed images will have the same quality.

#### Batch PNG Image Compression and Optimization

To compress batch or multiple PNG images at once, just go the directory where all images resides and run the following command to compress.

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

For more details about **optipng** check man pages.

```console
$ man optipng
```

**********
[CentOS](/tags/CentOS.md)
[jpegoptim](/tags/jpegoptim.md)
[OptiPNG](/tags/OptiPNG.md)
