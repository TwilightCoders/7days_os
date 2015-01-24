#!/bin/sh
# script run immediately after the extraction of PBI contents to disk

# http://forum.i3d.net/threads/hlds_linux-steamcmd-on-freebsd.184049/

seven_days_os_pbi_path=/usr/pbi/7days_os-$(uname -m)

${seven_days_os_pbi_path}/bin/python2.7 ${seven_days_os_pbi_path}/7days_osUI/manage.py syncdb --migrate --noinput

curl -L -o ${seven_days_os_pbi_path}/steamcmd_linux.tar.gz http://media.steampowered.com/installer/steamcmd_linux.tar.gz
cd ${seven_days_os_pbi_path}
tar zxf steamcmd_linux.tar.gz

# https://steamdb.info/app/251570/
# 251570 7 Days 2 Die App ID

# https://wiki.teamfortress.com/wiki/Linux_dedicated_server

# Will install as well
./update.sh
