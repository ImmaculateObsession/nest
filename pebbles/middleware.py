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
    whitelist = ['/admin']

    def process_request(self, request):
        domain = request.META.get('HTTP_HOST').split(':')[0]
        if any(substring in request.path for substring in self.whitelist):
            return
        try:
            pebble = Domain.objects.get(url=domain).pebble
        except Domain.DoesNotExist:
            pebble = None

        if not any([pebble, request.is_secure(), settings.DEBUG]):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)

        request.pebble = pebble