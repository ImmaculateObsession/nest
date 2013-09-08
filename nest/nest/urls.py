from django.conf.urls import patterns, include, url
from django.contrib import admin

from comics.views import (
    HomeView,
    ComicPostView,
    ComicListView,
)

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^comic/$', HomeView.as_view(), name='comic'),
    url(r'^comic/all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^comic/(?P<slug>[\w-]+)/$', ComicPostView.as_view(), name='comicpostview'),
    
    url(r'^admin/', include(admin.site.urls)),
)
