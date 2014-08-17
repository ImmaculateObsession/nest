from django.conf.urls import patterns, url

from recommendations.api import (
    APIRecommendationListView,
    APIRecommendationDetailView,
)

apipatterns = patterns('',
    url(
        r'^list/$',
        APIRecommendationListView.as_view(),
        name='api-like-list-view',
    ),
    url(
        r'^(?P<pk>[0-9]+)/$',
        APIRecommendationDetailView.as_view(),
        name='api-like-detail-view',
    ),
)