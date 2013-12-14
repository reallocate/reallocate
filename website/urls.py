from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
from website import settings

admin.autodiscover()

urlpatterns = patterns('',

  url(r'', include('social_auth.urls')),
  url(r'^$', 'website.views.home', name='home'),
  url(r'^about$', 'website.views.about', name='about'),
  url(r'^privacy$', 'website.views.privacy', name='privacy'),
  url(r'^tos$', 'website.views.tos', name='tos'),
  url(r'^get-started$', 'website.views.get_started', name='get_started'),
  url(r'^sign-up$', 'website.views.sign_up'),
  url(r'^login$', 'website.views.login_user', name='login_user'),
  url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
  url(r'^forgot-password$', 'website.views.forgot_password', name='forgot_password'),
  url(r'^reset-password$', 'website.views.reset_password', name='reset_password'),

  url(r'^organization/new/$', 'website.views.new_organization', name='new_organization'),
  url(r'^project/new/$', 'website.views.new_project', name='new_project'),
  url(r'^project/(?P<pid>\d+)/opportunity/(?P<oid>\d+)/$', 'website.views.view_opportunity', name='view_opportunity'),
  url(r'^project/(?P<pid>\d+)/opportunity/add/$', 'website.views.add_opportunity', name='add_opportunity'),
  url(r'^project/(?P<pid>\d+)/manage/$', 'website.views.manage_project', name='manage_project'),
  url(r'^project/(?P<pid>\d+)/$', 'website.views.view_project', name='view_project'),

  url(r'^ajax/modify-project-relation', 'website.ajax_views.modify_project_relation', name='modify_project_relation'),
  url(r'^ajax/engage-opportunity', 'website.ajax_views.engage_opportunity', name='engage_opportunity'),
  url(r'^ajax/close-opportunity', 'website.ajax_views.close_opportunity', name='close_opportunity'),
  url(r'^ajax/add-update', 'website.ajax_views.add_update', name='add_update'),
  url(r'^ajax/check-available', 'website.ajax_views.check_available'),
  url(r'^ajax/check-org-name', 'website.ajax_views.check_org_name'),
  url(r'^ajax/get-orgs', 'website.ajax_views.get_orgs'),
  url(r'^ajax/login', 'website.ajax_views.login_user'),
  url(r'^ajax/update-project', 'website.ajax_views.update_project'),
  url(r'^ajax/delete-opportunity', 'website.ajax_views.delete_opportunity'),
  url(r'^ajax/invite-users', 'website.ajax_views.invite_users'),

  url(r'^profile/?(?P<username>[^/]+)?', 'website.views.profile', name='profile'),    # public view

  # pay-pal receiver
  url(r'^paypal', 'website.paypal.receive_paypal', name='paypal'),

  # test urls
  url(r'^test_email', 'website.views.test_email', name='test_emails'),

  # Admin site
  url(r'^admin/', include(admin.site.urls)),

  # Server Static Files from Django
  url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),

  url(r'^find-opportunity', 'website.views.find_opportunity', name='find_opportunity'),
)
