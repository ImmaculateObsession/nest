from .base import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default'] = dj_database_url.config()

ALLOWED_HOSTS = [
    '.captainquail.com',
    '.quailcomics.com',
    '.herokuapp.com',
    'localhost',
    '127.0.0.1'
]

STATIC_URL = 'http://media.quailcomics.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)