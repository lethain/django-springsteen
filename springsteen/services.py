from urllib import urlopen
from threading import Thread
from django.utils import simplejson
from django.conf import settings
from springsteen.utils import cache_get, cache_put
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree



class Service(Thread):
    total_results = 0
    _results = []
    _topic = None
    _qty = None

    def __init__(self, query, params={}):
        super(Service, self).__init__()
        self.query = self.rewrite_query(query)
        self.params = params.copy()

    def rewrite_query(self, query):
        query = query.replace(' ','+')
        if self._topic and not self._topic in query:
            query = "%s+%s" % (self._topic, query)
        return query

    def run(self):
        return False

    def filter_results(self):
        'Limits maximum results fetched from  a given source.'
        if self._qty:
            self._results = self._results[:self._qty]
            self.total_results = len(self._results)

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
        cache_put(self.make_cache_key(), raw, self._cache_duration)

class HttpCachableService(CachableService):
    _source = 'web'

    def uri(self):
        'Return full uri for query.'
        return None

    def decode(self, results):
        pass

    def retrieve_cache(self):
        cached = cache_get(self.make_cache_key())
        if cached != None:
            self.decode(cached)

    def run(self):
        self.retrieve_cache()
        if not self._results:
            request = urlopen(self.uri())
            raw = request.read()
            self.store_cache(raw)
            self.decode(raw)
        self.filter_results()

    def results(self):
        for result in self._results:
            if result.has_key('source'):
                result['_source'] = result['source']
            result['source'] = self._source
        return self._results


class SpringsteenService(HttpCachableService):
    _uri = ""
    _source = 'springsteen'
    _use_start_param = True

    def uri(self):
        uri = "%s?query=%s" % (self._uri, self.query)
        if self._use_start_param and self.params.has_key('start'):
                uri = "%s&start=%s" % (uri, self.params['start'])
        return uri

    def decode(self, results):
        try:
            data = simplejson.loads(results)
            self._results = data['results']
            self.total_results = data['total_results']
        except ValueError:
            pass


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
        self._results = results['ysearchresponse']['resultset_%s' % self._source]


class Web(BossSearch):
    _source = "web"


class Images(BossSearch):
    _source = "images"


class News(BossSearch):
    _source = "news"


class TwitterSearchService(HttpCachableService):
    """
    Returns Twitter search results in SpringsteenService compatible format.

    This service is intentionally restricted to a maximum of ``_qty`` results,
    and will not be queried again throughout pagination.

    I've done it this way because old tweets are likely to have extremely
    low relevency, and I don't want to flood results with them.
    """

    _source = 'springsteen'
    _qty = 3

    def uri(self):
        return 'http://search.twitter.com/search.json?q=%s' % self.query

    def decode(self, results):
        def transform(result):
            return {
                'title':"Twitter: %s" % result['from_user'],
                'image':result['profile_image_url'],
                'url':"http://twitter.com/%s/" % result['from_user'],
                'text':result['text'],
                }

        data = simplejson.loads(results)
        self._results = [ transform(x) for x in data['results'] ]
        self.total_results = len(self._results)

class TwitterLinkSearchService(TwitterSearchService):
    'Returns only Tweets that contain a link.'

    def filter_results(self):
        self._results = [ x for x in self._results if 'http://' in x['text'] ]
        super(TwitterLinkSearchService, self).filter_results()
        

class MetawebService(HttpCachableService):
    _source = 'metaweb'
    _service = 'search'
    _params = ''
    _qty = 3

    def uri(self):
        params = (self._service, self.query, self._params)
        return 'http://www.freebase.com/api/service/%s?query=%s%s' % params
        
    def decode(self, results):
        self._results = simplejson.loads(results)['result']
        def convert(result):
            title = result['name']
            topics = result['type']
            id = result['id']
            aliases = result['alias']
            image = result['image']
            data =  {
                'title':title,
                'text':'',
                'url': id,
                }
            if aliases:
                data['alias'] = aliases
            if topics:
                data['topics'] = topics
            if image:
                data['image'] = image['id']
            return data


        self._results = [ convert(x) for x in self._results ]


class AmazonProductService(HttpCachableService):
    _source = 'springsteen'
    _base_uri = 'http://ecs.amazonaws.com/onca/xml'
    _service = 'AWSECommerceService'
    _source = 'springsteen'
    _access_key=''
    _operation = 'ItemSearch'
    _search_index = 'Books'
    _search_type = 'Title'
    _qty = 2

    def uri(self):
        params = (self._base_uri, self._service,
                  self._access_key, self._operation,
                  self._search_index, self._search_type,
                  self.query)
        return "%s?Service=%s&AWSAccessKeyId=%s&Operation=%s&SearchIndex=%s&%s=%s" % params

    def decode(self, results):
        def tag(name):
            return '{http://webservices.amazon.com/AWSECommerceService/2005-10-05}%s' % name
        self._results = []
        elem = ElementTree.XML(results)
        for item in elem.find(tag('Items')).findall(tag('Item')):
            #asin = item.find(tag('ASIN')).text
            url = item.find(tag('DetailPageURL')).text
            attrs = item.find(tag('ItemAttributes'))
            authors = (attrs.findall(tag('Author')))
            author = ', '.join([x.text for x in authors])
            title = attrs.find(tag('Title')).text
            
            self._results.append({'title': "%s: %s" % (author, title),
                                  'text':'',
                                  'url':url})
        self._results = self._results[:self._qty]
        self.total_results = len(self._results)
