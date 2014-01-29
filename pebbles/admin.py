from django.contrib import admin
from django.forms import ModelForm
from suit_redactor.widgets import RedactorWidget

from pebbles.models import (
    Pebble,
    Domain,
    PebbleSettings,
    PebblePage,
)


class PebblePageForm(ModelForm):

    class Meta:
        widgets = {
            'content': RedactorWidget(editor_options={'lang': 'en'})
        }


class PebblePageAdmin(admin.ModelAdmin):

    form = PebblePageForm


admin.site.register(Pebble)
admin.site.register(Domain)
admin.site.register(PebbleSettings)
admin.site.register(PebblePage, PebblePageAdmin)