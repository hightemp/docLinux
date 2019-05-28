# Как использовать команду «Script» для записи терминальной сессии Linux

Эта команда сценария очень полезна для системного администратора. Если в системе возникает какая-либо проблема, очень трудно найти, какая команда была выполнена ранее. Следовательно, системный администратор знает важность этой команды сценария. Иногда вы находитесь на сервере и думаете, что ваша команда или кто-то из ваших знакомых на самом деле не хватает документации о том, как выполнить конкретную конфигурацию. Вы можете выполнить настройку, записать все действия сеанса оболочки и показать запись человеку, который точно увидит, что у вас было (тот же вывод) в вашей оболочке в момент настройки.

### Как работает команда сценария?

Команда script записывает для вас сеанс оболочки, так что вы можете посмотреть на вывод, который вы видели в то время, и вы можете даже записать с синхронизацией, чтобы вы могли воспроизводить в реальном времени. Это действительно полезно и пригодится в самые странные времена и места.

Команда script ведет журнал действий для различных задач. Сценарий записывает все в сеансе, например, что вы печатаете, что видите. Для этого просто введите команду _script_ на терминале и введите _exit_ когда закончите. Все, что находится между командой _script_ и _exit_, заносится в файл. Это включает в себя сообщения с подтверждением от самого скрипта.

## 1\. Record your terminal session

script makes a typescript of everything printed on your terminal. If the argument file is given, script saves all dialogue in the indicated file in the current directory. If no file name is given, the typescript is saved in default file typescript. To record your shell session so what you are doing in the current shell, just use the command below

```console
# script shell\record1
Script started, file is shell\record1
```

Это указывает на то, что файл _shell\_record1_ создан. Давайте проверим файл

```console
# ls -l shell_*
-rw-r--r-- 1 root root 0 Jun 9 17:50 shell_record1
```

После завершения вашей задачи вы можете ввести _exit_ или `Ctrl-d`, чтобы закрыть сеанс скрипта и сохранить файл.

```console
# exit
exit
Script done, file is shell_record1
```

Вы можете видеть, что скрипт указывает имя файла.

## 2\. Check the content of a recorded terminal session

When you use script command, it records everything in a session such as things you type so all your output. As the output is saved into a file, it is possible after to check its content after existing a recorded session. You can simply use a text editor command or a text file command viewer.

\# cat shell\_record1 
Script started on Fri 09 Jun 2017 06:23:41 PM UTC
\[root@centos-01 ~\]# date
Fri Jun 9 18:23:46 UTC 2017
\[root@centos-01 ~\]# uname -a
Linux centos-01 3.10.0-514.16.1.el7.x86\_64 #1 SMP Wed Apr 12 15:04:24 UTC 2017 x86\_64 x86\_64 x86\_64 GNU/Linux
\[root@centos-01 ~\]# whoami
root
\[root@centos-01 ~\]# pwd
/root
\[root@centos-01 ~\]# exit
exit

Script done on Fri 09 Jun 2017 06:25:11 PM UTC

While you view the file you realize that the script also stores line feeds and backspaces. It also indicates the time of the recording to the top and the end of the file.

## 3\. Record several terminal session

You can record several terminal session as you want. When you finish a record, just begin another new session record. It can be helpful if you want to record several configurations that you are doing to show it to your team or students for example. You just need to name each recording file.

For example, let us assume that you have to do[OpenLDAP](https://linoxide.com/linux-how-to/install-openldap-2-different-hosts-configure-mirror-mode/),[DNS](https://linoxide.com/containers/setting-dns-server-docker/),[Machma](https://linoxide.com/tools/machma-enables-run-multiple-commands-parallel-linux/) configurations. You will need to record each configuration. To do this, just create recording file corresponding to each configuration when finished.

\# script openldap\_record
   ...............
    configuration step
   ..............
# exit

When you have finished with the first configuration, begin to record the next configuration

\# script machma\_record
    ............
     configuration steps
    .............
# exit

And so on for the other. Note that if you script command followed by existing filename, the file will be replaced. So you will lost everything.

Now, let us imagine that you have begun Machma configuration but you have to abort its configuration in order to finish DNS configuration because of some emergency case. Now you want to continue the machma configuration where you left. It means you want to record the next steps into the existing file_machma\_record _without deleting its previous content; to do this you will use`script -a`command to append the new output to the file.

This is the content of our recorded file

![](/images/script-record1.png)

Now if we want to continue our recording in this file without deleting the content already present, we will do

\# script -a machma\_record
Script started, file is machma\_record

Now continue the configuration, then exit when finished and let's check the content of the recorded file.

![](/images/script-append.png)

Note the new time of the new record which appears. You can see that the file has the previous and actual records.

## 4\. Replay a linux terminal session

We have seen that it is possible to see the content of the recorded file with commands to display a text file content. The script command also gives the possibility to see the recorded session as a _video. _It means that you will review exactly what you have done step by step at the moment you were entering the commands as if you were looking a video. So you will playback/replay the recorded terminal session.

To do it, you have to use `--timing`option of script command when you will start the record.

\# script --timing=file\_time shell\_record1
Script started, file is shell\_record1

See that the file into which to record is _shell\_record1. _When the record is finished, exit normally

\# exit
exit
Script done, file is shell\_record1

Let's see check the content of _file\_time _

\# cat file\_time 
0.807440 49
0.030061 1
116.131648 1
0.226914 1
0.033997 1
0.116936 1
0.104201 1
0.392766 1
0.301079 1
0.112105 2
0.363375 152

The`--timing` option outputs timing data to the file indicated. This data contains two fields, separated by a space which indicates how much time elapsed since the previous output how many characters were output this time. This information can be used to replay typescripts with realistic typing and output delays.

Now to replay the terminal session, we use scriptreplay command instead of script command with the same syntax when recording the session. Look below

\# scriptreplay --timing=file\_time shell\_record1

You will that the recorded session with be played as if you were looking a video which was recording all that you were doing. You can just insert the timing file without indicating all the --timing=file\_time. Look below

\# scriptreplay file\_time shell\_record1

So you understand that the first parameter is the timing file and the second is the recorded file.

## Conclusion

The script command can be your to-go tool for documenting your work and showing others what you did in a session. It can be used as a way to log what you are doing in a shell session. When you run script, a new shell is forked. It reads standard input and output for your terminal tty and stores the data in a file.