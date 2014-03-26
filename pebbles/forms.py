from django import forms
from django.utils.text import slugify


from suit_redactor.widgets import RedactorWidget

from pebbles.models import (
    Pebble,
    PebblePage,
)

class PebblePageForm(forms.Form):
    title = forms.CharField(
        max_length=140,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    is_live = forms.BooleanField(initial=False, required=False)
    standalone = forms.BooleanField(initial=False, required=False)
    content = forms.CharField(
        required=False,
        widget=RedactorWidget,
    )

    def __init__(self, *args, **kwargs):
        selected_pebble = None
        if kwargs.get('selected_pebble'):
            selected_pebble = kwargs.pop('selected_pebble')
        self.pebbles = kwargs.pop('pebbles')
        super(PebblePageForm, self).__init__(*args, **kwargs)
        choices = [(pebble.id, pebble.title) for pebble in self.pebbles]
        if choices and not selected_pebble:
            selected_pebble = choices[0][0]

        self.fields['pebble'] = forms.ChoiceField(
            choices=choices,
            initial=selected_pebble,
            widget=forms.Select(attrs={'class':'form-control',}),
        )

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug or slug == '':
            slug = slugify(self.cleaned_data['title'])

        return slug

    def clean(self):
        cleaned_data = self.cleaned_data
        slug = cleaned_data.get('slug')
        pebble = Pebble.objects.get(id=cleaned_data.get('pebble'))
        if slug != self.initial.get('slug') and PebblePage.objects.filter(pebble=pebble, slug=slug).exists():
            raise forms.ValidationError("Slug matches an existing page")

        return cleaned_data


class PebbleSettingsForm(forms.Form):
    site_title = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    facebook_page = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    twitter_page = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    youtube_channel = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    tagline = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    show_rss = forms.BooleanField()
    copyright = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    feed_description = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    feed_title = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    



