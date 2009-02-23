from springsteen.views import search as default_search
from springsteen.services import Web

class DjangoProjectSearch(Web):
    _service = "web"
    def __init__(self, query, params={}):
        super(Web, self).__init__(query, params)
        self.params['sites']='djangoproject.com'

def search(request, timeout=2000, max_count=5, services=(DjangoProjectSearch,), extra_params={}):
    return default_search(request, timeout, max_count, services, extra_params)
