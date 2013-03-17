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
                       url(r'^signup', 'website.views.signup'),
                       url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),

                       url(r'^add_project', 'website.views.add_project', name='add_project'),
                       url(r'^project/(?P<oid>\d+)/add_opportunity', 'website.views.add_opportunity',
                           name='add_opportunity'),
                       url(r'^test_project', 'website.views.test_project', name='test_project'),
                       url(r'^project/(.*?)$', 'website.views.view_project', name='view_project'),
                       url(r'^opportunity/(.*?)$', 'website.views.view_opportunity', name='view_opportunity'),
                       url(r'^ajax/follow_project', 'website.ajaxviews.follow_project', name='follow_project'),
                       url(r'^login', 'website.views.login_user', name='login_user'),

                       url(r'^private$', 'website.views.private', name='private'),
                       # url(r'^test$', 'website.views.test', name='test'),

                       # url("^index", TemplateView.as_view(template_name='index.html'), name="mission"),

                       # Admin site
                       #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),

                       # Server Static Files from Django
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)
