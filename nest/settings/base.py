# Django settings for nest project.
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from unipath import Path

# from .gargoyle_switches import *

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise ImproperlyConfigured(error_msg)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

GARGOYLE_AUTO_CREATE = True

ADMINS = (
    ('Philip James', 'philip@immaculateobsession.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nest.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

PROJECT_ROOT = Path(__file__).ancestor(3)

MEDIA_ROOT = PROJECT_ROOT.child('media')
STATIC_ROOT = ''
STATICFILES_DIRS = (
    PROJECT_ROOT.child('static'),
)
TEMPLATE_DIRS = (
    PROJECT_ROOT.child('templates'),
)
STATIC_URL = '/static/'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1234567890'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pebbles.middleware.PebbleMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'petroglyphs.context_processors.setting_injector',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ROOT_URLCONF = 'nest.urls'

TESTING = False

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nest.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.redirects',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comics',
    'petroglyphs',
    'suit',
    'django.contrib.admin',
    'suit_redactor',
    # 'nexus',
    # 'gargoyle',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    # TODO: tumblr support in the next verstion, maybe?
    # 'allauth.socialaccount.providers.tumblr',
    'allauth.socialaccount.providers.twitter',
    'datetimewidget',
    'rest_framework',
    'saltpeter',
    'pebbles',
    'profiles',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

#ALLAUTH SETTINGS
LOGIN_REDIRECT_URL = '/pebbles/'
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_UNIQUE_EMAIL=True
ACCOUNT_EMAIL_SUBJECT_PREFIX="[Inkpebble]"

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'METHOD': 'oauth2',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pjj@philipjohnjames.com'
EMAIL_HOST_PASSWORD = get_env_variable('MANDRILL_KEY')
DEFAULT_FROM_EMAIL = 'site@inkpebble.com'
SERVER_EMAIL = 'site@inkpebble.com'

MIXPANEL_KEY = get_env_variable('MIXPANEL_KEY')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'loggly': {
            'format':'loggly: %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false',],
        },
        'mail_error': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'post_to_social': {
            'handlers': ['mail_error'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# try:
#     from mezzanine.utils.conf import set_dynamic_settings
# except ImportError:
#     pass
# else:
#     set_dynamic_settings(globals())
