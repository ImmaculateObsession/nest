from django.contrib import admin

from pebbles.models import (
    Pebble,
    Domain,
    PebbleSettings
)

admin.site.register(Pebble)
admin.site.register(Domain)
admin.site.register(PebbleSettings)