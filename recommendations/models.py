from django.db import models
from comics.models import Post
from pebbles.models import Pebble

class Recommendation(models.Model):
    COMIC = 0
    VIDEO_GAME = 1
    TYPE_CHOICES = (
        (COMIC, 'Comic'),
        (VIDEO_GAME, 'Video Game'),
    )

    name = models.CharField(max_length=140)
    url = models.URLField()
    kind = models.IntegerField(choices=TYPE_CHOICES)
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    pebble = models.ForeignKey(
        Pebble,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s: %s" % (
            self.TYPE_CHOICES[self.kind][1],
            self.name,
        )