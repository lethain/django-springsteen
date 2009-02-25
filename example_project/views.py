from springsteen.views import search as default_search
from springsteen.views import service
from springsteen.services import Web
from django.utils import simplejson

class DjangoProjectSearch(Web):
    def __init__(self, query, params={}):
        super(Web, self).__init__(query, params)
        self.params['sites']='djangoproject.com'

def search(request, timeout=2000, max_count=5, services=(DjangoProjectSearch,), extra_params={}):
    return default_search(request, timeout, max_count, services, extra_params)


def my_retrieve_func(query, start, count):
    def random_data(query):
        return {
            'title': "random %s" % query,
            'url': "http://example.com/%s/" % query,
            'abstract': '%s %s %s' % (query,query,query),
            }
    results = [ random_data(query) for x in range(count) ]
    dict = { 'total_results': 1000, 'results': results, }
    return simplejson.dumps(dict)

def service2(request):
    return service(request, retrieve_func=my_retrieve_func)
