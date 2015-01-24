from django.conf.urls import patterns, include, url

urlpatterns = patterns('7days_osUI.freenas.views',
     url(r'^edit$', 'edit', name="7days_os_edit"),
     url(r'^treemenu-icon$', 'treemenu_icon', name="treemenu_icon"),
     url(r'^_s/treemenu$', 'treemenu', name="treemenu"),
     url(r'^_s/start$', 'start', name="start"),
     url(r'^_s/stop$', 'stop', name="stop"),
     url(r'^_s/status$', 'status', name="status"),
)
