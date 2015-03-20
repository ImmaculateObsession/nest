from django.conf import settings
from django.http import (
    Http404,
    HttpResponseRedirect,
)

from pebbles.models import (
    Pebble,
    Domain,
)

class PebbleMiddleware(object):

    def process_request(self, request):
        domain = request.META.get('HTTP_HOST')
        try:
            pebble = Domain.objects.get(url=domain).pebble
        except Domain.DoesNotExist:
            pebble = None

        if not pebble:
            try:
                domain = request.META.get('HTTP_HOST').split(':')[0]
                pebble = Domain.objects.get(url=domain).pebble
            except:
                pebble = None

        # Leave this redirect out until such time as we get HTTPS again
        # if not any([pebble, request.is_secure(), settings.DEBUG, request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
        #     url = request.build_absolute_uri(request.get_full_path())
        #     secure_url = url.replace("http://", "https://")
        #     return HttpResponseRedirect(secure_url)

        request.pebble = pebble