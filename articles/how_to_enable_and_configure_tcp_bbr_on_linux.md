# Как включить и настроить TCP BBR в Linux

Источник: [How to Enable and Configure TCP BBR on Linux](https://oneuptime.com/blog/post/2026-03-20-enable-configure-tcp-bbr-linux/view)

Nawaz Dhandala · 20 марта 2026

## Введение

BBR (Bottleneck Bandwidth and RTT) — это алгоритм управления перегрузкой TCP от Google, доступный в ядре Linux 4.9+ при сборке ядра с поддержкой BBR. В отличие от чисто основанных на потерях алгоритмов (CUBIC, Reno), BBR моделирует доступную пропускную способность и минимальный RTT пути, чтобы управлять скоростью отправки. Это может сделать его значительно более эффективным на дальних или зашумлённых каналах, где потери пакетов происходят даже без перегрузки.

## Предварительные требования и установка

```bash
# Проверяем версию ядра (для BBR требуется 4.9+)

uname -r
# Должно показать 4.9 или выше

# Проверяем, доступен ли уже BBR
sysctl net.ipv4.tcp_available_congestion_control | grep bbr

# Если BBR в списке нет, пробуем загрузить модуль и проверяем снова
modprobe tcp_bbr
sysctl net.ipv4.tcp_available_congestion_control | grep bbr

# Если BBR всё ещё нет в списке: ядро слишком старое
# либо BBR не был включён при сборке
# Решение: обновить ядро или собрать с CONFIG_TCP_CONG_BBR=y
# или CONFIG_TCP_CONG_BBR=m
```

## Включение BBR

```bash
# Включаем BBR как алгоритм управления перегрузкой по умолчанию
sysctl -w net.ipv4.tcp_congestion_control=bbr

# Для лучшего результата используйте BBR вместе с qdisc fq (Fair Queue)
sysctl -w net.core.default_qdisc=fq

# Проверяем обе настройки
sysctl net.ipv4.tcp_congestion_control
# net.ipv4.tcp_congestion_control = bbr

sysctl net.core.default_qdisc
# net.core.default_qdisc = fq

# Делаем настройки постоянными
cat >> /etc/sysctl.conf << EOF
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
EOF
sysctl -p

# В Debian/Ubuntu включаем автозагрузку модуля при старте,
# если BBR собран как модуль
echo "tcp_bbr" >> /etc/modules
```

## Почему fq помогает BBR

BBR управляет скоростью отправки через пейсинг (pacing) — отправку пакетов с рассчитанной скоростью вместо отправки их всех разом. В Linux 4.20+ BBR больше не строго требует qdisc `fq` для работы, но `fq` остаётся сильным выбором по умолчанию, поскольку эффективно реализует пейсинг для каждого потока:

```bash
# Смотрим текущий qdisc на каждом интерфейсе
tc qdisc show dev eth0

# На одноочередных интерфейсах применяем fq вручную при необходимости
tc qdisc replace dev eth0 root fq

# sysctl net.core.default_qdisc=fq влияет на qdisc, созданные
# после изменения настройки
# Физические многоочередные NIC сохраняют mq как корневой qdisc
# и используют qdisc по умолчанию для листьев
```

## Проверка, что BBR активен

```bash
# Убеждаемся, что BBR работает на активных соединениях
ss -tin state established | grep "bbr"
# Ищем строку TCP info, начинающуюся с "bbr"

# Более детальная статистика BBR
ss -tin state established | head -5
# Вывод включает:
# имя алгоритма управления перегрузкой в начале строки TCP info
# pacing_rate — текущий темп пейсинга BBR

# Мониторим окно перегрузки BBR во время передачи
watch -n 0.5 'ss -tin state established | grep -E "bbr|cwnd|pacing_rate"'
```

## Тестирование производительности BBR

```bash
# Базовый замер с CUBIC
sysctl -w net.ipv4.tcp_congestion_control=cubic
iperf3 -c 10.20.0.5 -t 30
echo "Результат CUBIC выше"

# Переключаемся на BBR
sysctl -w net.ipv4.tcp_congestion_control=bbr
iperf3 -c 10.20.0.5 -t 30
echo "Результат BBR выше"

# Быстрая симуляция на стороне исходящего трафика с tc netem
# Для реалистичных результатов TCP помещайте netem на путь
# входящего трафика приёмника
tc qdisc add dev eth0 root netem delay 100ms loss 1%
iperf3 -c 10.20.0.5 -t 30   # Сравниваем результат нового соединения: BBR против CUBIC
tc qdisc del dev eth0 root
```

## Когда BBR выигрывает, а когда остаться на CUBIC

```text
Используйте BBR для:
- WAN-каналов с RTT > 50 мс
- Спутниковых каналов (RTT 300–600 мс)
- Сетей с фоновыми потерями 0.5–2%
- Дальних массовых передач (из дата-центра в облако и т.п.)

Оставайтесь на CUBIC для:
- Чистого LAN (RTT <5 мс, потери почти нулевые)
- Легаси-систем, которые могут плохо уживаться с поведением BBR
- Сред, где критична справедливость между отдельными потоками
```

## Заключение

BBR — широко используемый вариант управления перегрузкой для Linux-систем, смотрящих в интернет. Его включение обычно означает установку `tcp_congestion_control=bbr`, и многие развёртывания также сочетают его с `default_qdisc=fq` для пейсинга. Наибольший выигрыш обычно проявляется на путях с высокой задержкой или случайными потерями, но точное улучшение зависит от рабочей нагрузки и сетевого пути.

**********

[linux](/tags/linux.md)
[tcp](/tags/tcp.md)
[networking](/tags/networking.md)