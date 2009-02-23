from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'example_project.views.search'),
)
