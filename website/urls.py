from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

class TextPlainView(TemplateView):
  def render_to_response(self, context, **kwargs):
    return super(TextPlainView, self).render_to_response(context, content_type='text/plain', **kwargs)

urlpatterns = patterns('',

  url(r'', include('social_auth.urls')),
  #url(r'^api/', include('reallocate_tastypie.urls')),

  url(r'^$', 'website.views.home', name='home'),
  url(r'^about$', 'website.views.about', name='about'),
  url(r'^privacy$', 'website.views.privacy', name='privacy'),
  url(r'^tou$', 'website.views.tou', name='tou'),
  url(r'^get-started$', 'website.views.get_started', name='get-started'),
  url(r'^sign-up$', 'website.views.sign_up', name='sign-up'),
  url(r'^login$', 'website.views.login_user', name='login'),
  url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
  url(r'^forgot-password$', 'website.views.forgot_password', name='forgot-password'),
  url(r'^reset-password$', 'website.views.reset_password', name='reset-password'),

  url(r'^find-opportunity$', 'website.views.find_opportunity', name='find-opportunity'),
  url(r'^find-project$', 'website.views.find_project', name='find-project'),

  url(r'^projects(/.*?)$', TemplateView.as_view(template_name="projects.html"), name='find-project'),

  url(r'^organization/new/$', 'website.views.new_organization', name='new-organization'),
  url(r'^project/new/$', 'website.views.new_project', name='new-project'),
  url(r'^project/(?P<pid>\d+)/opportunity/(?P<oid>\d+)/$', 'website.views.view_opportunity', name='opportunity'),
  url(r'^project/(?P<pid>\d+)/opportunity/add/(?P<sponsorship>\w*)$', 'website.views.add_opportunity', name='add-opportunity'),
  url(r'^project/(?P<pid>\d+)/manage/$', 'website.views.manage_project', name='manage-project'),
  url(r'^project/(?P<pid>\d+)/$', 'website.views.view_project', name='project'),

  # staff management
  url(r'^manage/projects$', 'website.views.manage_projects', name='manage-projects'),

  url(r'^ajax/projects', 'website.ajax_views.projects'),
  url(r'^ajax/modify-project-relation', 'website.ajax_views.modify_project_relation'),
  url(r'^ajax/engage-opportunity', 'website.ajax_views.engage_opportunity'),
  url(r'^ajax/close-opportunity', 'website.ajax_views.close_opportunity'),
  url(r'^ajax/add-update', 'website.ajax_views.add_update'),
  url(r'^ajax/delete-update', 'website.ajax_views.delete_update'),
  url(r'^ajax/check-available', 'website.ajax_views.check_available'),
  url(r'^ajax/check-org-name', 'website.ajax_views.check_org_name'),
  url(r'^ajax/get-orgs', 'website.ajax_views.get_orgs'),
  url(r'^ajax/login', 'website.ajax_views.login_user'),
  url(r'^ajax/update-project', 'website.ajax_views.update_project'),
  url(r'^ajax/change-project', 'website.ajax_views.change_project'),
  url(r'^ajax/delete-opportunity', 'website.ajax_views.delete_opportunity'),
  url(r'^ajax/invite-users', 'website.ajax_views.invite_users'),

  url(r'^profile', 'website.views.profile', name='profile'),
  url(r'^profile/?(?P<username>[^/]+)?', 'website.views.profile', name='profile'),  # public profile view

  # pay-pal receiver
  url(r'^paypal', 'website.paypal.receive_paypal'),

  # stripe handlers
  url(r'^stripe-subscription', 'website.views.stripe_subscription'),

  # test urls
  url(r'^test_email', 'website.views.test_email'),

  url(r'^admin/', include(admin.site.urls)),

  # django static
  url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
  url(r'^robots\.txt$', TextPlainView.as_view(template_name='robots.txt')),
  url(r'^favicon\.ico$', RedirectView.as_view(url='%simages/favicon.png' % settings.STATIC_URL)),
)
