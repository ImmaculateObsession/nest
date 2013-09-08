from django.contrib import admin
from comics.models import (
    Comic,
    Post,
    Character,
    Tag,
)

admin.site.register(Comic)
admin.site.register(Post)
admin.site.register(Character)
admin.site.register(Tag)