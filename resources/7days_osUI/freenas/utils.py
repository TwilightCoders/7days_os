from subprocess import Popen, PIPE
import hashlib
import os
import platform

seven_days_os_pbi_path = "/usr/pbi/7days_os-" + platform.machine()
7days_os_etc_path = os.path.join(seven_days_os_pbi_path, "etc")
7days_os_fcgi_pidfile = "/var/run/7days_os_fcgi_server.pid"
7days_os_control = "/usr/local/etc/rc.d/7days_os"
7days_os_icon = os.path.join(seven_days_os_pbi_path, "default.png")
7days_os_oauth_file = os.path.join(seven_days_os_pbi_path, ".oauth")


def get_rpc_url(request):
    return 'http%s://%s:%s/plugins/json-rpc/v1/' % (
        's' if request.is_secure() else '',
        request.META.get("SERVER_ADDR"),
        request.META.get("SERVER_PORT"),
        )


def get_7days_os_oauth_creds():
    f = open(7days_os_oauth_file)
    lines = f.readlines()
    f.close()

    key = secret = None
    for l in lines:
        l = l.strip()

        if l.startswith("key"):
            pair = l.split("=")
            if len(pair) > 1:
                key = pair[1].strip()

        elif l.startswith("secret"):
            pair = l.split("=")
            if len(pair) > 1:
                secret = pair[1].strip()

    return key, secret

7days_os_settings = {
    "7days_os_ssl": {
        "field": "7days_os_ssl",
        "type": "checkbox",
        },
    "7days_os_cert": {
        "field": "7days_os_cert",
        "type": "textbox",
        },
    "7days_os_key": {
        "field": "7days_os_key",
        "type": "textbox",
        },
    "7days_os_port": {
        "field": "7days_os_port",
        "type": "textbox",
        },
    "7days_os_mask": {
        "field": "7days_os_mask",
        "type": "checkbox",
        },
    "7days_os_locale": {
        "field": "7days_os_locale",
        "type": "textbox",
        },
    "7days_os_delay": {
        "field": "7days_os_delay",
        "type": "textbox",
        },
    "7days_os_basedir": {
        "field": "7days_os_basedir",
        "type": "textbox",
        },
    "7days_os_log": {
        "field": "7days_os_log",
        "type": "textbox",
        }
}
