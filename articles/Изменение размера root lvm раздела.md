## Изменение размера root lvm раздела

### Подготовим временный раздел 

```bash
pvcreate /dev/sdb
vgcreate vg_root /dev/sdb
lvcreate -n lv_root -l +100%FREE /dev/vg_root
```

### Создадим на нем файловую систему и смонтируем его, чтобы перенести туда данные

```bash
mkfs.xfs /dev/vg_root/lv_root
mount /dev/vg_root/lv_root /mnt
```

### Этой командой скопируем все данные с / раздела в /mnt

```bash
xfsdump -J - /dev/VolGroup00/LogVol00 | xfsrestore -J - /mnt
```

### Затем переконфигурируем grub для того, чтобы при старте перейти в новый /

Сымитируем текущий root -> сделаем в него chroot и обновим grub:

```bash
for i in /proc/ /sys/ /dev/ /run/ /boot/; do mount --bind $i /mnt/$i; done
chroot /mnt/
grub2-mkconfig -o /boot/grub2/grub.cfg
```

> Generating grub configuration file ...                                          
> Found linux image: /boot/vmlinuz-3.10.0-862.2.3.el7.x86_64               
> Found initrd image: /boot/initramfs-3.10.0-862.2.3.el7.x86_64.img
> done


**********
[LVM](/tags/LVM.md)
[root](/tags/root.md)
