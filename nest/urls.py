import nexus

from django.conf.urls import patterns, include, url
from django.contrib import admin

from robots_txt.views import RobotsTextView

from allauth.account.views import (
    signup,
    login,
    logout,
)

from nest.views import HomeRedirectView

from comics.views import (
    StaticPageView,
    ShareView,
    CharacterListView,
)

from comics.urls import (
    comicpatterns,
    postpatterns,
    characterpatterns,
    tagpatterns,
)
from comics.urls import apipatterns as comicapi

from comics.feeds import LatestPostFeed

from pebbles.urls import (
    pagepatterns,
    pebblepatterns,
)
from pebbles.views import (
    DashboardView,
)

from profiles.urls import profilepatterns

from reader.urls import readerpatterns

from recommendations.urls import apipatterns as likeapi
from recommendations.views import RecommendationListView

admin.autodiscover()
nexus.autodiscover()

apipatterns = patterns('',
    url(r'^comic/', include(comicapi)),
    url(r'^likes/', include(likeapi)),
)

urlpatterns = patterns('',
    url(r'^robots.txt$', RobotsTextView.as_view()),
    url(r'^$', HomeRedirectView.as_view(), name='home'),
    url(r'^likes/$', RecommendationListView.as_view(), name='like-list'),
    url(r'^api/', include(apipatterns)),
    url(r'^comic/', include(comicpatterns)),
    url(r'^post/', include(postpatterns)),
    url(r'^tag/', include(tagpatterns)),
    url(r'^feed/$', LatestPostFeed(), name='postfeed'),
    url(r'^read/', include(readerpatterns)),
    url(r'^pebbles/$', DashboardView.as_view(), name='dashview'),
    url(r'^pebble/', include(pebblepatterns)),
    url(r'^about/$', StaticPageView.as_view(), {'template': 'about.html'}),
    url(r'^profile/', include(profilepatterns)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^share/$', ShareView.as_view()),
    url(r'^characters/$', CharacterListView.as_view(), name='characterlistview'),
    url(r'^character/', include(characterpatterns)),
    url(r'^signup/$', signup),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^p/', include(pagepatterns)),
)
