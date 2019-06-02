# GRUB2 конфигурация

## /etc/default/grub

Часто модифицируемые опции:

* GRUB_CMDLINE_LINUX - параметры ядра
* GRUB_BACKGROUND - фоновая картинка
* GRUB_DEFAULT - пункт меня “по умолчания”
* GRUB_DISABLE_RECOVERY - убирает автогенерация рековери пунктов
* GRUB_PRELOAD_MODULES - переченþ GRUB модулей
* GRUB_TIMEOUT - время в секундах до автовыбора

## Обновление GRUB конфигурации

```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

**********
[grub](/tags/grub.md)
[CentOS](/tags/CentOS.md)
