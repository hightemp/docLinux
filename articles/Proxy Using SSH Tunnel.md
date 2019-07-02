# Proxy Using SSH Tunnel

###  A simple example

Let’s start with a simple example. We can access a sshd server  _sshd\_server_  and we want to use it as a socks5 proxy server. It is simple by using ssh:

$ ssh -D 8080 username@sshd\_server

After that, set the browser such as firefox’s proxy option to use socks5 proxy 127.0.0.1:8080. That’s it!

Then, check whether your IP is from the proxy from the websites’ view:  [Who am I](http://www.pkill.info/whoami/) .

###  Making ssh proxy 

We can set up a more complex proxy server through ssh. For example, we have a sshd server s2 and another server s1 as the proxy server. Then we can set up a proxy server system using ssh tunnel. s1 will act as the proxy server, while s2 connects to the service provider (s3). The overall system can be shown as this:

c0:p0 <--> s1:p1 <==> s2:p2 <--> s3

Maybe most of the time c0 and s1 are the same machines as the simple example at the beginning of the post.

Using ssh as a proxy to browse the web is very useful under some situation: Local access restriction such as behind a strict firewall in some country, company or school; You are in a insecure  [network](https://www.systutorials.com/category/tutorial/network/)  environment while you want to login to your account.

Now let’s look at how to set up proxy by using ssh tunnel. This uses ssh’s “dynamic” port forwarding function by using parameter “-D”. ssh allocates a socket to listen to port on the local side, optionally bound to the specified ip address. Whenever a connection is made to this port, the connection is forwarded over the ssh channel, and the application protocol is then used to determine where to connect to from the remote machine.

####  1) Proxy listening to localhost port only 

This proxy server can only be used on localhost, which means the other users can not use it. c0 and s1 in the graph above are the same machine.  
The command is:

$ ssh -D p1 username@sshd\_server

p1 is the port on localhost. Any port larger than 1024 can be chosen as p1. After setting up this proxy tunnel, set the proxy option in browser to  _127.0.0.1:p1_  and using socks5. Then it is done. Enjoy it now :) .

####  2) Proxy listening to specific IP 

This kind of proxy server can provide service to other users. Users (and include yourself of course) can use this socks5 proxy with address  _s1\_ip_  and port  _p1_ .  
The command is:

$ ssh -D s1\_ip:p1 username@sshd\_server

This command sets up a socks5 proxy server on s1. The proxy address is:  _s1\_ip:p1_ .

*   Some useful ssh arguments
    

There are some other ssh arguments that can make the port forwarding more convenient for us:

\-C  Requests gzip compression of all data
-T  Disable pseudo-tty allocation
-N  Do not execute a remote command. This is useful for just forwarding ports.
-f  Requests ssh to go to background just before command execution.
-n  Redirects stdin from /dev/null (actually, prevents reading from stdin).
-q  Quiet mode. Causes most warning and diagnostic messages to be suppressed.

These arguments can be used with -D for different usages. I like to use this combination:

$ ssh -CnfND 8080 username@sshd\_server

When I want to close the ssh proxy tunnel, I need to find the  _pid_  of it by

$ ps aux | grep ssh

and then kill it.

Or let it run in the shell:

$ ssh -CTND 8080 username@sshd\_server

You can also configure it to listen on all addresses on the host by:

$ ssh -D "\*:8080" username@sshd\_server

###  Port forwarding squid proxy 

This post mainly focus on using ssh to build up the proxy system. But the connection between the client and the other kind of proxy server such as squid can also make use of ssh tunnel. I only provides a simple example here, while more details of ssh port forwarding can be found from  [Port Forwarding using ssh Tunnel](https://www.systutorials.com/b/818/port-forwarding-using-ssh-tunnel/) . For example, the proxy server and port is  _proxy:port_ . Now we can port forwards port 8080 on localhost to it by this:

$ ssh -L 8080:proxy:port username@sshd\_server

####  Global Proxy in GNOME with NetworkManager on  [Linux](https://www.systutorials.com/category/tutorial/linux/)   [∞](https://www.systutorials.com/944/proxy-using-ssh-tunnel/#global-proxy-in-gnome-with-networkmanager-on-linux "Link to this section")  

If you are using Linux with NetworkManager, it is very convenient to set up the global proxy of GNOME to use the socks proxy created by SSH.

 ![](/images/fd9d21a01d3788f1d8c166454930cf2b.png)

**********
[ssh](/tags/ssh.md)
