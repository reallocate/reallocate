# Local settings
import os

FACEBOOK_APP_ID = 'xxxxxxxx'
FACEBOOK_API_SECRET = 'xxxxxxxx'
GOOGLE_OAUTH2_CLIENT_ID = '991028767654.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'hNtl2LmCuZ-lEWJWMFIZigdY'

GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}
GOOGLE_EXTRA_DATA = [('oauth_token', 'oauth_token')]
GOOGLE_SREG_EXTRA_DATA = [('oauth_token', 'oauth_token')]
GOOGLE_AX_EXTRA_DATA = [('oauth_token', 'oauth_token')]

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

DEPLOY_ENV = 'local'

# email settings
FROM_EMAIL = "xxxxxxx@gmail.com"
TO_EMAIL = ["xxxxxxx@gmail.com"]