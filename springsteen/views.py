from django.shortcuts import render_to_response
from django.http import HttpResponse
from springsteen.services import Web, Images, News
from django.utils import simplejson
from time import time
from django.conf import settings
import springsteen.utils

def multi_join(threads, timeout=None):
    'Join multiple threads with shared timeout.'
    for thread in threads:
        start = time()
        thread.join(timeout)
        if timeout is not None:
            timeout -= time() - start

def dummy_retrieve_func(query, start, count):
    """
    This is a dummy function for retrieving results.
    It should be replaced by a real function that
    return data in the same format.
    """
    data = {
        'total_results': 0,
        'results':[],
        }
    return simplejson.dumps(data)


def service(request, retrieve_func=dummy_retrieve_func, mimetype="application/json"):
    query = request.GET.get('query',None)
    if query:
        try:
            count = int(request.GET.get('count','10'))
        except ValueError:
            count = 10
        try:
            start = int(request.GET.get('start','0'))
        except ValueError:
            start = 0
        start = max(start, 0)
        return HttpResponse(retrieve_func(query, start,count), mimetype=mimetype)
    return HttpResponse('{"total_results":0, "results":[] }',
                        mimetype='application/json')


def fetch_results_batch(query, timeout, services, params):
    "Perform a batch of requests and aggregate results."
    threads = [ x(query, params) for x in services ]
    for thread in threads:
        thread.start()
    multi_join(threads, timeout=timeout)
    total_results = 0
    results = []
    unexhausted_services = []
    for thread in threads:
        if not thread.exhausted():
            unexhausted_services.append(thread.__class__)
        results = results + thread.results()
        total_results = total_results + thread.total_results

    return results, total_results, unexhausted_services


def search(request, timeout=2500, max_count=10, services=(), \
               extra_params={}, reranking_func=None, extra_context={},\
               render=True):
    """
    timeout:      a global timeout for all requested services
    max_count:    used to prevent resource draining URL hacking
    services:     services to query with search terms
    extra_params: overrides and extra parameters for searches
    reranking_func: function for reranking all results
    extra_context: extra stuff passed to the template for rendering
    """
    query = request.GET.get('query',None)
    results = []
    total_results = 0
    try:
        count = int(request.GET.get('count','%s' % max_count))
    except ValueError:
        count = 10
    count = min(count, max_count)
    try:
        start = int(request.GET.get('start','0'))
    except ValueError:
        start = 0
    start = max(start, 0)

    if query:
        # log the query
        springsteen.utils.log_query(query)

        # because we are aggregating distributed resources,
        # we don't know how many results they will return,
        # so finding the 30th result (for example) has potential
        # to be rather complex
        #
        # instead we must build up results from 0th to nth result
        # due to the caching of service results, this ideally
        # still only requires one series of requests if the
        # user is paginating through results (as opposed to jumping
        # to a high page, for example)
        batch_start = 0
        batch_count = count
        batch_i = 0
        batch_result_count = 0
        batches = []
        max_batches = getattr(settings, 'SPRINGSTEEN_MAX_BATCHES', 3)
        while batch_result_count < start+count and \
                len(services) > 0 and \
                batch_i < max_batches:
            params = {'count':batch_count, 'start':batch_start}
            params.update(extra_params)
            batch, total_results, services = fetch_results_batch(query, timeout, services, params)
            batch_result_count = batch_result_count + len(batch)
            batches.append(batch)
            
            batch_start = batch_start + batch_count
            batch_i = batch_i + 1


        # hook for providing custom ranking for results
        # we have to rerank each batch individually to
        # preserve ordering (otherwise you might have results
        # from the first batch pushed into the second batch,
        # and thus have results occur on multiple pages.
        if reranking_func:
            reranked_batches = []
            for batch in batches:
                reranked = reranking_func(query, batch)
                reranked_batches.append(reranked)
            batches = reranked_batches

        for batch in batches:
            results = results + batch
    
        # remove duplicate results
        new_results = []
        seen = {}
        for result in results:
            url = result['url']
            if not seen.has_key(url):
                new_results.append(result)
                seen[url] = True
        results = new_results
        results = results[start:start+count]

    if render:
        range = ( start+1, min(start+count,total_results) )
        next_start = start + count
        previous_start = start - count
        has_next = range[1] < total_results
        has_previous = range[0] > 1
        context = {
            'query': query,
            'count': count,
            'start': start,
            'range': range,
            'has_next': has_next,
            'has_previous': has_previous,
            'next_start': next_start,
            'previous_start': previous_start,
            'results': results,
            'total_results': total_results,
            }
        context.update(extra_context)
        return render_to_response("springsteen/results.html",context)
    else:
        return {'total_results': total_results,
                'results': results,
                'start': start,
                'count': count }


def web(request, timeout=2500, max_count=10, extra_params={}):
    services = (Web,)
    return search(request,timeout,max_count,services,extra_params)


def images(request, timeout=2500, max_count=10, extra_params={}):
    services = (Images,)
    return search(request,timeout,max_count,services,extra_params)


def news(request, timeout=2500, max_count=10, extra_params={}):
    services = (News,)
    return search(request,timeout,max_count,services,extra_params)
