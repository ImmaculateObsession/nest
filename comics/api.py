import time
import json
import base64
import hmac
import sha
import urllib

from rest_framework.response import Response
from rest_framework.views import APIView

from petroglyphs.models import Setting


class S3SignView(APIView):

    def get(self, request, format=None):
        AWS_ACCESS_KEY = str(Setting.objects.get(key='aws_access_key').value)
        AWS_SECRET_KEY = str(Setting.objects.get(key='aws_secret_key').value)
        S3_BUCKET = str(Setting.objects.get(key='s3_bucket').value)

        object_name = request.QUERY_PARAMS.get('s3_object_name')
        mime_type = request.QUERY_PARAMS.get('s3_object_type')

        expires = int(time.time()+10)
        amz_headers = 'x-amz-acl:public-read'

        put_request = 'PUT\n\n%s\n%d\n%s\n/%s/%s' % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

        signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha).digest())
        signature = urllib.quote_plus(signature.strip())
        url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

        data = {
            'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
            'url': url,
        }
        # import pdb; pdb.set_trace()
        return Response(data)