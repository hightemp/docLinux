# Команда capsh

Источник: [capsh command](https://linux-audit.com/system-administration/commands/capsh/)

Команда capsh предоставляет оболочку-обёртку для возможностей (capabilities) с целью тестирования возможностей Linux.

_Типичное применение: диагностика проблем с правами доступа, ужесточение безопасности системных служб, анализ бинарных файлов и процессов_

* Установка
  * AlmaLinux
  * Arch Linux
  * Debian
  * Fedora
  * Red Hat Enterprise Linux
  * Rocky Linux
  * openSUSE
  * Ubuntu
* Использование
  * Опции
* Примеры

## Знакомство с capsh

Утилита capsh — очень полезный инструмент в Linux, позволяющий узнать больше о [возможностях Linux](/kernel/capabilities/). Она может отображать активные возможности и показывать информацию о них. Инструмент также способен запускать другие команды, показывая или определяя, какие возможности Linux к ним применимы. Это делает его полезным для широкого круга задач, например для устранения неполадок, а также когда вы хотите глубже разобраться в том, как работают процессы. Эта информация полезна при работе с контейнерами или при укреплении безопасности служб Linux с помощью [настроек юнитов systemd](/systemd/settings/units/), таких как [CapabilityBoundingSet](/systemd/settings/units/capabilityboundingset/).

## Установка

Если capsh не установлен по умолчанию, его можно добавить в систему с помощью соответствующего программного пакета.

### Информация о пакете capsh

Операционная система| Имя пакета| Установка
---|---|---
AlmaLinux| libcap|

```bash
dnf install libcap
```

Arch Linux| libcap|

```bash
pacman -S libcap
```

Debian| libcap2-bin|

```bash
apt install libcap2-bin
```

Fedora| libcap|

```bash
dnf install libcap
```

Red Hat Enterprise Linux| libcap|

```bash
dnf install libcap
```

Rocky Linux| libcap|

```bash
dnf install libcap
```

openSUSE| libcap-progs|

```bash
zypper install libcap-progs
```

Ubuntu| libcap2-bin|

```bash
apt install libcap2-bin
```

В вашем дистрибутиве Linux используется другой пакет? Поделитесь своим [отзывом](/contact/).

## Использование

### Доступные опции

Опция| Описание
---|---
\--addamb=CAPABILITY| Добавить возможность в набор окружающих (ambient) возможностей
\--decode=VALUE| Расшифровать значение связанного с возможностями поля в /proc/PID/status, например CapInh, CapPrm, CapEff, CapBnd, CapAmb
\--delamb=CAPABILITY| Убрать возможность из набора окружающих (ambient) возможностей
\--explain=CAPABILITY| Показать описание выбранной возможности
\--noamb| Сбросить окружающие (ambient) возможности
\--print| Показать текущие возможности, securebits, информацию о пользователе и группе

Не хватает какой-то опции в этом обзоре? Поделитесь своим [отзывом](/contact/).

### Примеры использования capsh

#### Основы

Показать ограничивающий набор возможностей (capability bounding set), набор окружающих возможностей, securebits, идентификатор пользователя и идентификатор группы.

```bash
capsh --print
```

####

Запустить команду и показать связанные с ней сведения о возможностях, защищённые биты, а также информацию о пользователе и группе.

```bash
capsh --print -- -c "sudo ps"
```

#### Вспомогательные и информационные команды

Получить описание выбранной возможности:

```bash
capsh --explain=cap_net_bind_service
```

####

Найти возможность, содержащую определённое слово в своём имени или описании.

```bash
capsh --suggest=port
```

## Часто задаваемые вопросы

Что такое команда capsh и каково её назначение?

Команда capsh — это инструмент командной строки, предоставляющий оболочку-обёртку для возможностей (capabilities). Он помогает тестировать возможности Linux и предоставляет ряд опций для отображения информации, анализа бинарных файлов и процессов, а также диагностики проблем с правами доступа.

Какой пакет предоставляет команду capsh?

Команда capsh поставляется в пакете libcap, libcap-progs или libcap2-bin.

### Статьи, использующие команду capsh

Следующие статьи содержат примеры использования capsh и могут быть полезны для дальнейшего изучения.

* [Настройка SecureBits](/systemd/settings/units/securebits/)
* [Linux capabilities 101](/kernel/capabilities/linux-capabilities-101/)

## Родственные и похожие команды

В Linux доступно множество инструментов и команд, и иногда вам нужно именно чуть другое средство. Вот список команд, похожих на capsh или связанных с ней:

Родственные и похожие команды capshКоманда| Категория| Описание
---|---|---
[captest](/system-administration/commands/captest/)| capabilities| Инструмент тестирования возможностей и повышения привилегий
[filecap](/system-administration/commands/filecap/)| capabilities| Отображение возможностей Linux, установленных на бинарные файлы в путях
[firejail](/system-administration/commands/firejail/)| sandboxing| Инструмент песочницы (sandboxing) для Linux
[getcap](/system-administration/commands/getcap/)| capabilities| Показать возможности файла
[getpcaps](/system-administration/commands/getpcaps/)| capabilities| Показать возможности процесса
[netcap](/system-administration/commands/netcap/)| capabilities| Отображение доступных возможностей для запущенных процессов, использующих сетевые сокеты
[pscap](/system-administration/commands/pscap/)| capabilities| Отображение доступных возможностей для запущенных процессов
[setcap](/system-administration/commands/setcap/)| capabilities| Добавить возможности Linux файлу или удалить их из него

Также 💙 командная строка или терминал? Вот набор шпаргалок по Linux, чтобы успевать больше из оболочки:

* [dig](/cheat-sheets/dig/)
* [pacman](/cheat-sheets/pacman/)
* [run0](/cheat-sheets/run0/)
* [apt](/cheat-sheets/apt/)
* [tcpdump](/cheat-sheets/tcpdump/)
* [dmidecode](/cheat-sheets/dmidecode/)
* [tar](/cheat-sheets/tar/)
* [ip](/cheat-sheets/ip/)
* [lsof](/cheat-sheets/lsof/)
* [ss](/cheat-sheets/ss/)
* [du](/cheat-sheets/du/)
* [find](/cheat-sheets/find/)
* [systemctl](/cheat-sheets/systemctl/)
* [journalctl](/cheat-sheets/journalctl/)
* [curl](/cheat-sheets/curl/)
* [awk](/cheat-sheets/awk/)
* [strace](/cheat-sheets/strace/)

## Сделайте следующий шаг!

Хотите узнать больше о безопасности Linux? Взгляните на инструмент с открытым исходным кодом Lynis и станьте экспертом по безопасности Linux сами.

### Lynis

Lynis — проверенный в боях инструмент технического аудита безопасности для систем на базе Unix. Он с открытым исходным кодом, свободно доступен и используется системными администраторами по всему миру. Среди других пользователей — специалисты по безопасности, пентестеры и ИТ-аудиторы.

### Информация об инструменте

* Стоимость: Бесплатно
* Лицензия: GPLv3
* Ссылки
  * [GitHub-проект](https://github.com/CISOfy/lynis)
  * [Пакеты (deb/rpm)](https://packages.cisofy.com/)
  * [Tarball](https://cisofy.com/downloads/lynis/)

[Посетить страницу проекта](https://cisofy.com/lynis/)

**********

[capabilities](/tags/capabilities.md)
[linux](/tags/linux.md)
[kernel](/tags/kernel.md)