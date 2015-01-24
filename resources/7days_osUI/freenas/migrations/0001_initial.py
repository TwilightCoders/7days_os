# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model '7days_os'
        db.create_table('freenas_7days_os', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('7days_os_ssl', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('7days_os_cert', self.gf('django.db.models.fields.CharField')(default='/etc/ssl/certs/7days_os.crt', max_length=500)),
            ('7days_os_key', self.gf('django.db.models.fields.CharField')(default='/etc/ssl/certs/7days_os.key', max_length=500)),
            ('7days_os_port', self.gf('django.db.models.fields.IntegerField')(default=8080)),
            ('7days_os_mask', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('7days_os_locale', self.gf('django.db.models.fields.CharField')(default='en', max_length=120)),
            ('7days_os_delay', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('7days_os_basedir', self.gf('django.db.models.fields.CharField')(default='/var/games/minecraft', max_length=500)),
            ('7days_os_log', self.gf('django.db.models.fields.CharField')(default='/var/log/7days_os.log', max_length=500)),
        ))
        db.send_create_signal('freenas', ['7days_os'])


    def backwards(self, orm):

        # Deleting model '7days_os'
        db.delete_table('freenas_7days_os')


    models = {
        'freenas.7days_os': {
            'Meta': {'object_name': '7days_os'},
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '7days_os_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '7days_os_cert': ('django.db.models.fields.CharField', [], {'default': "'/etc/ssl/certs/7days_os.crt'", 'max_length': '500'}),
            '7days_os_key': ('django.db.models.fields.CharField', [], {'default': "'/etc/ssl/certs/7days_os.key'", 'max_length': '500'}),
            '7days_os_port': ('django.db.models.fields.IntegerField', [], {'default': '8080'}),
            '7days_os_mask': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '7days_os_locale': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '120'}),
            '7days_os_delay': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            '7days_os_basedir': ('django.db.models.fields.CharField', [], {'default': "'/var/games/minecraft'", 'max_length': '500'}),
            '7days_os_log': ('django.db.models.fields.CharField', [], {'default': "'/var/log/7days_os.log'", 'max_length': '500'})
        }
    }

    complete_apps = ['freenas']
