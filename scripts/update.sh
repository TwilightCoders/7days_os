#!/bin/sh

# https://wiki.teamfortress.com/wiki/Linux_dedicated_server

seven_days_os_pbi_path=/usr/pbi/7days_os-$(uname -m)

./steam.sh +runscript ${seven_days_os_pbi_path}/resources/update.txt
