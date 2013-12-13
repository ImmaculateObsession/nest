from django.db import models
from django.contrib.auth.models import User


class Pebble(models.Model):
    title = models.CharField(max_length=140, unique=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Domain(models.Model):
    url = models.CharField(max_length=140, unique=True)
    pebble = models.ForeignKey('Pebble')

    def __str__(self):
        return '%s: %s' % (self.url, self.pebble)
