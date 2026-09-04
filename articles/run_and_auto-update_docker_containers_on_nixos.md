# Запуск и автообновление Docker-контейнеров на NixOS

Источник: [Run and Auto-Update Docker Containers on NixOS](https://nixcademy.com/posts/auto-update-containers/)

Яцек Галович · 21 ноября 2024 · 5 мин чтения

![Run and Auto-Update Docker Containers on NixOS](/images/7a6078ba738f7a8228fd85b3ae66fa31.png)

Изображение сгенерировано ИИ. Контент написан человеком.

Узнайте, как запускать Docker/Podman-контейнеры на NixOS с автоматическим обновлением и очисткой старых образов. Я использую это на Raspberry Pi 4, но код из статьи будет работать на любой системе NixOS.

Год назад я настроил Raspberry Pi 4 для работы с [Home Assistant](https://www.home-assistant.io/) и [дешёвым USB Zigbee-шлюзом](https://www.amazon.de/-/en/dp/B0B6P22YJC?ref=ppx_yo2ov_dt_b_fed_asin_title). Настройка Home Assistant имеет somewhat капризный характер. Тем не менее, он отлично работает с Zigbee-продукциями всех видов — как дорогими, так и дешёвыми: отопительными термостатами, выключателями, датчиками температуры и влажности, лампочками и т. д.

Эта статья не о том, как установить NixOS на Raspberry Pi. Если вы хотите этому научиться, взгляните на [этот очень хороший официальный учебник nix.dev](https://nix.dev/tutorials/nixos/installing-nixos-on-a-raspberry-pi). (Я предлагаю использовать быструю USB3-флешку вместо SD-карты для системного диска.)

Мы будем использовать [оригинальный Docker-образ](https://www.home-assistant.io/installation/alternative#docker-compose) вместо нативных модулей NixOS ([просмотреть опции официального модуля Home Assistant для NixOS можно здесь](https://search.nixos.org/options?channel=unstable&from=0&size=50&sort=relevance&type=packages&query=services.home-assistant.config)), потому что это хороший пример того, как запускать важные сервисы в виде Docker-образа с меньшими хлопотами, чем на других дистрибутивах GNU/Linux. Модули и пакеты NixOS в целом хорошо поддерживаются, но это также интересная альтернатива на случай, если какой-то модуль не настолько свежий, как нам нужно.

## Запуск Home Assistant через Docker на NixOS

Чтобы добавить Docker-образ Home Assistant в конфигурацию нашей системы и заставить его работать как сервис, добавьте этот новый файл модуля NixOS в папку конфигурации:

```nix
# file: homeassistant.nix
{ ... }:

{
  virtualisation.oci-containers = {
    backend = "podman";
    containers.homeassistant = {
      volumes = [ "home-assistant:/config" ];
      environment.TZ = "Europe/Berlin";
      image = "ghcr.io/home-assistant/home-assistant:stable";
      extraOptions = [
        "--network=host"
        "--device=/dev/ttyACM0:/dev/ttyACM0"
      ];
    };
  };

  networking.firewall.allowedTCPPorts = [ 8123 ];
}
```

Модуль добавляет в систему новый контейнер с именем `homeassistant`. `extraOptions` необходимы, чтобы дать ему возможность использовать сеть хоста. Вторая строка пробрасывает наш USB-донгл Zigbee внутрь контейнера. Обратите внимание: ваш Zigbee-донгл может появиться по другому пути `/dev/...` — подстройте конфигурацию соответствующим образом.

Последняя строка про настройки файрвола нужна только в том случае, если ваша конфигурация NixOS устанавливает `networking.firewall.enable = true;`.

Вместо Docker мы используем бэкенд [`podman`](https://podman.io/). Podman интересен на NixOS, потому что он [работает без центрального демона](https://medium.com/@supportfly/podman-vs-docker-a-comprehensive-comparison-77b1b41e67e0) и запускает образы напрямую.

Добавьте этот новый файл модуля в строку `imports = [ ... ];` вашего `configuration.nix` (будь то внутри flake или в `/etc/nixos/`) и пересоберите систему командой `nixos-rebuild switch`.

Теперь вы должны иметь возможность открыть `http://<ip-raspberry>:8123` в браузере и попасть в диалог настройки!

## Автоматическое обновление Home Assistant

У Home Assistant есть некоторые возможности самообновления, но это не то же самое, что обновление Docker-образа и перезапуск сервиса.

Мы можем автоматически обновлять _все_ образы в системе, используя [таймеры systemd](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) и команду `podman pull`:

Создайте ещё один файл модуля NixOS и добавьте его в секцию `imports` вашего `configuration.nix` либо поместите его содержимое в файл модуля, который мы создали ранее.

```nix
# file: update-containers.nix
{ ... }:

{
  systemd.timers.update-containers = {
    timerConfig = {
      Unit = "update-containers.service";
      OnCalendar = "Mon 02:00";
    };
    wantedBy = [ "timers.target" ];
  };
  systemd.services.update-containers = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = lib.getExe (pkgs.writeShellScriptBin "update-containers" ''
        images=$(${pkgs.podman}/bin/podman ps -a --format="{{.Image}}" | sort -u)

        for image in $images; do
          ${pkgs.podman}/bin/podman pull "$image"
        done
      '');
    };
  };
}
```

Каждый понедельник в 2:00 ночи этот таймер systemd запускает обновление всех запущенных образов Podman.

Если вы хотите запустить этот сервис вручную, выполните `sudo systemctl restart update-containers.service`.

Само по себе обновление образов не перезапускает сервис Home Assistant. Для этого мы напишем ещё один таймер systemd:

```nix
# file: restart-homeassistant.nix
{ ... }:

{
  systemd.timers.restart-homeassistant = {
    timerConfig = {
      Unit = "restart-homeassistant.service";
      OnCalendar = "Tue 02:00";
    };
    wantedBy = [ "timers.target" ];
  };
  systemd.services.restart-homeassistant = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.systemd}/bin/systemctl try-restart podman-homeassistant.service";
    };
  };
}
```

Этот модуль перезапускает `podman-homeassistant.service`, который запускает Docker-образ, каждый вторник в 2:00 ночи. Конечно, вы можете установить поле `OnCalendar` на момент времени, более близкий к обновлениям.

Снова сохраните эту часть конфигурации в ещё один файл модуля NixOS, затем добавьте его в секцию `imports` конфигурации NixOS вашей системы или добавьте его содержимое в существующий файл. Затем переключите систему на новую конфигурацию.

## Автоматическая очистка старых образов

Через несколько месяцев в нашей системе может накопиться несколько версий образов Home Assistant, хотя реально мы используем только последнюю. Это расходует место на диске.

Модуль podman для NixOS уже «из коробки» поддерживает периодическую еженедельную очистку (pruning), поэтому нам не нужно писать третий таймер systemd:

```nix
# file: prune-containers.nix
{ ... }:

{
  virtualisation.podman = {
    enable = true;
    autoPrune = {
      enable = true;
      flags = [ "--all" ];
    };
  };
}
```

И снова: добавьте этот новый файл в папку конфигурации и в секцию `imports` вашего модуля конфигурации NixOS либо добавьте его содержимое в существующий модуль NixOS. Затем пересоберите систему командой `nixos-rebuild switch`.

## Резюме

Эта конфигурация NixOS работает на моём Raspberry Pi, спрятанном за полкой, уже год без необходимости присмотра. Я вхожу в систему раз в несколько месяцев, чтобы исправить устаревания формата конфигурации, если таковые есть.

Определения сервисов systemd выглядят повторяющимися и могут быть сокращены разными способами. На [обучении Nixcademy Nix & NixOS 101](https://nixcademy.com) участники учатся писать надёжные, как скала, конфигурации NixOS, а также собственные настраиваемые модули NixOS — с лучшими практиками и практическими упражнениями, выполняемыми вместе с помощью преподавателя, если что-то идёт не так, как ожидалось.

![Jacek Galowicz](/images/b73a86e857d7b2d8d58174f32606fc9c.png)

### Об авторе — Яцек Галович

Яцек — основатель Nixcademy, интересуется функциональным программированием, управлением сложностью и распространением Nix и NixOS по всему миру. Он также написал книгу о C++ и читал университетские лекции о качестве ПО.

**********

[nixos](/tags/nixos.md)
[nix](/tags/nix.md)
[systemd](/tags/systemd.md)