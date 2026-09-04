# Какие правила добавить в /etc/gai.conf

Источник: [Finding out what rules to add to /etc/gai.conf](https://blog.bilak.info/2022/04/15/finding-out-what-rules-to-add-to-etc-gai-conf/)

riyad · 15 апреля 2022 (обновлено 14 декабря 2025)

У меня возникла странная проблема. Я [использовал трансляцию сетевого префикса (Network Prefix Translation, NPT) для маршрутизации IPv6-пакетов в интернет через VPN](https://blog.bilak.info/2022/04/03/routing-my-way-out-with-ipv6-npt6/). Но хотя все устройства могли без проблем подключаться к IPv6-интернету, сами по себе они этого никогда не делали. Когда у них был выбор, они всегда предпочитали IPv4-соединения. 🤨

## Предыстория проблемы

Я знал, что современные сетевые стеки в целом настроены предпочитать IPv6 вместо IPv4, но был в недоумении, почему он не использует IPv6, раз соединения с интернетом явно работают. Небольшая возня показала, что IPv4-соединения с интернетом предпочитаются только когда у моего устройства нет **глобальных** IPv6-адресов. Поскольку я полагался на [NPT](https://en.wikipedia.org/wiki/IPv6-to-IPv6_Network_Prefix_Translation), у моих устройств были только [ULA](https://en.wikipedia.org/wiki/Unique_local_address).

Оказывается, [мудрые люди, создающие стандарты](https://www.ietf.org/), решили, что когда у устройства есть только приватные IPv4-адреса и ULA, для интернета предпочитаются IPv4-соединения — исходя из предположения, что приватные IPv4-адреса определённо проходят через [NAT](https://en.wikipedia.org/wiki/Network_address_translation), а ULA в IPv6, вероятно (_определённо_?) — нет. 😯

## Поиск решения

Быстрый поиск по всему, что связано с приоритетом IPv4 против IPv6, приводит исключительно к вопросам и постам, авторы которых хотят, чтобы IPv4 всегда имел приоритет над IPv6. Хотя мой случай был обратным, стало ясно одно: дело в изменении файла [/etc/gai.conf](https://manpages.ubuntu.com/manpages/impish/en/man5/gai.conf.5.html). Это файл для настройки [RFC 6724 (Default Address Selection for Internet Protocol Version 6 (IPv6))](https://www.rfc-editor.org/rfc/rfc6724.html).

Это позволило мне повлиять на алгоритм выбора, что, казалось, и требовалось для решения моей проблемы. Если открыть этот файл, в нём даже есть закомментированные строки для решения проблемы «всегда предпочитать IPv4 вместо IPv6». Обратный случай оказался не так прост: среди правил `precedence` не было диапазона адресов для ULA, а добавление такого для моего конкретного ULA тоже не решило проблему:

```text
[...]
# precedence  <mask>   <value>
#    Add another rule to the RFC 3484 precedence table.  See section 2.1
#    and 10.3 in RFC 3484.  The default is:
#
precedence  ::1/128       50
precedence  ::/0          40
precedence  2002::/16     30
precedence ::/96          20
precedence ::ffff:0:0/96  10
precedence 3fff:01:23::/48  45  # <-- added my ULA, but didn't help
#
#    For sites which prefer IPv4 connections change the last line to
#
#precedence ::ffff:0:0/96  100
[...]
```

## Алгоритм вручную

Я попытался сделать шаг назад и выяснить, было ли изменение настройки `precedence` вообще правильным решением. Я собрался с духом и попытался вручную вычислить алгоритм [«Source Address Selection» из RFC 6725 (раздел 5)](https://www.rfc-editor.org/rfc/rfc6724.html#section-5).

#### Адреса-кандидаты

Моими адресами-кандидатами для назначения (этот сервер) были:

```text
2a01:4f8:c2c:8101::1   # native IPv6
::ffff:116.203.176.52  # native IPv4 (mapped to IPv6 for this algorithm)
```

Мои адреса-кандидаты источника (из моего WLAN-подключения) выглядели так:

```text
3fff:01:23::aa  # global dynamic noprefixroute
3fff:01:23::bb  # global temporary dynamic
3fff:01:23::cc  # global mngtmpaddr noprefixroute
::ffff:10.0.0.50  # private IPv4 (mapped to IPv6 for this algorithm)
```

#### Правила

```text
Rule 1: Prefer same address.
```

пропускаем, источник и назначение не совпадают.

```text
Rule 2: Prefer appropriate scope.
```

пропускаем, соединение unicast, так что никакого multicast.

```text
Rule 3: Avoid deprecated addresses.
```

пропускаем, устаревшие адреса источника не используются.

```text
Rule 4: Prefer home addresses.
```

пропустить? Я не был уверен, чем должен быть «домашний адрес» (home address), но, похоже, это связано с мобильными сетями. Я просто предположил, что все адреса источника являются «домашними».

```text
Rule 5: Prefer outgoing interface.
```

пропускаем, я и так рассматривал здесь только исходящий интерфейс.

```text
Rule 5.5: Prefer addresses in a prefix advertised by the next-hop.
```

пропустить? все next-hop'ы были `fe00::<router's EUI64>`.

```text
Rule 6: Prefer matching label.
```

Берём метки по умолчанию из /etc/gai.conf (мои из Ubuntu 21.10):

```text
[…]
#label ::1/128       0  # loopback address
#label ::/0          1  # IPv6, unless matched by other rules
#label 2002::/16     2  # 6to4 tunnels
#label ::/96         3  # IPv4-compatible addresses (deprecated)
#label ::ffff:0:0/96 4  # IPv4-mapped addresses
#label fec0::/10     5  # site-local addresses (deprecated)
#label fc00::/7      6  # ULAs
#label 2001:0::/32   7  # Teredo tunnels
[…]
```

Тогда адреса назначения получат такие метки:

```text
2a01:4f8:c2c:8101::1   # label 1
::ffff:116.203.176.52  # label 4
```

А адреса источника получат такие метки:

```text
3fff:01:23::aa  # label 6
3fff:01:23::bb  # label 6
3fff:01:23::cc  # label 6
::ffff:10.0.0.50  # label 4
```

Здесь мы видим, почему выбираются IPv4-адреса: их адреса назначения и источника имеют одинаковую метку, а IPv6-адреса — нет. 😔

Значит, я мог добавить новую метку для моего ULA с той же меткой, что у адресов `::/0` (то есть 1 здесь). Я не менял метку в строке `fc00::/7`, чтобы не менять поведение для всех ULA — мне же нужно было специальное правило для моей конкретной сети. Поэтому я раскомментировал строки `label` по умолчанию и добавил следующую строку:

```text
label 3fff:01:23::/48 1  # my ULA prefix and the same label as ::/0
```

Перезагрузка (возможно, не строго обязательная)… и — вот чудо! — это сработало! 😎

## Заключение

Хотя это и сработало, я действительно чувствовал себя неуютно из-за вмешательства в приоритизацию адресов, особенно если учесть, что мне пришлось бы делать это на каждом устройстве. И это поверх уже эзотерической настройки с использованием NPT. 🙈

Позже я выяснил, что когда VPN падает (то есть нет IPv6-связности с интернетом), система не переключится (фактически не сможет переключиться) на IPv4 для интернет-соединения. 😓

**Обновление от 14.12.2025:** используйте [3fff::/20 как документационный префикс](https://www.rfc-editor.org/rfc/rfc9637.html).

**********

[networking](/tags/networking.md)
[dns](/tags/dns.md)
[linux](/tags/linux.md)
[ubuntu](/tags/ubuntu.md)