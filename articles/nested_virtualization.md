# Вложенная виртуализация

## Введение

Виртуальные машины можно запускать внутри других виртуальных машин. Это называется вложенной виртуализацией.[^1]

## Qubes

Запустить VirtualBox, KVM или Qubes внутри Qubes непросто. Разработчики Qubes официально не поддерживают такую конфигурацию, и к Whonix™ она отношения не имеет.

Подробнее о текущем состоянии вложенной виртуализации можно узнать в списках рассылки `qubes-devel` и `qubes-users`. Ищите сообщения по запросам `VirtualBox`, `KVM` и `nested virtualization`.

## KVM

Раздел необходимо дополнить.

- [Вложенная виртуализация в Whonix KVM](https://www.whonix.org/wiki/Dev/KVM#Nested_Virtualization)
- [Обсуждение необходимости 64-битной гостевой системы Whonix](https://forums.whonix.org/t/nested-virtulization-needs-64-bit-whonx-guest)

## VirtualBox внутри VirtualBox

Обязательно измените клавишу хоста: *VirtualBox → Preferences → Input → Host Key*. Клавиши хоста для внешней и внутренней виртуальных машин должны различаться, иначе выйти из внутренней виртуальной машины не получится.

Использование ACPI[^2] и IOAPIC[^3][^4] для всех виртуальных машин значительно ускоряет внутреннюю виртуальную машину. В виртуальных машинах Whonix™ эти параметры включены по умолчанию.

VirtualBox пока не поддерживает VT внутри VT.[^5] Поэтому производительность внутренней виртуальной машины зависит от быстродействия хоста и может быть низкой. Отключите VT во внутренней виртуальной машине: *VirtualBox → правый щелчок по виртуальной машине → Settings → System → Acceleration → снимите флажок Enable VT-x/AMD-V*.

Oracle VM VirtualBox поддерживает вложенную виртуализацию на хостах с процессорами AMD. Эта возможность предоставляет гостевой виртуальной машине доступ к функциям аппаратной виртуализации. Благодаря этому в гостевой системе Oracle VM VirtualBox можно установить гипервизор, например Oracle VM VirtualBox, Oracle VM Server или KVM, а затем создавать и запускать в ней виртуальные машины.

Вложенную виртуализацию можно включить одним из следующих способов:

- В VirtualBox Manager на вкладке *Processor* установите флажок *Enable Nested VT-x/AMD-V*. Чтобы отключить эту возможность, снимите флажок.
- Используйте параметр `--nested-hw-virt` команды `VBoxManage modifyvm`, чтобы включить или отключить вложенную виртуализацию. Подробнее см. в документации по [`VBoxManage modifyvm`](https://docs.oracle.com/cd/E97728_01/E97727/html/vboxmanage-modifyvm.html).

Обсуждение на форуме: [вложенная виртуализация в Whonix VBox — Windows 7 внутри Whonix-WS](https://forums.whonix.org/t/nested-visualization-with-whonix-vbox-windows-7-inside-whonix-ws).

## См. также

- [Другие операционные системы](https://www.whonix.org/wiki/Other_Operating_Systems "Другие операционные системы")

## Примечания

[^1]: [Вложенная виртуализация](http://en.wikipedia.org/wiki/Nested_virtualization)
[^2]: `vboxmanage "Whonix-Workstation" modifyvm --acpi on`
[^3]: *VirtualBox → правый щелчок по виртуальной машине → Settings → System → снимите флажок Enable IO APIC*.
[^4]: `vboxmanage "Whonix-Workstation" modifyvm --ioapic on`
[^5]: [Задача VirtualBox № 4032](https://www.virtualbox.org/ticket/4032)

---

[виртуализация](/tags/virtualization.md)
