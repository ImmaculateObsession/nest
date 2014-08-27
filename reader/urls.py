from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url

from reader.views import ReaderView, ItemView


readerpatterns = patterns('',
    url(r'^$', login_required(ReaderView.as_view())),
    url(r'^(?P<pk>\d+)/$', login_required(ItemView.as_view())),
)