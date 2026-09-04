# Как переключать алгоритмы контроля перегрузки TCP в Linux

Источник: [How to Switch TCP Congestion Control Algorithms on Linux](https://oneuptime.com/blog/post/2026-03-20-switch-tcp-congestion-control-linux/view)

Nawaz Dhandala · 20 марта 2026

## Введение

Linux позволяет менять алгоритм контроля перегрузки TCP (congestion control) как глобально для всей системы, так и для отдельного сокета. Системное значение по умолчанию применяется ко всем новым соединениям, если его не переопределили на уровне приложения. Переключение алгоритмов — особенно с CUBIC на BBR — может кардинально повысить пропускную способность на сетевых путях с высокой задержкой или потерями пакетов.

## Просмотр доступных алгоритмов

```bash
# List all available algorithms

sysctl -n net.ipv4.tcp_available_congestion_control
# reno cubic bbr ...

# If BBR is not listed, load the module
modprobe tcp_bbr
sysctl -n net.ipv4.tcp_available_congestion_control  # Check again

# View currently active algorithm
sysctl net.ipv4.tcp_congestion_control
```

## Загрузка дополнительных модулей контроля перегрузки

```bash
# Load algorithms provided as kernel modules
modprobe tcp_bbr       # BBR
modprobe tcp_htcp      # H-TCP (good for high-speed links)
modprobe tcp_westwood  # Better for wireless
modprobe tcp_hybla     # Better for satellite links

# Auto-load on boot on systemd-based systems
echo "tcp_bbr" > /etc/modules-load.d/tcp-bbr.conf

# Verify module loaded
lsmod | grep '^tcp_'
```

## Изменение алгоритма для всей системы

```bash
# Switch to BBR
sysctl -w net.ipv4.tcp_congestion_control=bbr

# Verify
sysctl net.ipv4.tcp_congestion_control
# net.ipv4.tcp_congestion_control = bbr

# Make permanent (survives reboot)
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p

# Or use sysctl.d for cleaner organization
echo "net.ipv4.tcp_congestion_control=bbr" > /etc/sysctl.d/10-tcp-bbr.conf
sysctl -p /etc/sysctl.d/10-tcp-bbr.conf
```

## Переопределение алгоритма для отдельного сокета

Приложения могут переопределять системное значение по умолчанию для своих конкретных сокетов с учётом ограничений Linux `tcp_allowed_congestion_control` и `CAP_NET_ADMIN`:

```python
# Python: set congestion control per socket (Linux-specific)
import socket

TCP_CONGESTION = getattr(socket, "TCP_CONGESTION", 13)  # Linux socket option

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set BBR for this specific socket
s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, b'bbr\x00')

# Verify
algo = s.getsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, 16).rstrip(b"\0")
print(f"Algorithm: {algo.decode()}")
```

```bash
# ss shows the congestion control algorithm per connection
ss -tin state established | grep -Eo 'cubic|bbr|reno'
```

## Переключение алгоритма и тестирование

```bash
#!/bin/bash
# Compare algorithms on your network
TARGET="10.20.0.5"

echo "=== Testing TCP Congestion Control Algorithms ==="
for algo in cubic bbr reno; do
    # Check if algorithm is available
    if sysctl -n net.ipv4.tcp_available_congestion_control | grep -qw -- "$algo"; then
        sysctl -w "net.ipv4.tcp_congestion_control=$algo" >/dev/null 2>&1
        RESULT=$(iperf3 -c "$TARGET" -t 10 -J 2>/dev/null | \
                 python3 -c "import sys,json; d=json.load(sys.stdin); \
                   print(f'{d[\"end\"][\"sum_sent\"][\"bits_per_second\"]/1e6:.1f} Mbps')")
        echo "$algo: $RESULT"
    fi
done
```

## Проверка алгоритма в активных соединениях

```bash
# Check algorithm for all established connections
ss -tin state established | grep -E '(^|[[:space:]])(cubic|bbr|reno)([[:space:]]|$)'

# Or for a specific connection
ss -tino "( dst 10.20.0.5 )"
# Look for the algorithm name, e.g. bbr or cubic, in the TCP info line.

# Per-connection statistics with current algorithm
ss -tin state established | head -30
```

## Заключение

Смена алгоритма контроля перегрузки в Linux — это однострочная команда sysctl. Сначала загрузите модуль нужного алгоритма (`modprobe tcp_bbr`), установите его как значение по умолчанию и сохраните настройку в `/etc/sysctl.conf`. Приложения также могут переопределять алгоритм для отдельных сокетов с помощью `TCP_CONGESTION`, если это разрешено политикой контроля перегрузки ядра. Прежде чем внедрять изменение в продакшене, проведите короткий сравнительный тест с iperf3 — правильный алгоритм зависит от характеристик именно вашей сети.

**********

[tcp](/tags/tcp.md)
[networking](/tags/networking.md)
[linux](/tags/linux.md)