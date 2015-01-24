import hashlib
import json
import os
import pwd
import urllib

from django.utils.translation import ugettext_lazy as _

from dojango import forms
from 7days_osUI.freenas import models, utils

class 7days_osForm(forms.ModelForm):

    class Meta:
        model = models.7days_os
        widgets = {
            '7days_os_port': forms.widgets.TextInput(),
            '7days_os_delay': forms.widgets.TextInput(),
        }
        exclude = (
            'enable',
            )

    def __init__(self, *args, **kwargs):
        self.jail_path = kwargs.pop('jail_path')
        super(7days_osForm, self).__init__(*args, **kwargs)

        self.fields['7days_os_cert'].widget = \
        self.fields['7days_os_key'].widget = \
        self.fields['7days_os_log'].widget = forms.widgets.TextInput(attrs={
            'data-dojo-type': 'freeadmin.form.PathSelector',
            'root': self.jail_path,
            'dirsonly': 'false',
            })

        self.fields['7days_os_basedir'].widget = forms.widgets.TextInput(attrs={
            'data-dojo-type': 'freeadmin.form.PathSelector',
            'root': self.jail_path,
            'dirsonly': 'true',
            })

    def save(self, *args, **kwargs):
        obj = super(7days_osForm, self).save(*args, **kwargs)

        rcconf = os.path.join(utils.7days_os_etc_path, "rc.conf")
        with open(rcconf, "w") as f:
            if obj.enable:
                f.write('7days_os_enable="YES"\n')

        settingsfile = os.path.join(utils.7days_os_etc_path, "7days_os.conf")
        settings = {}

        for field in obj._meta.local_fields:
            if field.attname not in utils.7days_os_settings:
                continue
            info = utils.7days_os_settings.get(field.attname)
            value = getattr(obj, field.attname)
            _filter = info.get("filter")
            if _filter:
                settings[info.get("field")] = _filter(value)
            else:
                settings[info.get("field")] = value

        with open(settingsfile, 'w') as f:
            f.write('[global]\n')
            f.write('server.socket_host = "0.0.0.0"\n')
            f.write('server.socket_port = %d\n' % (obj.7days_os_port, ))
            f.write('server.commit_delay = %d\n' % (obj.7days_os_delay, ))
            f.write('log.error_file = "%s"\n' % (obj.7days_os_log, ))
            f.write('server.ssl_module = "builtin"\n')
            f.write('server.ssl_certificate = "%s"\n' % (obj.7days_os_cert, ))
            f.write('server.ssl_private_key = "%s"\n' % (obj.7days_os_key, ))
            f.write('server.ssl_ca_certificate =\n')
            f.write('server.ssl_certificate_chain =\n')
            f.write('misc.server_as_daemon = True\n')
            f.write('misc.pid_file = "/var/run/7days_os.pid"\n')
            f.write('misc.require_https = %r\n' % (obj.7days_os_ssl, ))
            f.write('misc.base_directory = "%s"\n' % (obj.7days_os_basedir, ))
            f.write('misc.localization = "%s"\n' % (obj.7days_os_locale, ))
            f.write('webui.mask_password = %r' % (obj.7days_os_mask, ))

        os.system(os.path.join(utils.seven_days_os_pbi_path, "tweak-rcconf"))
