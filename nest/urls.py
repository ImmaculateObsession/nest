# import nexus

from django.conf.urls import patterns, include, url
from django.contrib import admin

from nest.views import HomeRedirectView

from comics.views import (
    HomeView,
    StaticPageView,
    ShareView,
    CharacterListView,
)

from comics.urls import (
    comicpatterns,
    postpatterns,
    characterpatterns,
)

from comics.feeds import LatestPostFeed

from pebbles.urls import (
    pagepatterns,
    pebblepatterns,
)
from pebbles.views import (
    DashboardView,
)

from profiles.urls import profilepatterns

admin.autodiscover()
# nexus.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeRedirectView.as_view(), name='home'),
    url(r'^comic/', include(comicpatterns)),
    url(r'^post/', include(postpatterns)),
    url(r'^feed/$', LatestPostFeed(), name='postfeed'),
    url(r'^pebbles/$', DashboardView.as_view(), name='dashview'),
    url(r'^pebble/', include(pebblepatterns)),
    url(r'^about/$', StaticPageView.as_view(), {'template': 'about.html'}),
    url(r'^profile/', include(profilepatterns)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^nexus/', include(nexus.site.urls)),
    url(r'^share/$', ShareView.as_view()),
    url(r'^characters/$', CharacterListView.as_view(), name='characterlistview'),
    url(r'^character/', include(characterpatterns)),
    url(r'^p/', include(pagepatterns)),
)
