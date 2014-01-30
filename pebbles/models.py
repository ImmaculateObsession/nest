from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


class Pebble(models.Model):
    title = models.CharField(max_length=140, unique=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def comics(self):
        # prevent circular import. icky
        from comics.models import Comic
        return Comic.objects.filter(pebbles=self)

    def comics_by_published(self):
        return self.comics().order_by('-id')

    def pages(self):
        return PebblePage.objects.filter(pebble=self)

    def pages_by_published(self):
        return self.pages().order_by('-id')

    def __str__(self):
        return self.title


class Domain(models.Model):
    url = models.CharField(max_length=140, unique=True)
    pebble = models.ForeignKey('Pebble', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s: %s' % (self.url, self.pebble)


class PebbleSettings(models.Model):
    pebble = models.ForeignKey('Pebble', null=True, on_delete=models.SET_NULL)
    settings = JSONField()

    def __str__(self):
        return '"%s" Settings' % (self.pebble.title)

class PebblePage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=140)
    slug = models.SlugField(blank=True)
    is_live = models.BooleanField(default=False)
    standalone = models.BooleanField(default=False)
    content = models.TextField(blank=True)
    pebble = models.ForeignKey('Pebble', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%s (%s)" % (self.title, self.pebble)
