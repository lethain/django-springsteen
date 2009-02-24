from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from springsteen.services import News, Web, News
from django.utils import simplejson
from time import time

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


def search(request, timeout=2500, max_count=10, services=(Web,), extra_params={}):
    """
    
    timeout:      a global timeout for all requested services
    max_count:    used to prevent resource draining URL hacking
    services:     services to query with search terms
    extra_params: overrides and extra parameters for searches
    """
    query = request.GET.get('query',None)
    results = []
    total_results = 0
    try:
        count = int(request.GET.get('count','10'))
    except ValueError:
        count = 10
    count = min(count, max_count)

    try:
        start = int(request.GET.get('start','0'))
    except ValueError:
        start = 0
    start = max(start, 0)

    if query:
        params = {
            'count': count,
            'start': start,
            }
        params.update(extra_params)
        threads = [ x(query, params) for x in services ]
        for thread in threads:
            thread.start()
        multi_join(threads, timeout=timeout)
        for thread in threads:
            results = results + thread.results()
            total_results = total_results + thread.total_results
        results = results[:count]

    range = [ start+1, min(start+count,total_results) ]
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
    return render_to_response("springsteen/results.html",context)
