from django.conf.urls import patterns, include, url
from django.contrib import admin

from comics.views import (
    HomeView,
    ComicPostView,
)

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^comic/(?P<slug>[\w-]+)/$', ComicPostView.as_view(), name='comicpostview'),

    url(r'^admin/', include(admin.site.urls)),
)
