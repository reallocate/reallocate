import os

BRAND = os.environ.get('BRAND', 'reallocate')

if BRAND == 'onearmenia':

	ALLOWED_HOSTS = ['.onearmenia.org', '.herokuapp.com']
	SITE_ID = 3
	SITE_IDS = [3]

elif BRAND == 'freespace':

	SITE_ORG_ID = os.environ.get('SITE_ORG_ID', '1')
	SITE_ID = 2
	SITE_IDS = [2]

elif BRAND == 'nil':

	SITE_ID = 4
	SITE_IDS = [4]

else:

	SITE_ID = 1
	SITE_IDS = [1,2]