# Перезапуск Systemd = всегда не соблюдается

Вы можете указать повторить попытку через `x` секунд в разделе `[Service]`,

```
[Service]
Type=simple
Restart=always
RestartSec=3
ExecStart=/path/to/script

```

После сохранения файла вам необходимо перезагрузить конфигурации демона, чтобы гарантировать, что `systemd` знает о новом файле,

```
systemctl daemon-reload

```

затем перезапустите службу, чтобы включить изменения,

```
systemctl restart test

```

* * *

Как вы просили, глядя на документацию,

```
Restart=on-failure

```

звучит как достойная рекомендация.

**********
[service](/tags/service.md)
[systemd](/tags/systemd.md)
[unit](/tags/unit.md)
