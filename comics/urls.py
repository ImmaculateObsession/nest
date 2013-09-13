from django.conf.urls import patterns, include, url

from comics.views import (
    ComicPostView,
    ComicListView,
    PostView,
)

comicpatterns = patterns('',
    url(r'^all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^(?P<slug>[\w-]+)/$', ComicPostView.as_view(), name='comicpostview'),
)

postpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', PostView.as_view(), name='postview'),
    )