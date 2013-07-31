ReAllocate Web Platform 
============================
This open source project is for the ReAllocate (reallocate.org) marketplace, where knowledge meets need.

PREREQUISITES

- Python 2.7
- SQLite, MySQL, or something similar
- (OS X) XCode or CLI

INITIAL SETUP

- git clone git@github.com:reallocate/reallocate.git
- sudo pip-2.7 install -r requirements.txt
- create a settings_local.py file next to settings.py (you can find our private keys in our DropBox folder)
- ./manage.py syncdb (it will offer to create a superuser; answer "no" -- you get admin / admin for free)
- ./manage.py runserver

OPTIONAL SETUP

If you want to be able to connnect to AWS, Google, LinkedIn, etc you will need to add those keys. To do so:

- create myproject/settings_local.py
- put all your overrides in there.  if you are a ReAllocate core team member, you can find this file in our Dropbox
