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
                       url(r'^learn$', 'website.views.learn', name='learn'),
                       url(r'^signup', 'website.views.signup'),
                       url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),

                       url(r'^add_organization', 'website.views.add_organization', name='add_organization'),
                       url(r'^organization/(?P<oid>\d+)/add_project', 'website.views.add_project', name='add_project'),
                    
                       url(r'^add_project', 'website.views.add_project', name='add_project'),
                       url(r'^project/(?P<pid>\d+)/add_opportunity', 'website.views.add_opportunity', name='add_opportunity'),
                       url(r'^project/(?P<pid>\d+)', 'website.views.view_project', name='view_project'),

                       url(r'^opportunity/(?P<oid>\d+)/engage', 'website.views.engage', name='engage'),
                       url(r'^opportunity/(?P<oid>\d+)$', 'website.views.view_opportunity', name='view_opportunity'),

                       url(r'^ajax/modify-project-relation', 'website.ajaxviews.modify_project_relation', name='modify_project_relation'),
                       url(r'^ajax/add-update', 'website.ajaxviews.add_update', name='add_update'),
                       url(r'^ajax/check-available', 'website.ajaxviews.check_available', name=''),
                       
                       url(r'^login', 'website.views.login_user', name='login_user'),
                       url(r'^ajax/login', 'website.ajaxviews.login_user'),

                       url(r'^profile/(?P<username>[^/]+)', 'website.views.public_profile', name='public_profile'), # public view
                       url(r'^profile', 'website.views.profile', name='profile'), # private settings page

                       # pay-pal receiver
                       url(r'^paypal', 'website.paypal.receive_paypal', name='paypal'),
                       
                       # test urls
                       url(r'^test_email', 'website.views.test_email', name='test_emails'),
                       
                       # Admin site
                       url(r'^admin/', include(admin.site.urls)),

                       # Server Static Files from Django
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
                       
                       url(r'^search', 'website.views.search', name='search'),
)
