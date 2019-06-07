# Файл подкачки, ограничения памяти и cgroups

https://jvns.ca/blog/2017/02/17/mystery-swap/

На этой неделе на работе произошла ошибка, и я узнал что-то новое о памяти, обмене и группах!

Понимание того, как работает использование памяти, уже некоторое время является постоянным проектом - еще в декабре я написал [Сколько памяти использует мой процесс?](Https://jvns.ca/blog/2016/12/03/how-much-memory-is-my-process-using-/), который объясняет, как работает память в Linux.

Поэтому вчера я был удивлен и обеспокоен, когда с Linux что-то происходит с памятью, чего я не понимаю! Вот ситуация и почему я был сбит с толку:

У нас было несколько машин, на которых работали сборки. Они менялись местами. Они сказали 30 ГБ ОЗУ в общей сложности. 15 ГБ использовались некоторыми процессами, а 15 ГБ - кешем файловой системы. Я был действительно смущен тем, почему эти машины менялись местами, потому что - я знаю о памяти! Если кеш файловой системы использует 15 ГБ памяти, ОС всегда может освободить эту память! Там нет причин для обмена!

Затем я узнал о параметре «swappiness» и о том, что, если «swappiness» является высоким, то ОС, будет использовать swap, даже если в этом нет особой необходимости. Мы попытались установить `sysctl vm.swappiness = 1`, что позволит вам сказать операционной системе: «Нет, действительно, пожалуйста, не используй swap, просто вместо этого удали память из кэша файловой системы». Машина продолжала использовать swap. Я был сбит с толку.

Через некоторое время мы отключили «своп» и все стало еще хуже. Некоторые процессы стали убиваться OOM. (OOM killer в Linux убьет процессы, если у вас не хватит памяти) Но почему? У боксов была свободная память, не так ли? У меня в голове была аксиома «если у компьютера есть свободная память, нет причин, по которым процессы на нем должны быть убиты OOM». Очевидно, было что-то, чего я не понял.

Наконец, я посмотрел на вывод `dmesg` (именно так вы видите сообщения, которые печатает ядро Linux о том, что он задумал), чтобы понять, почему процессы были уничтожены OOM. А потом появилось это волшебное слово: `cgroups`. Все стало понятно довольно быстро:

*   процессы, которые были убиты, были в cgroup (о которой мы говорили в этом [пространства имен и группы](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/) посте)
*   cgroups может иметь **ограничения памяти**, которые похожи на «вам разрешено использовать только 15 ГБ памяти, иначе ваши процессы будут убиты OOM килером»
*   и этот предел памяти был причиной того, что процессы были убиты, даже если была свободная память!

### swap + cgroup ограничения памяти = сюрпризы

Моя модель пределов памяти для cgroups всегда была «если вы используете больше памяти, чем X, вы сразу же будете убиты». Оказывается, это предположение было неверным! Если вы используете больше памяти X, вы все равно можете использовать swap!

И, видимо, некоторые ядра также поддерживают установку отдельных пределов подкачки. Таким образом, вы можете установить предел памяти в X и предел обмена в 0, что даст вам более предсказуемое поведение. Обмен это странно и сбивает с толку.

Anyway, we found out through all this that the processes in question had recently started using much more memory for very understandable reasons, and rolled back that change, and everything made sense again.

And more importantly than everything making sense, the build system was happy again.

### does swap even make sense?

It’s not completely clear to me under what circumstances having swap on a computer at all even makes sense. It seems like swap has some role on desktop computers.

I am not sure though if any of the servers we operate benefit by having swap enabled? This seems like it would be a good thing to understand.

Like I hear the advice “no, just always turn off swap, it will be better overall” a lot and maybe that is the right thing! I think the reason that swap is considered bad in production systems is that it has weird/unpredictable effects and predictability is good.

Somewhat relately, this [swap insanity](https://blog.jcole.us/2010/09/28/mysql-swap-insanity-and-the-numa-architecture/)article looks really interesting.

### understanding memory models is cool

I learned

*   the vm.swappiness exists and you can use it to make a machine more or less likely to swap
*   that when Linux OOM kills a process in a cgroup (“container”), it actually prints a bunch of very useful stuff about the memory usage of everything else in the cgroup at the time. I should remember to look at dmesg earlier on!

It’s really important to me to understand what’s happening on the computers that I work with – when something happens like “this computer is swapping and I don’t know WHY” it bothers me a lot.

Now if I ever see a process mysteriously swapping hopefully I will remember about memory limits!

**********
[swap](/tags/swap.md)
[cgroups](/tags/cgroups.md)
[память](/tags/%D0%BF%D0%B0%D0%BC%D1%8F%D1%82%D1%8C.md)
