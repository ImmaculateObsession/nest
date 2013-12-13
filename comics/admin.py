from django.contrib import admin
from django.forms import ModelForm
import reversion
from suit_redactor.widgets import RedactorWidget
from comics.models import (
    Comic,
    Post,
    Character,
    Tag,
)

class PostForm(ModelForm):

    class Meta:
        widgets = {
            'post': RedactorWidget(editor_options={'lang': 'en'})
        }


class ComicAdmin(reversion.VersionAdmin):

    def queryset(self, request):
        return Comic.objects.all()


class PostAdmin(reversion.VersionAdmin):

    form = PostForm

    def queryset(self, request):
        return Post.objects.all()

admin.site.register(Comic, ComicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Character)
admin.site.register(Tag)
