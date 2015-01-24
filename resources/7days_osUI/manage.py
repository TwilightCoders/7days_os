#!/usr/bin/env python2.7

import os
import sys
import platform

arch = platform.machine()
python_major = sys.version_info.major
python_minor = sys.version_info.minor
python = "python%d.%d" % (python_major, python_minor)

7days_os_PATH = "/usr/pbi/7days_os-%s" % arch
7days_os_UI = os.path.join(7days_os_PATH, "7days_osUI")
PYTHON_SITE_PACKAGES = os.path.join(7days_os_PATH,"lib/%s/site-packages" % python)

sys.path.append(PYTHON_SITE_PACKAGES)
sys.path.append(7days_os_PATH)
sys.path.append(7days_os_UI)

os.environ["DJANGO_SETTINGS_MODULE"] = "7days_osUI.settings"

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
