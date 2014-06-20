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

- export BRAND=[BRAND ID]
- cp -R brands/sample brands/$BRAND
- git add brands/$BRAND
- heroku create $BRAND-reallocate-staging
- add new site id to django_sites on staging
- add new settings to brands.settings (vim brands/settings.py)
- git commit -am "Adding new brand ($BRAND)"
- git remote add $BRAND-reallocate-staging git@heroku.com:$BRAND-reallocate-staging.git
- git push $BRAND-reallocate-staging master
- ./heroku-copy-config reallocate-staging $BRAND-reallocate-staging
- heroku config:set BRAND=$BRAND --app $BRAND-reallocate-staging
- curl http://$BRAND-reallocate-staging.herokuapp.com