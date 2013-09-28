from django.contrib import admin
from comics.models import (
    Comic,
    Post,
    Character,
    Tag,
    ReferralCode,
    ReferralHit,
)


class ComicAdmin(admin.ModelAdmin):

    def queryset(self, request):
        return Comic.objects.all()


class PostAdmin(admin.ModelAdmin):

    def queryset(self, request):
        return Post.objects.all()

admin.site.register(Comic, ComicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Character)
admin.site.register(Tag)
admin.site.register(ReferralCode)
admin.site.register(ReferralHit)