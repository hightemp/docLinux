# Приложения TCP/IP на примерах

In this tutorial we'll implement some simple TCP/IP applications with `ncat` , `bash` and some other standard UNIX tools. The principles learned here can be used to implement networking applications in other languages.

The `$` or `#` in front of command line examples denotes the system prompt. Do not type it yourself.

To run the examples, you need an operating system conforming to POSIX (eg. \*BSD or macOS) or Linux. The `ncat` program, usually bundled with `nmap` , is also required.

You can install `nmap` differently on different systems; on Ubuntu and other Debian-based distros, the following command should work:

```
$ sudo apt install nmap

```

> USE THESE EXAMPLES AT YOUR OWN RISK. Examples may have vulnerabilities, and should never be exposed to public Internet. Configure your firewall properly before proceeding.

#  [](https://gist.github.com/ilmoeuro/11284639#basic-usage-of-ncat) Basic usage of `ncat` 

Ncat is a simple tool for command line network I/O. It can be used either as a client or as a server. It's similar to the popular `netcat` program, but offers simultaneous connections for server use.

The program works by opening a network connection, sending all standard input to that network connection and printing all incoming data to standard output.

To use as a client, use the following command:

```
$ ncat <target-address> <target-port> 

```

To use as a server, use as follows:

```
$ ncat -lp <listen-port> 

```

The listening socket is closed when you quit the program, for example withCtrl\-C.

Let's try it out! From one shell (terminal window), type:

```
$ ncat -lp 10101 

```

From other shell, enter the following command:

```
$ ncat localhost 10101 

```

Now you can type something into one shell and it shows up in the other. TypeCtrl\-Dfrom the client side to quit.

If you want to learn more, read the `ncat` man page:

```
$ man ncat

```

#  [](https://gist.github.com/ilmoeuro/11284639#example-1-motd-server) Example 1: MOTD-server

The simplest possible server is one that sends a fixed message to the client when connected to. Example session:

```

CLIENT                      SERVER
|                           listening
|                           |
*  ------- connect ------>  *
|                           |
|                           |
*  <------ message -------  *
|                           |
|                           |
*  -- close connection -->  *
|                           |
|                           |


```

To implement the server, we'll use the magic `-c` option of Ncat:

```
$ ncat -c "echo hello world" -lp 10101 

```

This runs the given command ( `echo hello world` ) when a remote client connects to Ncat. The output of the command is sent to the client.

There's no need for a separate client, just use client mode:

```
$ ncat localhost 10101
hello world

```

To end the session, type Control-D.

Now, the server exits after one client connection. This can be changed with the `-k` (keep open) option.

#  [](https://gist.github.com/ilmoeuro/11284639#example-2-echo-server) Example 2: Echo server

Echo server just echoes everything sent to it back to the client. An UNIX program that does the same thing (without parameters) is called `cat` . So, can we use `cat` to implement an echo server? Type this to the "server" console:

```
$ ncat -c cat -lp 10101 -k

```

Let's use the same client as last time:

```
$ ncat localhost 10101

```

Now everything we type is echoed back after newline!

```
$ ncat localhost 10101
is this on?
is this on?
this is echoed.
this is echoed.

```

#  [](https://gist.github.com/ilmoeuro/11284639#example-3-chat-server) Example 3: Chat server

Echo server is fun, but it only echoes to the same client that sent the message. If we echoed the message to all clients, we could implement a simple chat/relay server. The problem is, all `ncat -c` connections run in separate processes, so we need a way to communicate between processes. Files and `tail -f` is perharps the simplest way to do real-time communication between processes.

Our chat server will have two components. One that receives messages and appends them to our shared file:

```
cat >>messages

```

And one that listens to the shared file and sends forward all the messages added to it. The `-f` switch makes `tail` keep listening to `messages` and outputting any new lines added to it:

```
tail -f messages

```

If we combine them, we got our relay server!

```
$ ncat -c "cat >>messages | tail -f messages" -lp 10101 -k

```

Now open _two_ new shells/terminal windows and open a client in both:

```
$ ncat localhost 10101

```

Now the two clients can chat with each other. One problem with this chat client is that you see the messages you send twice. We'll fix that problem in a later example.

#  [](https://gist.github.com/ilmoeuro/11284639#example-4-simple-http-server) Example 4: Simple HTTP server

