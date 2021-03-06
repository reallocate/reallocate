import os, sys, socket, re, logging

ALLOWED_HOSTS = ['.reallocate.org', '.herokuapp.com']

# invite system
INVITE_ONLY = True if 'INVITE_ONLY' in os.environ and os.environ['INVITE_ONLY'] == 'true' else False

# email settings
EMAIL_BACKEND = 'django_ses.SESBackend'
FROM_EMAIL = "Reallocate <noreply@reallocate.org>"
ADMIN_EMAIL = "admin@reallocate.org"

SEND_EMAILS = True if os.environ.get('SEND_EMAILS') and os.environ['SEND_EMAILS'] == 'true' else False

# parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default': dj_database_url.config(default='sqlite:/data.db')}

# allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be defined per machine.
if 'DEPLOY_ENV' in os.environ and os.environ['DEPLOY_ENV'] != 'local':

    DEPLOY_ENV = os.environ['DEPLOY_ENV']
    DEBUG = True if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'true' else False
    S3_BUCKET = os.environ.get('S3_BUCKET')
    AWS_STORAGE_BUCKET_NAME = S3_BUCKET

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

    STRIPE_KEY_PUB = os.environ.get('STRIPE_KEY_PUB')
    STRIPE_KEY_SECRET = os.environ.get('STRIPE_KEY_SECRET')

    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_API_SECRET = os.environ.get('FACEBOOK_API_SECRET')

    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_API_SECRET = os.environ.get('FACEBOOK_API_SECRET')

    LINKEDIN_CONSUMER_KEY = os.environ.get('LINKEDIN_CONSUMER_KEY')
    LINKEDIN_CONSUMER_SECRET = os.environ.get('LINKEDIN_CONSUMER_SECRET')

    GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
    GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
    GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = os.environ.get('GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS')
    GOOGLE_EXTRA_DATA = os.environ.get('GOOGLE_EXTRA_DATA')
    GOOGLE_SREG_EXTRA_DATA = os.environ.get('GOOGLE_SREG_EXTRA_DATA')
    GOOGLE_AX_EXTRA_DATA = os.environ.get('GOOGLE_AX_EXTRA_DATA')

else:

    DEPLOY_ENV = 'local'
    DEBUG = True
    try:
        from settings_local import *
    except ImportError:
        print '\nYou must create a settings_local.py file!\n'


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# add libs to PYTHONPATH
sys.path.insert(0, os.path.join(PROJECT_ROOT, "website", "libs"))

APP_NAME = 'website'

SITE_ORG_ID = os.environ.get('SITE_ORG_ID')   # used for matching site with an org model

ADMINS = (('admin', 'admin@reallocate.org'),)

MANAGERS = ADMINS

TIME_ZONE = 'America/Vancouver'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = os.path.join(PROJECT_ROOT, "static_root")
#STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

STATIC_ROOT = os.path.join(PROJECT_ROOT, APP_NAME, 'staticfiles')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    #os.path.join(PROJECT_ROOT, APP_NAME, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'e!!qskok^h9v_!klh-dq1@przcl2jwvp1=751x5xjquscq6phm'

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'website.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'website.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'website.base.context',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'widget_tweaks',
    'website',
    #'taggit',
    'django.contrib.admin',
    'social_auth',
    #'storages',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

AUTHENTICATION_BACKENDS = (
    #    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    #    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    #    'social_auth.backends.browserid.BrowserIDBackend',
    #    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #    'social_auth.backends.contrib.orkut.OrkutBackend',
    #    'social_auth.backends.contrib.foursquare.FoursquareBackend',
    #    'social_auth.backends.contrib.github.GithubBackend',
    #    'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    #    'social_auth.backends.contrib.live.LiveBackend',
    #    'social_auth.backends.contrib.skyrock.SkyrockBackend',
    'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    #    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.user.update_user_details',
    'website.base.associate_new_user_profile',
)

AUTH_PROFILE_MODULE = 'website.UserProfile'

GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}
GOOGLE_EXTRA_DATA = [('oauth_token', 'oauth_token')]
GOOGLE_SREG_EXTRA_DATA = [('oauth_token', 'oauth_token')]
GOOGLE_AX_EXTRA_DATA = [('oauth_token', 'oauth_token')]

FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'publish_stream']

# https://developer.linkedin.com/documents/profile-fields
LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress']
LINKEDIN_EXTRA_FIELD_SELECTORS = ['email-address', 'headline', 'industry', 'picture-url', 'first-name', 'last-name']
LINKEDIN_EXTRA_DATA = [
    ('id', 'id'),
    ('first-name', 'first_name'),
    ('last-name', 'last_name'),
    ('email-address', 'email_address'),
    ('headline', 'headline'),
    ('industry', 'industry'),
    ('picture-url', 'profile_picture')
]

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
POST_LOGIN_URL = '/search'
#LOGIN_ERROR_URL = '/login-error/'
#LOGOUT_URL= '/accounts/logout/'

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
SOCIAL_AUTH_UUID_LENGTH = 16

# honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

# setup brand
BRAND = os.environ.get('BRAND', 'reallocate')

from brands.settings import *

STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'brands', BRAND, 'static'),)
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'brands', BRAND, 'templates'),)
