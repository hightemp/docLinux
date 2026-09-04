# Rolling-релизы VyOS

Источник: [VyOS rolling release](https://vyos.net/get/nightly-builds/)

Сборки rolling-релизов VyOS автоматически создаются из ветки `current` минимум раз в день.

Они включают весь новейший код от мейнтейнеров и участников сообщества.

Сборки rolling-релиза не тестируются вручную перед выкладкой. Они проходят последовательность автоматических [smoke-тестов](https://github.com/vyos/vyos-1x/tree/current/smoketest/scripts/cli). Кроме того, мы загружаем произвольные [конфигурации](https://github.com/vyos/vyos-1x/tree/current/smoketest/configs), чтобы убедиться в отсутствии ошибок при миграции конфигурации и загрузке системы.

## Проверка подписей образов

Мы используем [minisign](https://jedisct1.github.io/minisign/) для подписи релизов. Чтобы узнать о его преимуществах перед GPG, прочитайте [signify: Securing OpenBSD From Us To You](https://www.openbsd.org/papers/bsdcan-signify.html).

Одно очевидное преимущество состоит в том, что вам не нужно никуда импортировать ключ — его можно передать как аргумент командной строки. Загрузив образ и его файл `.minisig`, вы можете проверить его целостность этой командой:

```text
minisign -Vm <ISO file> -P RWSIhkR/dkM2DSaBRniv/bbbAf8hmDqdbOEmgXkf1RxRoxzodgKcDyGq
```

Если сомневаетесь, вы можете получить публичный ключ из [репозитория ночных сборок](https://github.com/vyos/vyos-nightly-build/blob/main/minisign.pub). Если вы сомневаетесь _по-настоящему_ (то есть у вас есть основания подозревать, что репозиторий и/или этот сайт были скомпрометированы), вам следует сообщить об этом мейнтейнерам.

В настоящее время мы создаём сборки rolling-релизов с помощью GitHub Actions и храним их в релизах репозитория [vyos/vyos-nightly-build](https://github.com/vyos/vyos-nightly-build/releases). Вот автоматически сгенерированный список доступных сборок.

## Доступные сборки

  * [2026.09.01-0034-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.09.01-0034-rolling/vyos-2026.09.01-0034-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.09.01-0034-rolling/vyos-2026.09.01-0034-rolling-generic-amd64.iso.minisig))
  * [2026.08.31-0032-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.31-0032-rolling/vyos-2026.08.31-0032-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.31-0032-rolling/vyos-2026.08.31-0032-rolling-generic-amd64.iso.minisig))
  * [2026.08.28-0255-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.28-0255-rolling/vyos-2026.08.28-0255-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.28-0255-rolling/vyos-2026.08.28-0255-rolling-generic-amd64.iso.minisig))
  * [2026.08.27-1219-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.27-1219-rolling/vyos-2026.08.27-1219-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.27-1219-rolling/vyos-2026.08.27-1219-rolling-generic-amd64.iso.minisig))
  * [2026.08.27-0133-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.27-0133-rolling/vyos-2026.08.27-0133-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.27-0133-rolling/vyos-2026.08.27-0133-rolling-generic-amd64.iso.minisig))
  * [2026.08.26-1406-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.26-1406-rolling/vyos-2026.08.26-1406-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.26-1406-rolling/vyos-2026.08.26-1406-rolling-generic-amd64.iso.minisig))
  * [2026.08.25-0014-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.25-0014-rolling/vyos-2026.08.25-0014-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.25-0014-rolling/vyos-2026.08.25-0014-rolling-generic-amd64.iso.minisig))
  * [2026.08.22-0013-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.22-0013-rolling/vyos-2026.08.22-0013-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.22-0013-rolling/vyos-2026.08.22-0013-rolling-generic-amd64.iso.minisig))
  * [2026.08.21-0014-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.21-0014-rolling/vyos-2026.08.21-0014-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.21-0014-rolling/vyos-2026.08.21-0014-rolling-generic-amd64.iso.minisig))
  * [2026.08.19-0012-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.19-0012-rolling/vyos-2026.08.19-0012-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.19-0012-rolling/vyos-2026.08.19-0012-rolling-generic-amd64.iso.minisig))
  * [2026.08.18-1030-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.18-1030-rolling/vyos-2026.08.18-1030-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.18-1030-rolling/vyos-2026.08.18-1030-rolling-generic-amd64.iso.minisig))
  * [2026.08.14-0025-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.14-0025-rolling/vyos-2026.08.14-0025-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.14-0025-rolling/vyos-2026.08.14-0025-rolling-generic-amd64.iso.minisig))
  * [2026.08.13-0024-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.13-0024-rolling/vyos-2026.08.13-0024-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.13-0024-rolling/vyos-2026.08.13-0024-rolling-generic-amd64.iso.minisig))
  * [2026.08.12-0831-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.12-0831-rolling/vyos-2026.08.12-0831-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.12-0831-rolling/vyos-2026.08.12-0831-rolling-generic-amd64.iso.minisig))
  * [2026.08.05-0033-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.05-0033-rolling/vyos-2026.08.05-0033-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.05-0033-rolling/vyos-2026.08.05-0033-rolling-generic-amd64.iso.minisig))
  * [2026.08.04-0035-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.04-0035-rolling/vyos-2026.08.04-0035-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.08.04-0035-rolling/vyos-2026.08.04-0035-rolling-generic-amd64.iso.minisig))
  * [2026.07.30-0032-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.30-0032-rolling/vyos-2026.07.30-0032-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.30-0032-rolling/vyos-2026.07.30-0032-rolling-generic-amd64.iso.minisig))
  * [2026.07.29-0032-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.29-0032-rolling/vyos-2026.07.29-0032-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.29-0032-rolling/vyos-2026.07.29-0032-rolling-generic-amd64.iso.minisig))
  * [2026.07.28-0034-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.28-0034-rolling/vyos-2026.07.28-0034-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.28-0034-rolling/vyos-2026.07.28-0034-rolling-generic-amd64.iso.minisig))
  * [2026.07.21-1151-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.21-1151-rolling/vyos-2026.07.21-1151-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.21-1151-rolling/vyos-2026.07.21-1151-rolling-generic-amd64.iso.minisig))
  * [2026.07.11-0033-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.11-0033-rolling/vyos-2026.07.11-0033-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.11-0033-rolling/vyos-2026.07.11-0033-rolling-generic-amd64.iso.minisig))
  * [2026.07.10-1446-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.10-1446-rolling/vyos-2026.07.10-1446-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.07.10-1446-rolling/vyos-2026.07.10-1446-rolling-generic-amd64.iso.minisig))
  * [2026.06.30-0048-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.30-0048-rolling/vyos-2026.06.30-0048-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.30-0048-rolling/vyos-2026.06.30-0048-rolling-generic-amd64.iso.minisig))
  * [2026.06.24-0045-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.24-0045-rolling/vyos-2026.06.24-0045-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.24-0045-rolling/vyos-2026.06.24-0045-rolling-generic-amd64.iso.minisig))
  * [2026.06.23-0048-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.23-0048-rolling/vyos-2026.06.23-0048-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.23-0048-rolling/vyos-2026.06.23-0048-rolling-generic-amd64.iso.minisig))
  * [2026.06.22-0055-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.22-0055-rolling/vyos-2026.06.22-0055-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.22-0055-rolling/vyos-2026.06.22-0055-rolling-generic-amd64.iso.minisig))
  * [2026.06.20-0050-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.20-0050-rolling/vyos-2026.06.20-0050-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.20-0050-rolling/vyos-2026.06.20-0050-rolling-generic-amd64.iso.minisig))
  * [2026.06.19-0100-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.19-0100-rolling/vyos-2026.06.19-0100-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.19-0100-rolling/vyos-2026.06.19-0100-rolling-generic-amd64.iso.minisig))
  * [2026.06.18-0055-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.18-0055-rolling/vyos-2026.06.18-0055-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.18-0055-rolling/vyos-2026.06.18-0055-rolling-generic-amd64.iso.minisig))
  * [2026.06.17-0055-rolling](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.17-0055-rolling/vyos-2026.06.17-0055-rolling-generic-amd64.iso) ([sig](https://github.com/vyos/vyos-nightly-build/releases/download/2026.06.17-0055-rolling/vyos-2026.06.17-0055-rolling-generic-amd64.iso.minisig))

**********

[vyos](/tags/vyos.md)
[networking](/tags/networking.md)