# Как использовать logger в Linux

he[Linux](https://www.networkworld.com/article/3215226/linux/what-is-linux-uses-featres-products-operating-systems.html)**logger**command provides an easy way to add log files to**/var/log/syslog**— from the command line, from scripts, or from other files. In today's post, we'll take a look at how it works.

### How easy is easy?

This easy. Just type**logger <message>**on the command line and your message will be added to the end of the /var/log/syslog file.

$ logger comment to be added to log
$ tail -1 /vvar/log/syslog
May 21 18:02:16 butterfly shs: comment to be added to log

### Command output

You can also add the output from commands by enclosing the commands in backticks.

[

![](/images/77493432b8576587638f0950dbe5e558)





](https://www.networkworld.com/article/3274570/link)

$ logger \`who\`
$ tail -1 /var/log/syslog
May 21 18:02:43 butterfly shs: shs pts/0 2018-05-21 15:57 (192.168.0.15)

**\[ Two-Minute Linux Tips:[Learn how to master a host of Linux commands in these 2-minute video tutorials](https://www.networkworld.com/video/series/8559/2-minute-linux-tips)\]**

### Content from a file

The contents of text files can be added by using the**\-f**option. Put the name of the file to be added to the log following the**\-f**option as shown below.

$ cat msg
Backups to off-site facility will run this coming weekend.
System availability will not be affected.
$ logger -f msg
$ tail -2 /var/log/syslog
May 21 18:06:01 butterfly shs: Backups to off-site facility will run this coming weekend.
May 21 18:06:01 butterfly shs: System availability will not be affected.

### Using logger in scripts

You can add logger commands to scripts to make it easier to track the completion of important tasks.

$ grep logger /bin/runme
logger "$0 completed at \`date\`"
$ sudo runme
$ tail -1 /var/log/syslog
May 21 17:57:36 butterfly shs: ./runme completed at Mon May 21 17:57:36 EDT 2018

### Limiting the size of logger entries

If you're concerned about how much data will be added to your log file, especially if you're dumping content from a file, you can use the**\--size**option to limit it. In this example, the size is artificially small to make a point.

$ logger --size 10 12345678901234567890123456789012345678901234567890
$ tail -1 /var/log/syslog
May 21 18:18:02 butterfly shs: 1234567890

This option works differently than you might expect in that, given input that includes blanks, it will constrain the content on a per-line basis rather than an overall length basis.

$ logger --size 5 \`date\`
$ tail -5 /var/log/syslog
May 22 08:35:51 butterfly shs: May
May 22 08:35:51 butterfly shs: 22
May 22 08:35:51 butterfly shs: 08:35
May 22 08:35:51 butterfly shs: EDT
May 22 08:35:51 butterfly shs: 2018

Don't be misled by these simple examples. The**\--size**option is generally used to limit large amounts of text. The default maximum is 1KiB (1024 bytes).

[![](/images/35b96a4d7339f07cbba8891e4460a256)](https://eb2.3lift.com/pass?tl_clickthrough=true&redir=https%3A%2F%2Fams1-ib.adnxs.com%2Fclick%3FKeIDJmatCkDMyvavMa0IQAAAAAApXBZAZg5JLZT0DEB1w7ZFmU0PQLUoaJtFgIpwsMILS5Q_63257O5cAAAAAN5yvwAiBQAAzQQAAAIAAAAobJEJX_kVAAAAAABVU0QAVVNEAAEAAQB1dQAAAAABAgUCAAAAAIIAeSEJqgAAAAA.%2Fcpcpm%3DAAAAAAAAAAA%3D%2Fbcr%3DAAAAAAAA8D8%3D%2Fpp%3D%24%7BAUCTION_PRICE%7D%2Fcnd%3D%2521yRFW8gjU06oOEKjYxUwY3_JXIAAoADEAAAAAAADwPzoJQU1TMTozOTk0QNwMSXOiXYWUn-w_UQAAAAAAAAAAWQAAAAAAAAAA%2Fcca%3DMTIyOSNBTVMxOjM5OTQ%3D%2Fbn%3D84005%2Fclickenc%3Dhttps%253A%252F%252Fad.doubleclick.net%252Fddm%252Ftrackclk%252FN470006.3561905STARSGROUP_PS_RU_%252FB22720013.247184445%253Bdc_trk_aid%253D443336397%253Bdc_trk_cid%253D116267830%253Bdc_lat%253D%253Bdc_rdid%253D%253Btag_for_child_directed_treatment%253D%253Btfua%253D "Стань звездой")

Sponsored PostSponsored by Pokerstars

[Стань звездой](https://eb2.3lift.com/pass?tl_clickthrough=true&redir=https%3A%2F%2Fams1-ib.adnxs.com%2Fclick%3FKeIDJmatCkDMyvavMa0IQAAAAAApXBZAZg5JLZT0DEB1w7ZFmU0PQLUoaJtFgIpwsMILS5Q_63257O5cAAAAAN5yvwAiBQAAzQQAAAIAAAAobJEJX_kVAAAAAABVU0QAVVNEAAEAAQB1dQAAAAABAgUCAAAAAIIAeSEJqgAAAAA.%2Fcpcpm%3DAAAAAAAAAAA%3D%2Fbcr%3DAAAAAAAA8D8%3D%2Fpp%3D%24%7BAUCTION_PRICE%7D%2Fcnd%3D%2521yRFW8gjU06oOEKjYxUwY3_JXIAAoADEAAAAAAADwPzoJQU1TMTozOTk0QNwMSXOiXYWUn-w_UQAAAAAAAAAAWQAAAAAAAAAA%2Fcca%3DMTIyOSNBTVMxOjM5OTQ%3D%2Fbn%3D84005%2Fclickenc%3Dhttps%253A%252F%252Fad.doubleclick.net%252Fddm%252Ftrackclk%252FN470006.3561905STARSGROUP_PS_RU_%252FB22720013.247184445%253Bdc_trk_aid%253D443336397%253Bdc_trk_cid%253D116267830%253Bdc_lat%253D%253Bdc_rdid%253D%253Btag_for_child_directed_treatment%253D%253Btfua%253D "Стань звездой")

Выиграй поездку на Европейский Покерный Тур в Сочи бесплатно на pokerstarssochi.net. Выиграй поездку на EPT Open в Сочи бесплатно на pokerstarssochi.net

![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiI+PHBhdGggZD0iTTIuMDguMDQyQy40NDcuNDM3LS4wODMgMi4zMDYuMDU0IDMuNzg4LS4wNTYgOS45OC4wNDIgMTYuMTc0IDAgMjIuMzY3Yy4wNTEgMi40OTgtLjA4MyA1LjAxLjE2NiA3LjQ5Ny4xNTggMS44MjIgMi4wMzQgMi40NTEgMy41NzcgMS45OTEgMS41OTYtLjQyNyAyLjk2OS0xLjM5NSA0LjQzOS0yLjExNCAxLjg1LS43NTkgMS42NzUtNC4xLS42NTktMy43OTUtMS4zMTguNjk0LTMuMzIuNTEtMy4xNDktMS40NTQtLjAxLTYuMDA2LS4wOTQtMTIuMDI0LjA0My0xOC4wMjYuMzMtMS45MTggMi41NC0xLjMzNiAzLjYyMS0uNDU2IDEuOTI3IDEuMDIzIDMuODE0IDIuMDkgNS43NSAzLjA5OGE2NzEuNTUgNjcxLjU1IDAgMCAwIDUuODc3IDMuMTk2YzEuNTcuODg1IDMuMjMzIDEuNjQyIDQuNzA4IDIuNjc2IDEuMzQyIDEuNDkzLS45MDMgMi41NDgtMi4wNSAzLjAxLTEuOTY0LjkxNy0zLjgzOSAxLjk4Ny01Ljg0MiAyLjgxOC0uNzU0LjM1Ny0yLjM4NSAxLjYzOC0yLjczNS45ODYtLjEyNy0xLjg3LjA4Ny0zLjc4LS4xMDYtNS42MjYtLjM0LTEuNzc5LTMuMzQ3LTEuODY4LTMuNzMtLjA3OS0uMDQzIDMuMTgxLS4wMTYgNi4zNjgtLjAzMiA5LjU1Ljg4IDEuNjkgMy4yMjQgMS45MTkgNC42NDQuNzc0IDEuNjItLjgxMiAzLjIwNi0xLjYzMyA0LjgyNi0yLjQ1NSAxLjgwMy0uOTQzIDMuNjQtMS44NjkgNS40NTgtMi44MDcgMi4wNi0xLjE1NSA0LjI4Mi0yLjAxOCA2LjIxNy0zLjM4MyAxLjk4MS0xLjM1NC42MzYtNC4wNTUtMS4yNi00LjY4My0xLjkwNS0xLjA2My0zLjg5LTEuOTg5LTUuODE2LTMuMDM2YTkyMS42OCA5MjEuNjggMCAwIDEtNi45OTMtMy42MTdjLTEuMjI3LS42MS0yLjQzNi0xLjI3Mi0zLjY3Mi0xLjg5NUMxMC42MzggMy4xOSA4LjAyIDEuNzg3IDUuMzgzLjQ1IDQuMzg1LS4xNjcgMy4xOTEuMDI0IDIuMDguMDQyem05LjA3OCAxMC4yN2MtMS41NDkuMzU1LTEuNzc1IDIuNzc0LS4zNDYgMy40NSAxLjQxLjgzOCAzLjQ4Ni0uNTIxIDIuOTY3LTIuMTg1LS4yMzUtMS4xNjUtMS42MDEtMS41NDctMi42MjEtMS4yNjV6IiBmaWxsPSIjMTlhYmNjIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiLz48L3N2Zz4=)

### Ignoring blank lines

The**\-e**option allows you to avoid dumping empty lines into your log file. They will simply be ignored. Note, however, that a line that contains blanks will_not_be considered blank.

$ cat appts
Appts
                                              <=== file includes blank line
8 AM -- get to office
8:30 AM -- meet with boss
11:00 AM -- staff meeting
$ logger -e -f appts
May 22 08:17:31 butterfly shs: Appts          <=== log does not
May 22 08:17:31 butterfly shs: 8 AM -- get to office
May 22 08:17:31 butterfly shs: 8:30 AM -- meet with boss
May 22 08:17:31 butterfly shs: 11:00 AM -- staff meeting
May 22 08:17:33 butterfly kernel: \[58833.758599\] \[UFW BLOCK\] IN=enp0s25 OUT= MAC=01:00:5e:00:00:fb:ac:63:be:ca:10:cf:08:00 SRC=192.168.0.9 DST=224.0.0.251 LEN=32 TOS=0x00 PREC=0xC0 TTL=1 ID=0 DF PROTO=2

### Other options

The logger tool offers others as well — such as writing to a log on another server using**\-n**or**\--no-act**for testing. Check your man page for more details.

Join the Network World communities on[Facebook](https://www.facebook.com/NetworkWorld/)and[LinkedIn](https://www.linkedin.com/company/network-world)to comment on topics that are top of mind.



**********
[логи](/tags/%D0%BB%D0%BE%D0%B3%D0%B8.md)
[logger](/tags/logger.md)
