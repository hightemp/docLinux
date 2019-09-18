# Как мне разрешить имя хоста в IP-адрес в скрипте Bash?

You can use `getent` , which comes with `glibc` (so you almost certainly have it on Linux). This resolves using gethostbyaddr/gethostbyname2, and so also will check `/etc/hosts` /NIS/etc:

```bash
getent hosts unix.stackexchange.com | awk '{ print $1 }'

```

Or, as Heinzi said below, you can use `dig` with the `+short` argument (queries DNS servers directly, does not look at `/etc/hosts` /NSS/etc) :

```bash
dig +short unix.stackexchange.com

```

If `dig +short` is unavailable, any one of the following should work. All of these query DNS directly and ignore other means of resolution:

```bash
host unix.stackexchange.com | awk '/has address/ { print $4 }'
nslookup unix.stackexchange.com | awk '/^Address: / { print $2 }'
dig unix.stackexchange.com | awk '/^;; ANSWER SECTION:$/ { getline ; print $5 }'

```

If you want to only print one IP, then add the `exit` command to `awk` 's workflow.

```bash
dig +short unix.stackexchange.com | awk '{ print ; exit }'
getent hosts unix.stackexchange.com | awk '{ print $1 ; exit }'
host unix.stackexchange.com | awk '/has address/ { print $4 ; exit }'
nslookup unix.stackexchange.com | awk '/^Address: / { print $2 ; exit }'
dig unix.stackexchange.com | awk '/^;; ANSWER SECTION:$/ { getline ; print $5 ; exit }'
```

**********
[bash](/tags/bash.md)
