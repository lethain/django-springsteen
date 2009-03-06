try:
    import google.appengine.api
    def cache_get(key):
        return google.appengine.api.memcache.get(key)
    def cache_put(key, value, duration):
        google.appengine.api.memcache.add(key, value, duration)

except ImportError:
    import django.core.cache
    def cache_get(key):
        return django.core.cache.cache.get(key)
    def cache_put(key, value, duration):
        django.core.cache.cache.set(key, value, duration)
