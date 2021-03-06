import time
import base64
import hmac
import sha
import urllib
import hashlib

from django.utils import timezone

from comics.serializers import (
    ComicSerializer,
    PanelSerializer,
    TagSerializer,
)
from comics.models import Comic, Panel, Tag

from rest_framework import generics

from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from petroglyphs.models import Setting


class S3SignView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        AWS_ACCESS_KEY = str(Setting.objects.get(key='aws_access_key').value)
        AWS_SECRET_KEY = str(Setting.objects.get(key='aws_secret_key').value)
        S3_BUCKET = str(Setting.objects.get(key='s3_bucket').value)


        object_name = request.QUERY_PARAMS.get('s3_object_name')
        mime_type = request.QUERY_PARAMS.get('s3_object_type')

        hashcode = hashlib.sha1(
            str(object_name) + str(timezone.now())
        ).hexdigest()[:6]

        folder_name = request.user.username

        resource_name = "comics/%s/%s_%s" % (folder_name, hashcode, object_name)

        expires = int(time.time()+10)
        amz_headers = 'x-amz-acl:public-read'

        put_request = 'PUT\n\n%s\n%d\n%s\n/%s/%s' % (mime_type, expires, amz_headers, S3_BUCKET, resource_name)

        signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha).digest())
        signature = urllib.quote_plus(signature.strip())
        url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, resource_name)

        data = {
            'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
            'url': url,
        }
        return Response(data)

class APIComicListView(generics.ListCreateAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComicSerializer

    def get_queryset(self):

        if not self.request.user.is_anonymous():
            return Comic.objects.get_comics_for_user(self.request.user).order_by('published')
        if self.request.pebble:
            return self.request.pebble.comics_by_published()
        else:
            return Comic.published_comics.all()

class APIComicDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComicSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous():
            return Comic.objects.get_comics_for_user(self.request.user).order_by('published')
        return Comic.published_comics.all()


class APIPanelListView(generics.ListCreateAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PanelSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous():
            return Panel.objects.get_panels_for_user(self.request.user)
        return Panel.published_panels.all()

class APIPanelDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PanelSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous():
            return Panel.objects.get_panels_for_user(self.request.user)
        return Panel.published_panels.all()


class APITagListView(generics.ListCreateAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous():
            return Tag.objects.get_tags_for_user(self.request.user)
        return Tag.objects.all()


class APITagDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous():
            return Tag.objects.get_tags_for_user(self.request.user)
        return Tag.objects.all()