HTTP is a text-based protocol, so it's pretty easy to read and write HTTP messages. It's also a _request-response_ protocol: Each interaction between the client and the server is the client sending a _request_ to the server and the server responding with a _response_ . If the server always responds with the same response, we can just simply write it in a file and just send it every time.

Let's write a simple HTTP response:

```
HTTP/1.0 200 OK
Content-type: text/html; charset=utf-8
Connection: close


<!doctype html>
<html>
<head><title>Hello world</title></head>
<body>
<h1>Hello world</h1>
<img src="http://placecage.com/500/500" alt="">
</body>
</html>

```

Save the response to a file named `response.txt` . Now we can implement our server. Type the following in the same directory where `responses.txt` is:

```
$ ncat -c "cat response.txt" -lp 8080 -k

```

Now open your web browser, surf to `http://localhost:8080/` , and enjoy your "hello world" page!

#  [](https://gist.github.com/ilmoeuro/11284639#example-5-improved-chat-server) Example 5: Improved chat server

This version of the chat server has an identifier for each participant, so people can have conversations. Because `ncat` starts a new process for each client, we can use the process ID as the identifier. We can also filter outgoing messages based on the ID, so the problem with duplicate messages goes away.

We add 2 more programs to the pipeline of example 3 to accomplish this. The first one is added to the front, and it appends the process ID (available in environment variable `$PPID` ) to each incoming line. The `-u` flag turns off buffering in `sed` , so it works with interactive input/output from the network.

```
sed -ue "s/^/$PPID: /"

```

The second one is added to the end of the pipeline, and it filters out all the messages that start with the process ID ( `$PPID` ). We need to turn off buffering here too, with `--line-buffered` . The flag `-v` makes `grep` remove the matching lines instead of retaining them.

```
grep --line-buffered -v "^$PPID:"

```

Now, let's run the complete chat server that looks like this:

```
$ ncat -c 'sed -ue "s/^/$PPID: /"  | cat >>messages | tail -f messages | grep --line-buffered -v "^$PPID:"' -lp 10101 -k

```

Now open _two_ new shells/terminal windows and open a client in both:

```
$ ncat localhost 10101

```

The two clients can chat with each other. Now we have fixed the problems present in example 3.

#  [](https://gist.github.com/ilmoeuro/11284639#example-6-fuzz-testing) Example 6: Fuzz testing

Fuzz testing means feeding random input to a program, hopefully triggering edge cases in input processing and exposing bugs or vulnerabilities. `ncat` can be used for simple fuzz testing, there's more specialized programs for more advanced use cases. First, you need something to fuzz test. `ncat` can act both as a client and a server, so you can test both kinds of programs. Let's fuzz test our browser first! We can fuzz two parts of our program separately: the HTTP engine and the HTML engine. Let's first test the HTTP engine by just returning random (invalid) HTTP responses. This command will respond to requests with 1 000 000 bytes of random data ( `head -c` reads the given number of bytes from the file given as a parameter, and `/dev/urandom` is a file containing an infinite amount of random data).

```
$ ncat -c "head -c 1000000 /dev/urandom" -lp 8080 -k

```

Open a new browser and browse to `http://localhost:8080/` . In my tests, Firefox showed a lot of gibberish, and Chrome displayed an "invalid HTTP response" page. **I increased the amount of data to 1 000 000 000 bytes, and managed to crash my Firefox** .

Let's use the "header" part of the response from example 4, but instead of a fixed HTML message, we output random gibberish. First save the header part in a file named `response1.txt` , **note the empty lines in the end** :

```
HTTP/1.0 200 OK
Content-type: text/html; charset=utf-8
Connection: close



```

Now we can serve random data with the correct HTTP header part:

```
$ ncat -c "head -c 1000000 /dev/urandom | cat response1.txt -" -lp 8080 -k

```

If you try again opening the page with Chrome, you see a lot of gibberish (like with Firefox) instead of an "invalid response" message. You can also try to increase the amount of data and see if you can crash Chrome that way. Try other browsers too, you may be able to invoke more interesting behaviour (like segmentation faults) with lesser-known browsers.

**********
[bash](/tags/bash.md)
[ncat](/tags/ncat.md)
[НЕ ПЕРЕВЕДЕНО](/tags/%D0%9D%D0%95%20%D0%9F%D0%95%D0%A0%D0%95%D0%92%D0%95%D0%94%D0%95%D0%9D%D0%9E.md)
