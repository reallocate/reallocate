from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
from myproject import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'myproject.views.home', name='home'),
                       url(r'', include('social_auth.urls')),
                       url(r'^$', 'website.views.homepage', name='homepage'),
                       url(r'^about$', 'website.views.about', name='about'),
                       url(r'^signup', 'website.views.signup'),
                       url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),

                       url(r'^add_organization', 'website.views.add_organization', name='add_organization'),
                       url(r'^organization/(?P<oid>\d+)/add_project', 'website.views.add_project', name='add_project'),
                       url(r'^organization/(?P<pid>\d+)', 'website.views.view_organization', name='view_organization'),
                    
                       url(r'^add_project', 'website.views.add_project', name='add_project'),
                       url(r'^project/(?P<oid>\d+)/add_opportunity', 'website.views.add_opportunity', name='add_opportunity'),
                       url(r'^project/(?P<pid>\d+)', 'website.views.view_project', name='view_project'),

                       url(r'^add_opportunity', 'website.views.add_opportunity', name='add_opportunity'),
                       url(r'^opportunity/(?P<pid>\d+)', 'website.views.view_opportunity', name='view_opportunity'),
 
                       url(r'^opportunity/(?P<pid>\d+)$', 'website.views.view_opportunity', name='view_opportunity'),
                       url(r'^find-opportunity', 'website.views.opportunity_list', name='opportunity_list'),
                       url(r'^opportunity/(?P<pid>\d+)/engage', 'website.views.engage', name='engage'),

                       url(r'^ajax/modify_project_relation', 'website.ajaxviews.modify_project_relation', name='modify_project_relation'),
                       url(r'^login', 'website.views.login_user', name='login_user'),

                       # couldn't figure out how to make the o-auth pages not default send to /private
                       # so what should be /profile is staying /private for now.
                       url(r'^profile', 'website.views.profile', name='profile'),

                       # Admin site
                       url(r'^admin/', include(admin.site.urls)),

                       # Server Static Files from Django
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
                       
                       url(r'^search', 'website.views.search', name='search'),
)
