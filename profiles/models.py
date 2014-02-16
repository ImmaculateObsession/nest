from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse


from comics.models import (
    Comic,
    Post,
    Contributor,
)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    display_name = models.CharField(max_length=140, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s's Profile" % (self.user.username)

    def profile_url(self):
        domain = Site.objects.get_current().domain
        return "http://%s%s" % (
            domain,
            reverse('publicprofileview', args=(self.user.username,))
        )


def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)



