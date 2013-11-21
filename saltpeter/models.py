from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SocialPost(models.Model):
    FACEBOOK = 'facebook'
    TWITTER = 'twitter'
    REDDIT = 'reddit'
    TUMBLR = 'tumblr'
    SOCIAL_NETWORK_CHOICES = (
        (FACEBOOK, FACEBOOK),
        (TWITTER, TWITTER),
    )

    user = models.ForeignKey(User)
    url = models.URLField(blank=True)
    time_to_post = models.DateTimeField(default=timezone.now())
    is_posted = models.BooleanField(default=False)
    posted_on = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    social_network = models.CharField(
        max_length='20',
        choices=SOCIAL_NETWORK_CHOICES,
        default=FACEBOOK,
    )

    def __str__(self):
        if self.is_posted:
            return 'POSTED to %s on %s' % (
                self.social_network,
                self.posted_on
            )
        return '%s on %s' % (self.social_network, self.time_to_post)