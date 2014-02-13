from django.conf.urls import patterns, include, url

from profiles.views import ProfileView

profilepatterns = patterns('',
    url(r'^$', ProfileView.as_view(), name='profileview'),
)