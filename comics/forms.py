from django import forms
from django.utils import timezone

from datetimewidget.widgets import DateTimeWidget
from suit_redactor.widgets import RedactorWidget

from comics.models import (
    Comic,
    Post,
)

date_time_options = {
    'format': 'mm/dd/yyyy hh:ii',
    'todayBtn': 'true',
    'todayHighlight': 'true',
    'minuteStep': '1',
}

class ComicForm(forms.ModelForm):
    class Meta:
        model = Comic


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

class ComicPostForm(forms.Form):
    title = forms.CharField(
        max_length=140,
        required=True, 
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    image_url = forms.URLField(
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    image_url_large = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class':'form-control',}),
    )
    alt_text = forms.CharField(
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    published = forms.DateTimeField(
        initial=timezone.now(),
        required=True,
        widget=DateTimeWidget(
            attrs={'class': 'form-control',},
            options=date_time_options,
        )
    )
    is_live = forms.BooleanField(initial=False, required=False)
    transcript = forms.CharField(
        required=False,
        widget=RedactorWidget,
    )
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    post = forms.CharField(
        required=False,
        widget=RedactorWidget,
    )
    post_to_social = forms.BooleanField(
        required=False,
        initial=False,
    )
    social_post_time = forms.DateTimeField(
        initial=timezone.now(),
        required=False,
        widget=DateTimeWidget(
            attrs={'class': 'form-control',},
            options=date_time_options,
        ),
    )
    facebook_post_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class':'form-control',}),
    )
    twitter_post_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class':'form-control',}),
    )

    def __init__(self, *args, **kwargs):
        selected_pebble = None
        if kwargs.get('selected_pebble'):
            selected_pebble = kwargs.pop('selected_pebble')
        pebbles = kwargs.pop('pebbles')
        super(ComicPostForm, self).__init__(*args, **kwargs)
        choices = [(pebble.id, pebble.title) for pebble in pebbles]
        if not selected_pebble:
            selected_pebble = choices[0][0]

        self.fields['pebble'] = forms.ChoiceField(
            choices=choices,
            initial=selected_pebble,
            widget=forms.Select(attrs={'class':'form-control',}),
        )

