from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PublishedComicManager(models.Manager):
    def get_query_set(self):
        return super(PublishedComicManager, self).get_query_set().filter(is_live=True)


class ComicManager(models.Manager):
    pass


class Comic(models.Model):
    title = models.CharField(max_length=140)
    image_url = models.URLField()
    image_url_large = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True) 
    published = models.DateTimeField(default=timezone.now(), blank=True)
    is_live = models.BooleanField(default=False)
    transcript = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    post = models.ForeignKey('Post', blank=True, null=True)
    characters = models.ManyToManyField('Character', blank=True, null=True)
    creator = models.ForeignKey(User, blank=True, null=True)

    published_comics = PublishedComicManager()
    objects = ComicManager()

    def __str__(self):
        return self.title


class PublishedPostManager(models.Manager):
    def get_query_set(self):
        return super(PublishedPostManager, self).get_query_set().filter(is_live=True)


class PostManager(models.Manager):
    pass


class Post(models.Model):
    title = models.CharField(max_length=140)
    post = models.TextField(blank=True)
    slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(default=timezone.now())
    is_live = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)
    creator = models.ForeignKey(User, blank=True, null=True)

    published_posts = PublishedPostManager()

    objects = PostManager()

    def __str__(self):
        return self.title


class Character(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    profile_pic_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=140)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.tag