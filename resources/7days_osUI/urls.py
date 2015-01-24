from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
     url(r'^plugins/7days_os/(?P<plugin_id>\d+)/', include('7days_osUI.freenas.urls')),
)
