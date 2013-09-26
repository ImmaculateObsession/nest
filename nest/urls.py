import nexus

from django.conf.urls import patterns, include, url
from django.contrib import admin

from comics.views import HomeView
from comics.urls import comicpatterns, postpatterns

from comics.feeds import LatestPostFeed

admin.autodiscover()
nexus.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^comic/', include(comicpatterns)),
    url(r'^post/', include(postpatterns)),
    url(r'^feed/$', LatestPostFeed(), name='postfeed'),
    url(r'^pages/$', include('django.contrib.flatpages.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nexus/', include(nexus.site.urls)),
)
