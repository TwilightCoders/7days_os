from subprocess import Popen, PIPE
import json
import time
import urllib2
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

import jsonrpclib
import oauth2 as oauth
from 7days_osUI.freenas import forms, models, utils

from syslog import *

def _linprocfs_check(linprocfs_path):
    try:
        open(os.path.join(linprocfs_path, 'uptime'), 'rb')
        return True
    except IOError:
        return False

def _linprocfs_mount(server, plugin_id):
    try:
        linprocfs_path = '/usr/compat/linux/proc'
        linprocfs = _linprocfs_check(linprocfs_path)
        if linprocfs is False:
            server.fs.linprocfs(plugin_id, linprocfs_path)
    except:
        jail_path = server.plugins.jail.path(plugin_id)
        linprocfs_path = linprocfs_path.lstrip('/')
        linprocfs_path = os.path.join(jail_path, linprocfs_path)
        return HttpResponse(simplejson.dumps({
            'error': True,
            'message': 'Please run "mount -t linprocfs linprocfs ' + linprocfs_path + '" first.',
        }), content_type='application/json')

class OAuthTransport(jsonrpclib.jsonrpc.SafeTransport):
    def __init__(self, host, verbose=None, use_datetime=0, key=None,
            secret=None):
        jsonrpclib.jsonrpc.SafeTransport.__init__(self)
        self.verbose = verbose
        self._use_datetime = use_datetime
        self.host = host
        self.key = key
        self.secret = secret

    def oauth_request(self, url, moreparams={}, body=''):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time())
        }
        consumer = oauth.Consumer(key=self.key, secret=self.secret)
        params['oauth_consumer_key'] = consumer.key
        params.update(moreparams)

        req = oauth.Request(method='POST', url=url, parameters=params, body=body)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, None)
        return req

    def request(self, host, handler, request_body, verbose=0):
        request = self.oauth_request(url=self.host, body=request_body)
        req = urllib2.Request(request.to_url())
        req.add_header('Content-Type', 'text/json')
        req.add_data(request_body)
        f = urllib2.urlopen(req)
        return(self.parse_response(f))


class JsonResponse(HttpResponse):
    """
    This is a response class which implements FreeNAS GUI API

    It is not required, the user can implement its own
    or even open/code an entire new UI just for the plugin
    """

    error = False
    type = 'page'
    force_json = False
    message = ''
    events = []

    def __init__(self, request, *args, **kwargs):

        self.error = kwargs.pop('error', False)
        self.message = kwargs.pop('message', '')
        self.events = kwargs.pop('events', [])
        self.force_json = kwargs.pop('force_json', False)
        self.type = kwargs.pop('type', None)
        self.template = kwargs.pop('tpl', None)
        self.form = kwargs.pop('form', None)
        self.node = kwargs.pop('node', None)
        self.formsets = kwargs.pop('formsets', {})
        self.request = request

        if self.form:
            self.type = 'form'
        elif self.message:
            self.type = 'message'
        if not self.type:
            self.type = 'page'

        data = dict()

        if self.type == 'page':
            if self.node:
                data['node'] = self.node
            ctx = RequestContext(request, kwargs.pop('ctx', {}))
            content = render_to_string(self.template, ctx)
            data.update({
                'type': self.type,
                'error': self.error,
                'content': content,
            })
        elif self.type == 'form':
            data.update({
                'type': 'form',
                'formid': request.POST.get("__form_id"),
                'form_auto_id': self.form.auto_id,
                })
            error = False
            errors = {}
            if self.form.errors:
                for key, val in self.form.errors.items():
                    if key == '__all__':
                        field = self.__class__.form_field_all(self.form)
                        errors[field] = [unicode(v) for v in val]
                    else:
                        errors[key] = [unicode(v) for v in val]
                error = True

            for name, fs in self.formsets.items():
                for i, form in enumerate(fs.forms):
                    if form.errors:
                        error = True
                        for key, val in form.errors.items():
                            if key == '__all__':
                                field = self.__class__.form_field_all(form)
                                errors[field] = [unicode(v) for v in val]
                            else:
                                errors["%s-%s" % (
                                    form.prefix,
                                    key,
                                    )] = [unicode(v) for v in val]
            data.update({
                'error': error,
                'errors': errors,
                'message': self.message,
            })
        elif self.type == 'message':
            data.update({
                'error': self.error,
                'message': self.message,
            })
        else:
            raise NotImplementedError

        data.update({
            'events': self.events,
        })
        if request.is_ajax() or self.force_json:
            kwargs['content'] = json.dumps(data)
            kwargs['content_type'] = 'application/json'
        else:
            kwargs['content'] = (
                "<html><body><textarea>"
                + json.dumps(data) +
                "</textarea></body></html>"
                )
        super(JsonResponse, self).__init__(*args, **kwargs)

    @staticmethod
    def form_field_all(form):
        if form.prefix:
            field = form.prefix + "-__all__"
        else:
            field = "__all__"
        return field


def start(request, plugin_id):
    (7days_os_key, 7days_os_secret) = utils.get_7days_os_oauth_creds()

    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=7days_os_key, secret=7days_os_secret)

    server = jsonrpclib.Server(url, transport=trans)
    auth = server.plugins.is_authenticated(
        request.COOKIES.get("sessionid", "")
        )
    jail_path = server.plugins.jail.path(plugin_id)
    assert auth

    _linprocfs_mount(server, plugin_id)

    try:
        7days_os = models.7days_os.objects.order_by('-id')[0]
        7days_os.enable = True
        7days_os.save()
    except IndexError:
        7days_os = models.7days_os.objects.create(enable=True)

    try:
        form = forms.7days_osForm(7days_os.__dict__, instance=7days_os, jail_path=jail_path)
        form.is_valid()
        form.save()
    except ValueError:
        return HttpResponse(simplejson.dumps({
            'error': True,
            'message': ('7days_os data did not validate, configure '
                'it first.'),
            }), content_type='application/json')

    cmd = "%s onestart" % utils.7days_os_control
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, close_fds=True)

    out = pipe.communicate()[0]
    return HttpResponse(simplejson.dumps({
        'error': False,
        'message': out,
        }), content_type='application/json')


