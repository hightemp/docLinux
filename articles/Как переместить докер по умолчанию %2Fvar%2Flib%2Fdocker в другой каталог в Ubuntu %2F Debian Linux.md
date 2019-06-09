# Как переместить докер из /var/lib/docker в другой каталог в Ubuntu / Debian Linux

The following config will guide you through a process of changing the docker's default /var/lib/docker storage disk space to another directory. There are various reasons why you may want to change docker's default directory from which the most obvious could be that ran out of disk space. The following guide should work for both Ubuntu and Debian Linux or any other systemd system. Make sure to follow this guide in the exact order of execution.  
  
Let's get started by modifying systemd's docker start up script. Open file `/lib/systemd/system/docker.service` with your favorite text editor and replace the following line where `/new/path/docker` is a location of your new chosen docker directory:

```
FROM:
ExecStart=/usr/bin/docker daemon -H fd://
TO:
ExecStart=/usr/bin/docker daemon -g /new/path/docker -H fd://
```

When ready stop docker service:

```console
$ systemctl stop docker
```

It is important here that you have completely stopped docker daemon. The following [linux command](https://linuxconfig.org/linux-commands)will yield no output only if docker service is stopped:

```console
$ ps aux | grep -i docker | grep -v grep
```

If no output has been produced by the above command, reload systemd daemon:

```console
$ systemctl daemon-reload
```

Once this is done create a new directory you specified above and optionally `rsync` current docker data to a new directory:

```console
$ mkdir /new/path/docker
$ rsync -aqxP /var/lib/docker/ /new/path/docker
```

At this stage we can safely start docker daemon:

```console
$ systemctl start docker
```

Confirm that docker runs within a new data directory:

```console
$  ps aux | grep -i docker | grep -v grep
root      2095  0.2  0.4 664472 36176 ?        Ssl  18:14   0:00 /usr/bin/docker daemon -g  /new/path/docker -H fd://
root      2100  0.0  0.1 360300 10444 ?        Ssl  18:14   0:00 docker-containerd -l /var/run/docker/libcontainerd/docker-containerd.sock --runtime docker-runc
```

All done.

**********
[Ubuntu](/tags/Ubuntu.md)
[docker](/tags/docker.md)
