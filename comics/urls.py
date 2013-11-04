from django.conf.urls import patterns, include, url

from comics.views import (
    HomeView,
    ComicPostView,
    ComicPreviewView,
    ComicListView,
    PostView,
    PostPreviewView,
    ComicBackupView,
    TagView,
    ComicAddView,
)

from comics.api import S3SignView

comicpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='comichomeview'),
    url(r'^all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^add/$', ComicAddView.as_view(), name='comicaddview'),
    url(r'^backup/$', ComicBackupView.as_view(), name='comicbackupview'),
    url(r'^sign_s3/',
        S3SignView.as_view(),
        name='s3signview',
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        ComicPostView.as_view(),
        name='comicpostview'
    ),
    url(
        r'^(?P<slug>[\w-]+)/preview/$',
        ComicPreviewView.as_view(),
        name='comicpreviewview'
    ),
    url(r'^tag/(?P<tag>[\w-]+)/$',
        TagView.as_view(),
        name='tagview',
    ),
)

postpatterns = patterns('',
    url(
        r'^(?P<slug>[\w-]+)/$',
        PostView.as_view(),
        name='postview'
    ),
    url(
        r'^(?P<slug>[\w-]+)/preview/$',
        PostPreviewView.as_view(),
        name='postpreviewview'
    ),
)
    