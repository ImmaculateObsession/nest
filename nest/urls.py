# import nexus

from django.conf.urls import patterns, include, url
from django.contrib import admin

from nest.views import HomeRedirectView

from comics.views import (
    HomeView,
    ProfileView,
    CreateRefCodeView,
    PlaygroundView,
    StaticPageView,
    ShareView,
)

from comics.urls import comicpatterns, postpatterns

from comics.feeds import LatestPostFeed

from pebbles.views import DashboardView

admin.autodiscover()
# nexus.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeRedirectView.as_view(), name='home'),
    url(r'^comic/', include(comicpatterns)),
    url(r'^post/', include(postpatterns)),
    url(r'^feed/$', LatestPostFeed(), name='postfeed'),
    url(r'^pebbles/$', DashboardView.as_view(), name='dashview'),
    url(r'^about/$', StaticPageView.as_view(), {'template': 'about.html'}),
    # url(r'^refcode/$', CreateRefCodeView.as_view()),
     url(r'^profile/', ProfileView.as_view()),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^nexus/', include(nexus.site.urls)),
    url(r'^playground/$', PlaygroundView.as_view()),
    url(r'^share/$', ShareView.as_view()),
)
