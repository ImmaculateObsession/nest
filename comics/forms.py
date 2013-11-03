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
    # tags = forms.MultipleChoiceField()
    slug = forms.SlugField(
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    post = forms.CharField(
        widget=RedactorWidget,
    )