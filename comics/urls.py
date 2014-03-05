from django.conf.urls import patterns, url

from comics.views import (
    ComicPostView,
    ComicPreviewView,
    ComicListView,
    PostView,
    PostPreviewView,
    TagView,
    ComicAddView,
    ComicEditView,
    ComicDeleteView,
    CharacterAddView,
    CharacterEditView,
    CharacterView,
    CharacterDeleteView,
    PostEditView,
    PostAddView,
    PostDeleteView,
)

from comics.api import S3SignView

comicpatterns = patterns('',
    url(r'^$', ComicPostView.as_view(), name='comichomeview'),
    url(r'^all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^add/$', ComicAddView.as_view(), name='comicaddview'),
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
        ComicDeleteView.as_view(),
        name='comicdeleteview',
    ),
)

postpatterns = patterns('',
    url(r'^add/$', PostAddView.as_view(), name='postaddview'),
    url(
        r'^(?P<slug>[\w-]+)/$',
        PostView.as_view(),
        name='postview'
    ),
    url(
        r'^(?P<id>\d+)/preview/$',
        PostPreviewView.as_view(),
        name='postpreviewview'
    ),
    url(
        r'^(?P<id>\d+)/edit/$',
        PostEditView.as_view(),
        name="posteditview",
    ),
    url(
        r'^(?P<id>\d+)/delete/$',
        PostDeleteView.as_view(),
        name="postdeleteview",
    ),
)

characterpatterns = patterns('',
    url(r'^add/$', CharacterAddView.as_view(), name='characteraddview'),
    url(
        r'^(?P<id>\d+)/edit/$',
        CharacterEditView.as_view(),
        name='charactereditview',
    ),
    url(
        r'^(?P<id>\d+)/delete/$',
        CharacterDeleteView.as_view(),
        name='characterdeleteview',
    ),
    url(r'^(?P<id>\d+)/$', CharacterView.as_view(), name="characterview"),
)
