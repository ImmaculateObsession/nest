from django.contrib import admin

from pebbles.models import (
    Pebble,
    Domain,
)

admin.site.register(Pebble)
admin.site.register(Domain)