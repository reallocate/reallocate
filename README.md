ReAllocate, The Platform 
============================
This open source project is for the ReAllocate (reallocate.org) marketplace, where knowledge meets need.

PREREQUISITES

- Python 2.7
- pip
- SQLite

INITIAL DEV SETUP
OPTIONAL: use [virtualenv](http://www.virtualenv.org/) to create an isolated python environment for your ReAllocate development

- git clone git@github.com:reallocate/reallocate.git
- sudo pip-2.7 install -r requirements.txt (if using a virtualenv, omit sudo)
- mv website/settings_local_sample.py website/settings_local.py
- ./manage.py syncdb --all (create a db superuser if you'd like)
- ./manage.py migrate --fake
- ./manage.py runserver

NEW BRAND SETUP

- cp -R brands/sample brands/[BRAND_ID]
- git add brands/[BRAND_ID]
- create new heroku app
- add new site id to django_sites on staging
- add new settings to brands.settings
- commit changes
- inital push to heroku app
- heroku config:set BRAND=[BRAND_ID] --app [HEROKU_APP_ID]
- ./heroku_copy_config reallocate-staging [HEROKU_APP_ID]