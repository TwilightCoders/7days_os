import platform

from django.db import models


class 7days_os(models.Model):
    """
    Django model describing every tunable setting for 7days_os
    """

    enable = models.BooleanField(default=False)
    7days_os_ssl = models.BooleanField(
        verbose_name="Enable SSL",
        default=False,
        )
    7days_os_cert = models.CharField(
        verbose_name="SSL Certificate",
        max_length=500,
        default='/etc/ssl/certs/7days_os.crt',
        )
    7days_os_key = models.CharField(
        verbose_name="SSL Private Key",
        max_length=500,
        default='/etc/ssl/certs/7days_os.key',
        )
    7days_os_port = models.IntegerField(
        verbose_name="WebUI Port",
        default=8080,
        )
    7days_os_mask = models.BooleanField(
        verbose_name="Mask Password",
        default=False,
        )
    7days_os_locale = models.CharField(
        verbose_name="Localization",
        default="en",
        choices=(
            ("en", 'English'),
            ("nl", 'Dutch'),
            ("ru", 'Russian'),
            ("fr", 'French'),
        ),
        max_length=120,
        )
    7days_os_delay = models.IntegerField(
        verbose_name="Commit Delay (seconds)",
        default=10,
        )
    7days_os_basedir = models.CharField(
        verbose_name="Base Directory",
        max_length=500,
        default='/var/games/minecraft',
        )
    7days_os_log = models.CharField(
        verbose_name="Logfile",
        max_length=500,
        default='/var/log/7days_os.log',
        )
