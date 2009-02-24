from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^service/$', 'example_project.views.service'),
    (r'^service2/$', 'example_project.views.service2'),
    (r'^$', 'example_project.views.search'),
)
