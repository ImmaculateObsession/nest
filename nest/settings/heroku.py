from .base import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

try:
    DATABASES['default'] = dj_database_url.config()
except ImproperlyConfigured:
    DATABASES = {
        'default': {
            'ENGINE': 'postgresql_psycopg2',
            'NAME': 'quailcomics',
            'USER': 'quailcomics',
            'PASSWORD': 'quailcomics',
            'HOST': '192.241.228.250',
            'PORT': '49158',
        }
    }

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