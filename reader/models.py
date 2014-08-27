from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    title = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField()
    number_in_series = models.SmallIntegerField(
        blank=True,
        null=True,
    )
    published_on = models.DateTimeField(
        blank=True,
        null=True,
    )
    collection = models.ForeignKey('Collection')
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s: %s" % (self.collection, self.title)

    def get_siblings(self):
        try:
            older_siblings = Item.objects.filter(
                collection=self.collection,
                published_on__lt=self.published_on,
            ).order_by('-published_on')
            older = older_siblings[0]

        except IndexError:
            older = None

        try:
            younger_siblings = Item.objects.filter(
                collection=self.collection,
                published_on__gt=self.published_on,
            ).order_by('published_on')
            younger = younger_siblings[0]

        except IndexError:
            younger = None

        return (older, younger)

class Collection(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    feed_url = models.URLField()
    feed_title = models.CharField(blank=True,null=True,max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    readers = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % (self.title,)

class Reader(models.Model):
    reader = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
    )
    collection = models.ForeignKey('Collection')
    last_read = models.ForeignKey(
        'Item',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s reading %s" % (self.reader, self.collection)

    def get_last_read(self):
        if self.last_read:
            return self.last_read
        else:
            try:
                return Item.objects.filter(
                    collection=self.collection
                ).order_by('published_on')[0]
            except IndexError:
                return None


