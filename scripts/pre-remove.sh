#!/bin/sh
# script run before deletion of the PBI file

seven_days_os_pbi_path=/usr/pbi/7days_os-$(uname -m)

${seven_days_os_pbi_path}/etc/rc.d/7days_os forcestop 2>/dev/null || true
