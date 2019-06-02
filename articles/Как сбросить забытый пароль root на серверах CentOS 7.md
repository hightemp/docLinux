# Как сбросить забытый пароль root на серверах CentOS 7

To get started, turn on the machine that you’ve forgotten the root password on. For CentOS 7 devices, you’ll be given 5 seconds at the boot menu to select the operating system kernel to boot into.

That 5 seconds is important, because allows for  admins to select different kernels or edit existing kernel parameters before booting.

At the boot menu, press**e**to edit the existing kernel (Core) as shown below.

[![Changing root password on centos 7](/images/6639ad12dfb81779c5ab262634ba2ba3.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password.png)

[  
](https://is.ltroute.com/click.track?CID=420817&AFID=426982&SID=liberiangeek&nonencodedurl=https://www.fandomcentre.com/products/doctor-who-spinning-3d-tardis-police-box-pendant-necklace-w-30-chain)

Next, scroll down to the list until you see the line underlined below (**ro**) . What we need to do is change that ro to rw and start into a bash shell. It should look like this**rw init=/sysroot/bin/sh.**

[![forgotten root password on centos 7](/images/fec0c31cfaf6dc4587d9008125b9a50d.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-1.png)

Change the**ro**line to**rw**and add**init=/sysroot/bin/sh**

```
rw init=/sysroot/bin/sh
```

[![changing root password on centos](/images/91ec5236a7880cf72f8d01ebe5b1775f.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-2.png)

After changing that, press**Control + X** or**Ctrl + X** on your keyboard to start into single user mode using the bash shell specified above. In this mode, we’re going to change the root password.

In the single user mode, run the command as shown below

```
chroot /sysroot
```

[![password change on centos 7](/images/5db43420e207098a193135248fcae6cb.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-3.png)

Finally, run the commands below to change the root password.

[![change password on centos 7](/images/629515fa748d692d5f3e254117e5f55a.png)](https://www.liberiangeek.net/wp-content/uploads/2014/09/centos7-forgot-root-password-4.png)


You’ll be prompted to create and confirm a new password.  After creating the password, run the commands below to update SELinux parameters

```
touch /.autorelabel
```

Exit and reboot your system. You should be able to sign on and use the system with the new password you created. That’s how you change the root password on CentOS 7.