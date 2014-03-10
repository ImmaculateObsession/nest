from django import forms
from django.utils import timezone
from django.utils.text import slugify


from datetimewidget.widgets import DateTimeWidget
from suit_redactor.widgets import RedactorWidget

from comics.models import (
    Comic,
    Post,
)

from pebbles.models import Pebble

date_time_options = {
    'format': 'mm/dd/yyyy hh:ii:ss',
    'todayBtn': 'true',
    'todayHighlight': 'true',
    'minuteStep': '1',
}

class NeedsPebbleForm(forms.Form):

    def __init__(self, *args, **kwargs):
        selected_pebble = None
        if kwargs.get('selected_pebble'):
            selected_pebble = kwargs.pop('selected_pebble')
        self.pebbles = kwargs.pop('pebbles')
        super(NeedsPebbleForm, self).__init__(*args, **kwargs)
        choices = [(pebble.id, pebble.title) for pebble in self.pebbles]
        if choices and not selected_pebble:
            selected_pebble = choices[0][0]

        self.fields['pebble'] = forms.ChoiceField(
            choices=choices,
            initial=selected_pebble,
            widget=forms.Select(attrs={'class':'form-control',}),
        )


class HasTagsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        selected_tags = None
        if kwargs.get('selected_tags'):
            selected_tags = [tag.id for tag in kwargs.pop('selected_tags')]
        self.tags = kwargs.pop('tags')
        super(HasTagsForm, self).__init__(*args, **kwargs)
        choices = [(tag.id, tag.tag) for tag in self.tags]

        self.fields['tags'] = forms.MultipleChoiceField(
            required=False,
            choices=choices,
            initial=selected_tags,
            widget=forms.SelectMultiple(attrs={'class':'form-control',}),
        )


class ComicForm(forms.ModelForm):
    class Meta:
        model = Comic


class PostForm(NeedsPebbleForm):
    title = forms.CharField(
        max_length=140,
        required=True, 
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    published = forms.DateTimeField(
        initial=timezone.now,
        required=True,
        widget=DateTimeWidget(
            attrs={'class': 'form-control',},
            options=date_time_options,
        )
    )
    is_live = forms.BooleanField(initial=False, required=False)
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    post = forms.CharField(
        required=False,
        widget=RedactorWidget,
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
        if slug != self.initial.get('slug') and Post.objects.filter(pebbles=pebble, slug=slug).exists():
            raise forms.ValidationError("Slug matches an existing post")

        return cleaned_data


class ComicPostForm(NeedsPebbleForm, HasTagsForm):
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
        initial=timezone.now,
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
        initial=timezone.now,
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

class ComicDeleteForm(forms.Form):
    really_delete = forms.ChoiceField(
        widget=forms.RadioSelect,
        required=True,
        choices=[('yes', 'yes'), ('no', 'no')],
    )


class CharacterForm(NeedsPebbleForm):
    name = forms.CharField(
        max_length=140,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control',})
    )
    description = forms.CharField(
        required=False,
        widget=RedactorWidget,
    )
    profile_pic_url = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )


class TagForm(NeedsPebbleForm):
    tag = forms.CharField(
        max_length=140,
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )
    description = forms.CharField(
        required=False,
        widget=RedactorWidget,
    )
    header_image = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control',}),
    )

