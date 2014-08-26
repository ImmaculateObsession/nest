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

    def __str__(self):
        return "%s: %s" % (self.collection, self.title)

class Collection(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    feed_url = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    readers = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s (updated:%s/checked:%s)" % (
            self.title,
            self.updated_on.strftime("%Y-%m-%d,%H:%M%Z"),
            self.last_checked.strftime("%Y-%m-%d,%H:%M%Z"),
        )

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

    def __str__(self):
        return "%s reading %s" % (self.user, self.collection)