def stop(request, plugin_id):
    (7days_os_key, 7days_os_secret) = utils.get_7days_os_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=7days_os_key, secret=7days_os_secret)

    server = jsonrpclib.Server(url, transport=trans)
    auth = server.plugins.is_authenticated(
        request.COOKIES.get("sessionid", "")
        )
    jail_path = server.plugins.jail.path(plugin_id)
    assert auth

    _linprocfs_mount(server, plugin_id)

    try:
        7days_os = models.7days_os.objects.order_by('-id')[0]
        7days_os.enable = False
        7days_os.save()
    except IndexError:
        7days_os = models.7days_os.objects.create(enable=False)

    try:
        form = forms.7days_osForm(7days_os.__dict__,
            instance=7days_os,
            jail_path=jail_path)
        form.is_valid()
        form.save()
    except ValueError:
        pass

    cmd = "%s onestop" % utils.7days_os_control
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
        shell=True, close_fds=True)

    out = pipe.communicate()[0]
    linprocfs_path = '/usr/compat/linux/proc'
    linprocfs = _linprocfs_check(linprocfs_path)
    while linprocfs is True:
        server.fs.umount(plugin_id, linprocfs_path)
        linprocfs = _linprocfs_check(linprocfs_path)
    return HttpResponse(simplejson.dumps({
        'error': False,
        'message': out,
        }), content_type='application/json')


def edit(request, plugin_id):
    (7days_os_key, 7days_os_secret) = utils.get_7days_os_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=7days_os_key, secret=7days_os_secret)

    """
    Get the 7days_os object
    If it does not exist create a new entry
    """
    try:
        7days_os = models.7days_os.objects.order_by('-id')[0]
    except IndexError:
        7days_os = models.7days_os.objects.create()

    try:
        server = jsonrpclib.Server(url, transport=trans)
        jail_path = server.plugins.jail.path(plugin_id)
        jail = json.loads(server.plugins.jail.info(plugin_id))[0]['fields']
        jail_ipv4 = jail['jail_ipv4'].split('/')[0]
        if 7days_os.7days_os_ssl:
                7days_os_scheme = "https"
        else:
                7days_os_scheme = "http"
        7days_os_port = 7days_os.7days_os_port
        auth = server.plugins.is_authenticated(
            request.COOKIES.get("sessionid", "")
            )
        assert auth
    except Exception as e:
        raise

    if request.method == "GET":
        form = forms.7days_osForm(instance=7days_os, jail_path=jail_path)
        return render(request, "edit.html", {
            'form': form,
            'ipv4': jail_ipv4,
            'scheme': 7days_os_scheme,
            'port': 7days_os_port
        })

    if not request.POST:
        return JsonResponse(request, error=True, message="A problem occurred.")

    form = forms.7days_osForm(request.POST, instance=7days_os, jail_path=jail_path)
    if form.is_valid():
        form.save()

        cmd = "%s restart" % utils.7days_os_control
        pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, close_fds=True)

        return JsonResponse(request, error=True, message="7days_os settings successfully saved.")

    return JsonResponse(request, form=form)


def treemenu(request, plugin_id):
    """
    This is how we inject nodes to the Tree Menu

    The FreeNAS GUI will access this view, expecting for a JSON
    that describes a node and possible some children.
    """

    (7days_os_key, 7days_os_secret) = utils.get_7days_os_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=7days_os_key, secret=7days_os_secret)
    server = jsonrpclib.Server(url, transport=trans)
    jail = json.loads(server.plugins.jail.info(plugin_id))[0]
    jail_name = jail['fields']['jail_host']
    number = jail_name.rsplit('_', 1)
    name = "7days_os"
    if len(number) == 2:
        try:
            number = int(number)
            if number > 1:
                name = "7days_os (%d)" % number
        except:
            pass

    plugin = {
        'name': name,
        'append_to': 'plugins',
        'icon': reverse('treemenu_icon', kwargs={'plugin_id': plugin_id}),
        'type': 'pluginsfcgi',
        'url': reverse('7days_os_edit', kwargs={'plugin_id': plugin_id}),
        'kwargs': {'plugin_name': '7days_os', 'plugin_id': plugin_id },
    }

    return HttpResponse(json.dumps([plugin]), content_type='application/json')


def status(request, plugin_id):
    """
    Returns a dict containing the current status of the services

    status can be one of:
        - STARTING
        - RUNNING
        - STOPPING
        - STOPPED
    """
    pid = None

    proc = Popen(["/usr/local/etc/rc.d/7days_os", "onestatus"],
        stdout=PIPE,
        stderr=PIPE)

    stdout = proc.communicate()[0]

    if proc.returncode == 0:
        status = 'RUNNING'
        pid = stdout.split('\n')[0]
    else:
        status = 'STOPPED'

    return HttpResponse(json.dumps({
            'status': status,
            'pid': pid,
        }),
        content_type='application/json')


def treemenu_icon(request, plugin_id):

    with open(utils.7days_os_icon, 'rb') as f:
        icon = f.read()

    return HttpResponse(icon, content_type='image/png')
