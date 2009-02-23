from django.conf.urls.defaults import *

urlpatterns = patterns(
    'springsteen.views',
    url(r'^search/$', 'search', name='search'),
)
                       
