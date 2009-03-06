try:
    # Setup utilities for App Engine deployment
    import google.appengine.api

    def cache_get(key):
        return google.appengine.api.memcache.get(key)

    def cache_put(key, value, duration):
        google.appengine.api.memcache.add(key, value, duration)

    def log_query(msg):
        pass


except ImportError:
    # Setup utilities for normal Django deployment
    from django.conf import settings
    import django.core.cache
    import logging, os

    def cache_get(key):
        return django.core.cache.cache.get(key)
    def cache_put(key, value, duration):
        django.core.cache.cache.set(key, value, duration)

    if getattr(settings, 'SPRINGSTEEN_LOG_QUERIES', False):
        def get_logger(name, file):
            logger = logging.getLogger(name)
            hdlr = logging.FileHandler(os.path.join(settings.SPRINGSTEEN_LOG_DIR, file))
            formatter = logging.Formatter('%(message)s') 
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)
            logger.setLevel(logging.INFO)
            return logger

        QUERY_LOGGER = get_logger('findjango','queries.log')

        def log_query(msg):
            QUERY_LOGGER.info(msg.lower())
        
    else:
        def log_query(msg):
            pass


