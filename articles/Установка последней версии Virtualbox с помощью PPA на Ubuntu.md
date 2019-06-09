# Установка последней версии Virtualbox с помощью PPA на Ubuntu

##### Шаг 1.

Перед установкой новой версии нам нужно удалить старую версию с помощью программного центра или использовать следующую команду:

```
sudo apt-get remove virtualbox virtualbox-4.* virtualbox-5.*
```

##### Шаг 2. Добавьте список пакетов в sources.list

```
sh -c "echo 'deb http://download.virtualbox.org/virtualbox/debian '$(lsb_release -cs)' contrib non-free' > /etc/apt/sources.list.d/virtualbox.list"
```



**********
[virtualbox](/tags/virtualbox.md)
