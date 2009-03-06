# Settings for devel server
import os
ROOT_PATH = os.path.dirname(__file__)
DEBUG = True
TEMPLATE_DEBUG = DEBUG
CACHE_BACKEND='file://%s/django_cache' % ROOT_PATH
DATABASE_ENGINE = None
DATABASE_NAME = None
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

ROOT_URLCONF = 'urls'
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.doc.XViewMiddleware',
)
INSTALLED_APPS = (
    'springsteen',
)
CACHE_BACKEND = "dummy:///"
