from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2',
        'NAME': 'quailcomics',
        'USER': 'angel',
        'PASSWORD': 'whatdidtheusairdrop',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_URL = 'http://media.quailcomics.com/assets/'