from django.contrib import admin
from comics.models import (
    Comic,
    Post,
    Character,
)

admin.site.register(Comic)
admin.site.register(Post)
admin.site.register(Character)