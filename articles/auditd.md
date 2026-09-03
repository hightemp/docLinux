# auditd

Источник: [auditd](https://sematext.com/glossary/auditd/)

```text
sudo dnf install audit
```

`auditd` is not always operating on an openSUSE Leap system by default. However, the following command will enable it:

```text
sudo systemctl enable auditd
```

Similarly, in Debian-based Linux distributions, you can install the latest version of `auditd `along with its relevant plugins using:

```text
sudo apt-get install auditd audispd-plugins
```

After the installation is successfully complete, you can perform a list of operations. Once you’ve finished installing, you will want to start auditd with the service auditd start command. If auditd is already running but you want to restart it, use service auditd condrestart.

To check the status of the auditd service, run service auditd status. But to reload auditd service use service auditd reload.

Similarly, to stop auditd service, run service auditd stop; to restart it, run service auditd restart

Use the service auditd rotate comand, if you want to [rotate the log files](https://sematext.com/glossary/log-rotation/) in the`/var/log/audit/` directory.

## Set Up Rules

In RHE, you must use the auditctl utility to set up auditd rules. This utility gets the audit status and adds or deletes the rules into the system.

The rules for `auditd` are added to /etc/audit/rules.d/audit.rules file by default.When your system starts up, these rules are read by auditctl utility. It is recommended that you use the same path to maintain the rules for auditd to ensure uninterrupted access to the rules across the reboots.

Here is a list of some common options available to the `auditctl`utility.

  * **-w** : adds a watch to the file. auditd will record the user activities of that particular file.
  * **-k** : on a specific auditd rule, sets an optional string or key, which can be used for identifying the rule (or a set of rules) that created a specific log entry,
  * **-F** : builds a rule field using a name, arithmetic and/or logical operator, and a value.
  * **-l** : lists all currently loaded `auditd` rules in multiple lines, each line representing a rule.
  * **-t** : trims the subtrees that appear after a mount command.
  * **-S** : assigns system call name or number.
  * **-a** : appends rule to the end of a comma-separated catalog of list and action pairs

```text
* Valid list names – task, exit, user, exclude
* Valid action names – never, always
```

The pairs can be in either of the following order:

```text
* list, action
* action, list
```

In OpenSuse, in addition to building a set of rules in /etc/audit/audit.rules, which is processed each time the audit daemon starts, audit rules can also be provided to the audit daemon via the `auditctl`program. Edit `/etc/audit/audit.rules` directly if you want to modify it.

Rules provided on the program must be entered once more when the audit daemon is restarted because they do not persist.

The following would be a straightforward rule configuration for basic audits on a few significant files and directories:

```text
# basic audit system parameters
-D
-b 8192
-f 1
-e 1

# some file and directory watches with keys
-w /var/log/audit/ -k LOG_audit
-w /etc/audit/auditd.conf -k CFG_audit_conf -p rxwa
-w /etc/audit/audit.rules -k CFG_audit_rules -p rxwa

-w /etc/passwd -k CFG_passwd -p rwxa
-w /etc/sysconfig/ -k CFG_sysconfig
# an example system call rule
-a entry,always -S umask
```

Try these parameters with your audit rule set while configuring the fundamental audit system parameters to see if the backlog size is suitable for the volume of logging activity your audit rule set generates. Your system may not be capable of handling the audit load and may raise the failure flag (`-f)` whenever the backlog threshold is reached (if the backlog size you’ve specified is too tiny).

## How to Work with Linux auditd Data: Common Utilities

To understand how `auditd` works, you first need to understand how a Linux daemon works.

A daemon is a background process that is not dependent on the interaction of an active user, i.e., a general user can’t control the periodic execution of a daemon. It is launched when Linux boots, and an init process acts as its parent process. To start and stop the daemon, /etc/init.d scripts on the OS should be accessed initially.

In Linux, a daemon process has the suffix `d`. Using this suffix, you can differentiate whether a process is a daemon or a system, or a user process. By that definition, `auditd` is also a daemon process. Let’s look closer into the components and utilities of `auditd` utility.

### auditd File Location

`auditd.conf` is located in the /etc/audit/directory and is the configuration file for auditd. It contains the specific configuration information of the audit daemon and includes multiple lines of configuration, where each line has a keyword, an equal sign, and the appropriate configuration value. Some of the keywords available in the file are:

  * log_file
  * log_format
  * flush
  * freq
  * num_logs
  * max_ log_file
  * max_log_ file_action

You can check the configuration file by running:

```bash
$ sudo less /etc/audit/auditd.conf
```

A `auditd.conf` file could look something like this:

```text
log_file = /var/log/audit/audit.log
log_format = RAW
flush = INCREMENTAL
freq = 20
num_logs = 5
max_log_file = 8
max_log_file_action = ROTATE
```

### Search auditd Events

As mentioned above, `auditd` doesn’t let you view the logs. To view the logs, you must use the ausearch utility. It is used to query audit daemon logs for events based on different search criteria.

Here are some of the most common options used to query the logs

  * **-p** : Search for events with the given process ID.
  * **-m** : Search for events with the given message type.
  * **-sv** : Search for events with a given success value.
  * **-ua** : Search for an event using user ID, effective user ID, or login user ID or auid.
  * **-ts** : Search for events with time stamps equal to or after the given end time.

### Create auditd Reports

`aureport` is a tool that produces summary reports of the audit system logs. The reports contain a column label at the top to help interpret various fields. All reports have an audit event number except the main summary report. Some of the aureport keywords are:

  * **-k** : Report about audit rule keys.
  * **-i** : Interpret numeric entities into text e.g., uid is converted to the account name.
  * **-au** : Report about authentication attempts.
  * **-l** : Report about logins.

### Other Useful Utilities

On top of the utilities described above, there are additional utilities that can be advantageous to you.

For instance, if you need to define Audit rules that are permanent across reboots, there are two ways. You must either explicitly include Audit rules in the /etc/audit/rules.d/audit.rules file or run the`augenrules` program, which reads rules from the /etc/audit/rules.d/ directory.

But, say you want to add the audit rules to trace a process and save the audit information in audit logs when the audit daemon is running, autrace will do that for you.`autrace` runs a program until it exists. As a safety precaution, however, this command will not run unless all the rules are deleted with`auditcl` as `autrace `deletes all audit rules before executing the target program and after executing it.

If you want to analyze the logs events captured by `auditd`, use `autdisp. `It takes audit events and distributes them to child programs to analyze them in real-time. It is an audit event multiplexor that has to be started by the audit daemon.

Finally, to return information needed for analysis, aulast can be used to print a list of the last logged-in users. Itsearches through the audit logs and displays a list of all users logged in (and out). Meanwhile, there is also `aulastlog` thatreturns the latest login details of all machine users by printing the login name, port, and last login time. The port and time fields will show “Never logged in” if a user has never logged in.

## Sematext and auditd

Serious usage of auditd – even on just a few hosts – can generate lots of events. With standard tools like `ausearch`, it might be difficult to sift through all this data and even more complicated to set up alerts and automate responses. This is where [Sematext Logs](https://sematext.com/logsene/) comes in: with a lightweight tool such as AuditBeat or a [log shipper](https://sematext.com/blog/logstash-alternatives/), you can [aggregate](https://sematext.com/blog/log-aggregation/) audit logs across all hosts of your infrastructure. Once data is in, you can slice and dice it through customizable [dashboards](https://sematext.com/docs/dashboards/) or the API, create [alerts](https://sematext.com/docs/alerts/), or rely on [anomaly detection](https://sematext.com/glossary/anomaly-detection/) – so you can react to anything suspicious in a timely manner.

Watch the video below to learn more about Sematext Logs or try the [14-day free trial](https://apps.sematext.com/ui/registration) to test it out yourself.

### Frequently Asked Questions

What is the difference between Syslog and Auditd?

Syslog is a standard for computer message logging, allowing various devices and applications to generate and collect log messages. On the other hand, Auditd is a Linux security feature that provides a framework for monitoring and logging security-related events, such as file access and user authentication, for the purpose of enhancing system security and auditing. While syslog is a general-purpose logging mechanism, auditd specifically focuses on security-related events

[Start Free Trial](https://apps.sematext.com/ui/registration)

* * *

No related posts.

### [API Response TimeDefinition: What Is API Response Time? API response time is...](https://sematext.com/glossary/api-response-time/)### [Anomaly DetectionWhat Are Anomalies? Anomalies mean outliers or inconsistent data points,...](https://sematext.com/glossary/anomaly-detection/)### [AIOpsDefinition: What Is AIOps? Artificial Intelligence for IT Operations (AIOps)...](https://sematext.com/glossary/aiops/)

**********

[аудит](/tags/audit.md)
[auditd](/tags/auditd.md)
