from website.urls import *

# override brand-specific URLS patterns
urlpatterns = patterns('',

  url(r'^project/new/$', 'cobrands.freespace.views.new_project', name='new-project'),

) + urlpatterns
