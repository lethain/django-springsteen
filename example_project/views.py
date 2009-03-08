from springsteen.views import search as default_search
from springsteen.views import service
from springsteen.services import Web, MetawebService, DeliciousPopularService, TwitterLinkSearchService
from django.utils import simplejson


def search(request, timeout=2000, max_count=20, extra_params={}):
    services = (DeliciousPopularService, Web)
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
