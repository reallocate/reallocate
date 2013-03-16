from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'myproject.views.home', name='home'),
                       url(r'', include('social_auth.urls')),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

                       url(r'^$', 'website.views.homepage', name='homepage'),
                       
                       url(r'^add_project/$', 'website.views.add_project', name='add_project'),
                       url(r'^project/(.*?)/add_opportunity/$', 'website.views.add_opportunity', name='add_opportunity'),
                       
                       url(r'^project/(.*?)$', 'website.views.view_project', name='view_project'),
                       url(r'^opportunity/(.*?)$', 'website.views.view_opportunity', name='view_opportunity'),
                       
                       url(r'^login', 'website.views.login_page', name='login_page'),

                       url(r'^private$', 'website.views.private', name='private'),
                       # url(r'^test$', 'website.views.test', name='test'),

                       # url("^index", TemplateView.as_view(template_name='index.html'), name="mission"),

                       # Admin site
                       #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )