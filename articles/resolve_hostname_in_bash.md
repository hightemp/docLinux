# Как мне разрешить имя хоста в IP-адрес в скрипте Bash?

Вы можете использовать `getent`, который поставляется с `glibc` (так что вы почти наверняка имеете его в Linux). Это решается с помощью gethostbyaddr / gethostbyname2, а также проверяет `/etc/hosts` /NIS/etc:

```bash
getent hosts unix.stackexchange.com | awk '{ print $1 }'
```

Или, как сказал Хайнци ниже, вы можете использовать `dig` с аргументом` + short` (напрямую запрашивает DNS-серверы, не просматривает `/etc/hosts` /NSS/etc):

```bash
dig +short unix.stackexchange.com
```

Если `dig + short` недоступен, должно работать любое из следующих действий. Все они обращаются к DNS напрямую и игнорируют другие средства разрешения:

```bash
host unix.stackexchange.com | awk '/has address/ { print $4 }'
nslookup unix.stackexchange.com | awk '/^Address: / { print $2 }'
dig unix.stackexchange.com | awk '/^;; ANSWER SECTION:$/ { getline ; print $5 }'
```

Если вы хотите напечатать только один IP, добавьте команду `exit` в рабочий процесс `awk`.

```bash
dig +short unix.stackexchange.com | awk '{ print ; exit }'
getent hosts unix.stackexchange.com | awk '{ print $1 ; exit }'
host unix.stackexchange.com | awk '/has address/ { print $4 ; exit }'
nslookup unix.stackexchange.com | awk '/^Address: / { print $2 ; exit }'
dig unix.stackexchange.com | awk '/^;; ANSWER SECTION:$/ { getline ; print $5 ; exit }'
```

**********
[bash](/tags/bash.md)
[getent](/tags/getent.md)
[dig](/tags/dig.md)
