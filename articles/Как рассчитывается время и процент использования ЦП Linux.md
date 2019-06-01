# Как рассчитывается время и процент использования ЦП Linux

### обзор

Время процессора распределяется в дискретных временных срезах (тиках). В течение определенного количества временных интервалов процессор занят, в других случаях это не так (что представлено процессом простоя). На рисунке ниже процессор занят для 6 из 10 срезов процессора. 6/10 = .60 = 60% занятого времени (и поэтому было бы 40% простоя).

![](/images/3b036987b148a55b2e46e60aa3364470)

Примечание. Тик (цикл) - это время, необходимое для отправки одного импульса. Импульс состоит из высокого напряжения, за которым следует низкое напряжение. Может быть миллиарды тиков в секунду в зависимости от частоты (ГГц) тактовой частоты процессора.

Вы можете получить количество тактов процессора с момента загрузки из /proc/stat

```
 cat /proc/stat
     user nice system idle iowait  irq  softirq steal guest guest_nice
cpu  4705 356  584    3699   23    23     0       0     0          0

```

*   **user:** нормальные процессы, выполняющиеся в пользовательском режиме
*   **nice:** niced процессы, выполняющиеся в пользовательском режиме
*   **system:** процессы, выполняющиеся в режиме ядра
*   **idle:** большие пальцы
*   **iowait:** ожидание завершения ввода/вывода
*   **irq:** обслуживание прерываний
*   **softirq:** обслуживание Softirqs
*   **steal:** непроизвольное ожидание
*   **guest:** работающий под нормальным гость
*   **guest\_nice:** работающий под приятным(niced) гостем

###  Формула

Чтобы рассчитать время загрузки процессора Linux, вычтите время простоя процессора из общего времени процессора следующим образом:

**Общее время процессора с момента загрузки**\= user+nice+system+idle+iowait+irq+softirq+steal

**Общее время простоя процессора с момента загрузки**\= idle + iowait

**Общее время использования процессора с момента загрузки**\= Общее время процессора с момента загрузки - Общее время простоя процессора с момента загрузки

**Общий процент процессора**\= Общее время использования процессора с момента загрузки/Общее время процессора с момента загрузки X 100

Если вы используете формулу в приведенных выше примерах данных, вы должны получить процент использования ЦП Linux в размере 60%.

**Примечание:** Guest и Guest_nice уже учтены в user и nice, следовательно, они не включены в общий расчет

Для использования процессора в режиме реального времени вам необходимо рассчитать время между двумя интервалами.

Ниже приведен пример сценария Bash Пола Колби, который делает это

```
    #!/bin/bash
    # by Paul Colby (http://colby.id.au), no rights reserved ;)

    PREV_TOTAL=0
    PREV_IDLE=0

    while true; do
      # Get the total CPU statistics, discarding the 'cpu ' prefix.
      CPU=(`sed -n 's/^cpu\s//p' /proc/stat`)
      IDLE=${CPU[3]} # Just the idle CPU time.

      # Calculate the total CPU time.
      TOTAL=0
      for VALUE in "${CPU[@]}"; do
        let "TOTAL=$TOTAL+$VALUE"
      done

      # Calculate the CPU usage since we last checked.
      let "DIFF_IDLE=$IDLE-$PREV_IDLE"
      let "DIFF_TOTAL=$TOTAL-$PREV_TOTAL"
      let "DIFF_USAGE=(1000*($DIFF_TOTAL-$DIFF_IDLE)/$DIFF_TOTAL+5)/10"
      echo -en "\rCPU: $DIFF_USAGE%  \b\b"

      # Remember the total and idle CPU times for the next check.
      PREV_TOTAL="$TOTAL"
      PREV_IDLE="$IDLE"

      # Wait before checking again.
      sleep 1
    done

```

[https://www.kernel.org/doc/Documentation/filesystems/proc.txt](https://www.kernel.org/doc/Documentation/filesystems/proc.txt) section 1.8

[https://github.com/pcolby/scripts/blob/master/cpu.sh](https://github.com/pcolby/scripts/blob/master/cpu.sh)

[http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux](http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux)

[http://serverfault.com/questions/648704/how-are-cpu-time-and-cpu-usage-the-same](http://serverfault.com/questions/648704/how-are-cpu-time-and-cpu-usage-the-same)

[http://www.webopedia.com/TERM/C/clock\_tick.html](http://www.webopedia.com/TERM/C/clock_tick.html)

[http://www.pcworld.com/article/221559/cpu.html](http://www.pcworld.com/article/221559/cpu.html)

[http://stackoverflow.com/questions/16726779/how-do-i-get-the-total-cpu-usage-of-an-application-from-proc-pid-stat](http://stackoverflow.com/questions/16726779/how-do-i-get-the-total-cpu-usage-of-an-application-from-proc-pid-stat)

[http://www.ask.com/technology/many-times-system-clock-tick-per-second-1-ghz-processor-b9028ab0b0de7883](http://www.ask.com/technology/many-times-system-clock-tick-per-second-1-ghz-processor-b9028ab0b0de7883)

[https://github.com/torvalds/linux/blob/master/fs/proc/stat.c](https://github.com/torvalds/linux/blob/master/fs/proc/stat.c)