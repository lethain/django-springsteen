from springsteen.views import search as default_search
from springsteen.services import Web, TwitterLinkSearchService, AmazonProductService
from django.conf import settings

class AppleAmazonSearch(AmazonProductService):
    _access_key = settings.AMAZON_ACCESS_KEY
    _topic = 'apple'

class AppleTwitterService(TwitterLinkSearchService):
    _qty = 3
    _topic = 'apple'


def hostname(url):
    return url.replace('http://','').split('/')[0]

def ranking(query, results):
    query = query.lower()
    def rank(result):
        score = 0.0
        title = result['title'].lower()
        if title in query:
            score += 1.0
        return score

    scored = [(rank(x), x) for x in results]
    scored2 = []
    domains = {}
    for score, result in scored:
        domain = result['url'].replace('http://','').split('/')[0]
        times_viewed = domains.get(domain, 0)
        new_score = score + times_viewed * -0.1
        scored2.append((new_score, result))
        domains[domain] = times_viewed + 1
        
    scored2.sort()
    return [ x[1] for x in scored2 ]


def search(request, timeout=2500, max_count=10):
    services = (AppleAmazonSearch, AppleTwitterService, Web)
    return default_search(request, timeout, max_count,
                          services, {}, ranking)           
