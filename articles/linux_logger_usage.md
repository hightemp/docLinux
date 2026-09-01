# Как использовать logger в Linux

The [Linux](https://www.networkworld.com/article/3215226/linux/what-is-linux-uses-featres-products-operating-systems.html) **logger** command provides an easy way to add log files to **/var/log/syslog** — from the command line, from scripts, or from other files. In today's post, we'll take a look at how it works.

### How easy is easy?

This easy. Just type **logger <message>** on the command line and your message will be added to the end of the /var/log/syslog file.

	$ logger comment to be added to log
	$ tail -1 /var/log/syslog
	May 21 18:02:16 butterfly shs: comment to be added to log

### Command output

You can also add the output from commands by enclosing the commands in backticks.

	$ logger `who`
	$ tail -1 /var/log/syslog
	May 21 18:02:43 butterfly shs: shs pts/0 2018-05-21 15:57 (192.168.0.15)

### Content from a file

The contents of text files can be added by using the **\-f** option. Put the name of the file to be added to the log following the **\-f** option as shown below.

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
	logger "$0 completed at `date`"
	$ sudo runme
	$ tail -1 /var/log/syslog
	May 21 17:57:36 butterfly shs: ./runme completed at Mon May 21 17:57:36 EDT 2018

### Limiting the size of logger entries

If you're concerned about how much data will be added to your log file, especially if you're dumping content from a file, you can use the **\--size** option to limit it. In this example, the size is artificially small to make a point.

	$ logger --size 10 12345678901234567890123456789012345678901234567890
	$ tail -1 /var/log/syslog
	May 21 18:18:02 butterfly shs: 1234567890

This option works differently than you might expect in that, given input that includes blanks, it will constrain the content on a per-line basis rather than an overall length basis.

	$ logger --size 5 `date`
	$ tail -5 /var/log/syslog
	May 22 08:35:51 butterfly shs: May
	May 22 08:35:51 butterfly shs: 22
	May 22 08:35:51 butterfly shs: 08:35
	May 22 08:35:51 butterfly shs: EDT
	May 22 08:35:51 butterfly shs: 2018

Don't be misled by these simple examples. The **\--size** option is generally used to limit large amounts of text. The default maximum is 1KiB (1024 bytes).

### Ignoring blank lines

The **\-e** option allows you to avoid dumping empty lines into your log file. They will simply be ignored. Note, however, that a line that contains blanks will_not_be considered blank.

```console
$ cat appts
Appts <=== file includes blank line
8 AM -- get to office
8:30 AM -- meet with boss
11:00 AM -- staff meeting
$ logger -e -f appts
May 22 08:17:31 butterfly shs: Appts <=== log does not
May 22 08:17:31 butterfly shs: 8 AM -- get to office
May 22 08:17:31 butterfly shs: 8:30 AM -- meet with boss
May 22 08:17:31 butterfly shs: 11:00 AM -- staff meeting
May 22 08:17:33 butterfly kernel: \[58833.758599\] \[UFW BLOCK\] IN=enp0s25 OUT= MAC=01:00:5e:00:00:fb:ac:63:be:ca:10:cf:08:00 SRC=192.168.0.9 DST=224.0.0.251 LEN=32 TOS=0x00 PREC=0xC0 TTL=1 ID=0 DF PROTO=2
```console
	
### Other options

The logger tool offers others as well — such as writing to a log on another server using **\-n** or **\--no-act** for testing. Check your man page for more details.





**********
[логи](/tags/%D0%BB%D0%BE%D0%B3%D0%B8.md)
[logger](/tags/logger.md)
[НЕ ПЕРЕВЕДЕНО](/tags/%D0%9D%D0%95%20%D0%9F%D0%95%D0%A0%D0%95%D0%92%D0%95%D0%94%D0%95%D0%9D%D0%9E.md)
