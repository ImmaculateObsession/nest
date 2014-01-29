from django.conf.urls import patterns, include, url

from pebbles.views import (
    PebblePageView,
    AddPageView,
    EditPageView,
    DeleteView,
)

pagepatterns = patterns('',
    url(r'^(?P<id>\d+)/edit/$',
        EditPageView.as_view(),
        name='editpageview',
    ),
    url(r'^(?P<id>\d+)/delete/$',
        DeleteView.as_view(),
        name='deletepageview',
    ),
    url(r'^add/$', AddPageView.as_view(), name='addpageview'),
    url(r'^(?P<slug>[\w-]+)/$', PebblePageView.as_view(), name='pebblepageview'),
)