#  Ubuntu Make — разработчику в помощь

 Появилось желание познакомиться с разработкой под android. Скачал Android Studio, распаковал и удалил. Решил поискать другие варианты установки. В процессе поиска наткнулся на Ubuntu Make (он же Ubuntu Developer Tools Center в прошлом), и в этой небольшой заметке хочу рассказать вам о нем.   
  
 Ubuntu Developer Tools Center промелькнул в новостях вместе с Ubuntu 14.10 (Utopic Unicorn), но широкого внимания масс, как мне кажется, к себе не привлек. Не многим позже проект переименовали в Ubuntu Make, как он и называется по сей день подросшим до версии 0.4. Разработкой занимается Didier Roche, Software Engineer, Canonical. Также достоин внимания тот факт, что Ubuntu Make написан на Python 3.4.   
  
 Основная цель проекта быстрая и легкая установка общих потребностей разработчика в Ubuntu. И хотя до «общих потребностей» еще далековато (список доступных для установки пакетов пока маловат), с «быстро и просто» все отлично.   
  
 На данный момент с помощью Ubuntu Make можно установить:   

*   Android Studio
*   Eclipse
*   IntelliJ Idea Community Edition
*   PyCharm Community Edition
*   go-lang Google compiler
*   Stencyl game developer IDE

  

#### Установка

  
 В ubuntu 15.04 ubuntu-make доступен из коробки, пользователям версий 14.04 и 14.10 предлагается установить из ppa:   
  

```
sudo add-apt-repository ppa:ubuntu-desktop/ubuntu-make
sudo apt-get update
sudo apt-get install ubuntu-make

```

  

#### Использование

  
 Установка с ubuntu-make проста до неприличия. Для установки Android Studio достаточно выполнить в терминале:   
  

```
umake android

```

  
 Немного ожидания и вот результат:   
 ![](/images/9f2ec35677f0b19b42e01195a2baee31.png)   
  
 Иконка в dash и openjdk (если явы не было в системе) в комплекте. После запуска «студия» подтянула sdk и обновилась до версии 1.0.2. «Hello world» был запущен на телефоне и на этом проверка работоспособности завершилась.   
  
 golang устанавливается аналогично:    
 ![](/images/d083438e6a51fe4da3ba6fb5b58e47a7.png)   
  
 Для PyCharm, Eclipse, Idea добавится еще один аргумент:   
  

```
umake ide pycharm

```

  
 ![](/images/ca88b8dc50d07fb12f97751686cc94ef.png)   
  
 Для удаления пакета достаточно добавить аргумент "-r" к той же строчке:   
  

```
umake ide pycharm -r

```

#### Мнение

  
 Кто-то скажет: — «Много ли делов. Скачать архив, распаковать, иконку в dash да яву проверить. Нужен ли ubuntu make?». Согласен может дел и не много, но я нашел пакет полезным для себя. Он сэкономил мне время и избавил от рутины. Надеюсь будет полезным и вам.   
  
 Ссылки:   
 Ubuntu Make на   [Github](https://github.com/ubuntu/ubuntu-make)  .   
 [Блог](http://blog.didrocks.fr/)   Didier Roche.

**********
[Ubuntu](/tags/Ubuntu.md)
