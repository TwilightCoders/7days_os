#!/bin/sh
# script run before installation of the PBI; return non-0 to halt installation

# https://www.patpro.net/blog/index.php/2013/08/04/2502-running-source-dedicated-server-on-freebsd-9-x/
# Prerequisites are the same, you must first install the linux compatibility layer:
# As root, load the module & make sure it will be loaded after reboot:

# `kldload linux`
#echo 'linux_enable="YES"' >> /etc/rc.conf

#echo 'WITHOUT_X11=yes' >> /etc/make.conf

#`mkdir -p /usr/compat/linux/proc`

#echo 'linproc	/usr/compat/linux/proc	linprocfs	rw 0 0'

#`mount -a`
