from rest_framework import serializers
from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)

from recommendations.models import Recommendation

class RecommendationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recommendation


class APIRecommendationListView(generics.ListCreateAPIView):
    authentication_classes=(SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RecommendationSerializer
    queryset = Recommendation.objects.all()

class APIRecommendationDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=(SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RecommendationSerializer
    queryset = Recommendation.objects.all()