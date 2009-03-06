from springsteen.views import search as default_search
from springsteen.services import Web
from django.conf import settings


def search(request, timeout=2500, max_count=10):
    services = (Web,)
    return default_search(request, timeout, max_count, services)
