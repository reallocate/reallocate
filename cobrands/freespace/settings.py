import os, sys, socket, re, logging

from website.settings import *

APP_NAME = 'freespace'

ROOT_URLCONF = 'cobrands.freespace.urls'
INSTALLED_APPS = ('cobrands.freespace',) + INSTALLED_APPS
MIDDLEWARE_CLASSES += ('cobrands.freespace.Middleware',)
STATICFILES_DIRS += (os.path.join(PROJECT_ROOT, APP_NAME, 'static'),)

BRAND = {
    'id': 'freespace',
    'name': 'Freespace',
}