from django.conf.urls import patterns, url, include
from django.conf import settings
from gargoyle.decorators import switch_is_active

from comics.views import (
    ComicPostView,
    ComicPreviewView,
    ComicListView,
    PostView,
    PostPreviewView,
    TaggedComicView,
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
    LiveComicView,
    TagListView,
    TagAddView,
    TagEditView,
)

from comics.api import (
    S3SignView,
    APIComicListView,
    APIComicDetailView,
    APIPanelListView,
    APIPanelDetailView,
    APITagListView,
    APITagDetailView,
)

apipatterns = patterns('',
    url(
        r'^list/$',
        APIComicListView.as_view(),
        name='apicomiclistview',
    ),
    url(
        r'^panel/list/$',
        APIPanelListView.as_view(),
        name='apipanellistview',
    ),
    url(
        r'^panel/(?P<pk>[0-9]+)/$',
        APIPanelDetailView.as_view(),
        name='apipaneldetailview',
    ),
    url(
        r'^tag/list/$',
        APITagListView.as_view(),
        name='apitaglistview',
    ),
    url(
        r'^tag(?P<pk>[0-9]+)/$',
        APITagDetailView.as_view(),
        name='apitagdetailview',
    ),
    url(
        r'^(?P<pk>[0-9]+)/$',
        APIComicDetailView.as_view(),
        name='apicomicdetailview',
    ),
)

comicpatterns = patterns('',
    url(r'^$', ComicPostView.as_view(), name='comichomeview'),
    url(r'^all/$', ComicListView.as_view(), name='comiclistview'),
    url(r'^add/$', ComicAddView.as_view(), name='comicaddview'),
    url(r'^sign_s3/',
        S3SignView.as_view(),
        name='s3signview',
    ),
    url(r'^tags/$',
        switch_is_active(settings.COMIC_TAGGING)(TagListView.as_view()),
        name='taglistview'
    ),
    url(
        r'^live/$',
        switch_is_active(settings.LIVE_COMIC_VIEW)(LiveComicView.as_view()),
        name='livecomicview',
    ),
    url(r'^api/', include(apipatterns)),
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
    url(r'^tag/(?P<id>\d+)/$',
        switch_is_active(settings.COMIC_TAGGING)(TaggedComicView.as_view()),
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

tagpatterns = patterns('',
    url(r'add/$', TagAddView.as_view(), name='tagaddview'),
    url(
        r'^(?P<id>\d+)/edit/$',
        TagEditView.as_view(),
        name='tageditview',
    ),
)
