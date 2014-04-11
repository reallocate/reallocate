import os, sys, socket, re, logging

from website.settings import *

APP_NAME = 'onearmenia'

ALLOWED_HOSTS += ['.onearmenia.org']

ROOT_URLCONF = 'cobrands.onearmenia.urls'
INSTALLED_APPS = ('cobrands.onearmenia',) + INSTALLED_APPS
MIDDLEWARE_CLASSES += ('cobrands.onearmenia.Middleware',)
STATICFILES_DIRS += (os.path.join(PROJECT_ROOT, 'cobrands', APP_NAME, 'static'),)

BRAND = {
    'id': 'onearmenia',
    'name': 'One Armenia',
}