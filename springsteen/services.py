from urllib import urlopen
from threading import Thread
from django.utils import simplejson
from django.conf import settings
from django.core.cache import cache

class Service(Thread):
    total_results = 0
    _results = []

    def __init__(self, query, params={}):
        super(Service, self).__init__()
        self.query = query.replace(' ','+')
        self.params = params.copy()

    def run(self):
        return False

    def count(self):
        return len(self._results)

    def results(self):
        return self._results

    def exhausted(self):
        'Return whether a service has no additional results for query.'
        start = self.params['start']
        count = self.params['count']
        return start+count >= self.total_results 

class CachableService(Service):
    _cache_duration = 60 * 30

    def make_cache_key(self):
        key = "%s,%s,%s" % (self.__class__, self.query, self.params)
        return key.replace(" ","")

    def retrieve_cache(self):
        "Need to overload to decode cached data properly."
        pass

    def store_cache(self, raw):
        cache.set(self.make_cache_key(), raw, self._cache_duration)

class HttpCachableService(CachableService):
    _source = 'web'

    def uri(self):
        'Return full uri for query.'
        return None

    def decode(self, results):
        return None

    def retrieve_cache(self):
        cached = cache.get(self.make_cache_key())
        if cached != None:
            self.decode(cached)

    def run(self):
        self.retrieve_cache()
        if not self._results:
            request = urlopen(self.uri())
            raw = request.read()
            self.store_cache(raw)
            self.decode(raw)

    def results(self):
        for result in self._results:
            if result.has_key('source'):
                result['_source'] = result['source']
            result['source'] = self._source
        return self._results


class SpringsteenService(HttpCachableService):
    _uri = ""
    _source = 'springsteen'

    def uri(self):
        uri = "%s?query=%s" % (self._uri, self.query)
        if self.params.has_key('start'):
                uri = "%s&start=%s" % (uri, self.params['start'])
        return uri

    def decode(self, results):
        data = simplejson.loads(results)
        self._results = data['results']
        self.total_results = data['total_results']


class BossSearch(HttpCachableService):

    def uri(self):
        query = self.query.replace(' ','+')
        uri = "http://boss.yahooapis.com/ysearch/%s/v1/%s?appid=%s&format=json" \
            % (self._source, query, settings.BOSS_APP_ID)
        params = ["&%s=%s" % (p, self.params[p]) for p in self.params]
        return "%s%s" % (uri, "".join(params))

    def decode(self, results):
        results = simplejson.loads(results)
        self.total_results = int(results['ysearchresponse']['totalhits'])
        self._results = results['ysearchresponse']['resultset_%s' % self._service]



class Web(BossSearch):
    _source = "web"

class Images(BossSearch):
    _source = "images"

class News(BossSearch):
    _source = "news"
