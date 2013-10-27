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

STATIC_URL = 'http://media.quailcomics.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'loggly': {
            'format':'loggly: %(message)s',
        },
    },
    'handlers': {
        'logging.handlers.SysLogHandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local5',
            'formatter': 'loggly',
        },
    },
    'loggers': {
        'loggly_logs':{
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format':'loggly: %(message)s',
            'level': 'DEBUG',
        },
    }
}