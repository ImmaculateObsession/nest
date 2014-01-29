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
    ComicEditView,
    DeleteView,
)

from comics.api import S3SignView

comicpatterns = patterns('',
    url(r'^$', ComicPostView.as_view(), name='comichomeview'),
    url(r'^all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^add/$', ComicAddView.as_view(), name='comicaddview'),
    url(r'^backup/$', ComicBackupView.as_view(), name='comicbackupview'),
    url(r'^sign_s3/',
        S3SignView.as_view(),
        name='s3signview',
    ),
    url(r'^(?P<id>\d+)/$', ComicPostView.as_view()),
    url(
        r'^(?P<slug>[\w-]+)/$',
        ComicPostView.as_view(),
        name='comicpostview'
    ),
    url(
        r'^(?P<id>\d+)/preview/$',
        ComicPreviewView.as_view(),
        name='comicpreviewview'
    ),
    url(r'^tag/(?P<tag>[\w-]+)/$',
        TagView.as_view(),
        name='tagview',
    ),
    url(r'^(?P<id>\d+)/edit/$',
        ComicEditView.as_view(),
        name='comiceditview',
    ),
    url(r'^(?P<id>\d+)/delete/$',
        DeleteView.as_view(),
        name='comicdeleteview',
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
    