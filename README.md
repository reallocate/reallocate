Django Bootstrap Starter Project
============================
This project makes it really easy to create a Django project and publish it to Heroku.


What is included?
-----------------
* Heroku settings
* Social Auth. (Facebook, Google, Yahoo) Oauth


What you need to get started?
-----------------------------

### Mininmum requirements

* Sign up for AWS account
* Get AWS keys AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


### Advance requirements

* Facebook Oauth keys: FACEBOOK_APP_ID, FACEBOOK_API_SECRET
* Google OAuth keys: GOOGLE_OAUTH2_CLIENT_ID, GOOGLE_OAUTH2_CLIENT_SECRET



Setup Steps
===========

* git clone
* heroku create
* heroku rename <my_cool_project_name>
* source myproject/settings_local.env.sh
* sh myproject/settings_local.heroku.sh
* git push heroku master
* heroku run manage.py syncdb

* Great Success! You are done.


Helpful Commands
================


* Check settings

> heroku config

> printenv


### View logs and status
> heroku logs

> heroku ps

> heroku config


### Heroku 
Deployment of Django on Heroku https://devcenter.heroku.com/articles/django

> heroku run python manage.py syncdb

> heroku run python manage.py migrate website


> heroku domains:add www.example.com


> python manage.py collectstatic --noinput;

> heroku config:add DISABLE_COLLECTSTATIC=1         # To disable static collection

> heroku pg:reset DATABASE