from django.http import Http404

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

        request.pebble = pebble