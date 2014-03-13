from website.urls import *

# override brand-specific URLS patterns
urlpatterns = patterns('',

  #url(r'^about$', 'website.views.about', name='about'),

) + urlpatterns
