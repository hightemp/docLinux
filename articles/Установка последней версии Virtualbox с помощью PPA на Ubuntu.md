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

##### Шаг 3. Загрузите и установите ключи для Virtualbox

```
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | sudo apt-key add -
```

##### Шаг 4: Обновите репозиторий

```
sudo apt-get update
```

##### Шаг 5: Установите Virtualbox 6.0 (или любую последнюю версию 6.0+)

```
sudo apt-get install virtualbox-6.0
```



**********
[Ubuntu](/tags/Ubuntu.md)
[virtualbox](/tags/virtualbox.md)
