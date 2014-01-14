from .base import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default'] = dj_database_url.config()

SECRET_KEY = get_env_variable("SECRET_KEY")

ALLOWED_HOSTS = [
    '.captainquail.com',
    '.inkpebble.com',
    '.quailcomics.com',
    '.herokuapp.com',
    'localhost',
    '127.0.0.1'
]

STATIC_URL = 'http://inkpebble.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)
