from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import timezone


class PublishedComicManager(models.Manager):
    def get_query_set(self):
        return super(PublishedComicManager, self).get_query_set().filter(
                is_live=True
            ).filter(
                published__lte=timezone.now()
            )


class Comic(models.Model):
    title = models.CharField(max_length=140)
    image_url = models.URLField()
    image_url_large = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True) 
    published = models.DateTimeField(default=timezone.now(), blank=True)
    is_live = models.BooleanField(default=False)
    transcript = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    post = models.ForeignKey('Post', blank=True, null=True, on_delete=models.DO_NOTHING)
    characters = models.ManyToManyField('Character', blank=True, null=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    sites = models.ManyToManyField(Site, blank=True)

    objects = models.Manager()

    published_comics = PublishedComicManager()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class PublishedPostManager(models.Manager):
    def get_query_set(self):
        return super(PublishedPostManager, self).get_query_set().filter(
                is_live=True
            ).filter(
                published__lte=timezone.now()
            )


class Post(models.Model):
    title = models.CharField(max_length=140)
    post = models.TextField(blank=True)
    slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(default=timezone.now())
    is_live = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    sites = models.ManyToManyField(Site, blank=True)

    objects = models.Manager()

    published_posts = PublishedPostManager()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @property
    def comic(self):
        try: 
            comic = Comic.objects.filter(post=self)[0]
        except IndexError:
            comic = None
        return comic


class Character(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    profile_pic_url = models.URLField(blank=True)
    sites = models.ManyToManyField(Site, blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    sites = models.ManyToManyField(Site, blank=True)

    def __str__(self):
        return self.tag

    def __unicode__(self):
        return self.tag


class ReferralCode(models.Model):
    code = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    campaign = models.CharField(max_length=140, blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.code, self.user)

    def __unicode__(self):
        return '%s - %s' % (self.code, self.user)

    @property
    def hits(self):
        return ReferralHit.objects.filter(code=self).values('ip').distinct().count()



class ReferralHit(models.Model):
    code = models.ForeignKey('ReferralCode', on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True)

    def __str__(self):
        return '%s (%s)' % (self.code, self.created)

    def __unicode__(self):
        return '%s (%s)' % (self.code, self.created)
