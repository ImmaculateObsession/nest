from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.text import slugify

from pebbles.models import Pebble

class PublishedComicManager(models.Manager):
    def get_query_set(self):
        return super(PublishedComicManager, self).get_query_set().filter(
                is_live=True
            ).filter(
                published__lte=timezone.now
            )


class Comic(models.Model):
    title = models.CharField(max_length=140)
    image_url = models.URLField()
    image_url_large = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True) 
    published = models.DateTimeField(default=timezone.now, blank=True)
    is_live = models.BooleanField(default=False)
    transcript = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True, db_constraint=False)
    post = models.ForeignKey(
        'Post',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    characters = models.ManyToManyField(
        'Character',
        blank=True,
        null=True,
        db_constraint=False,
    )
    creator = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_constraint=False
    )
    pebbles = models.ManyToManyField(
        Pebble,
        blank=True,
        null=True,
        db_constraint=False,
    )

    objects = models.Manager()

    published_comics = PublishedComicManager()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @property
    def slug(self):
        if self.post:
            return self.post.slug
        return slugify(self.title)

    def writers(self):
        return Contributor.objects.filter(post=self.post, role=Contributor.WRITER)

    def artists(self):
        return Contributor.objects.filter(post=self.post, role=Contributor.ARTIST)

    def creators(self):
        return Contributor.objects.filter(post=self.post, role=Contributor.CREATOR)

    def get_comic_url(self):
        try:
            pebbles = self.pebbles.all()
            return "http://%s%s" % (
                pebbles[0].settings().primary_domain.url,
                reverse('comicpostview', args=(self.post.slug,)),
            )
        except ValueError:
            return None

    def is_published(self):
        if self.is_live and self.published < timezone.now():
            return True
        return False

    # def can_edit(self, user):
    #     if self.pebbles


class PublishedPostManager(models.Manager):
    def get_query_set(self):
        return super(PublishedPostManager, self).get_query_set().filter(
                is_live=True
            ).filter(
                published__lte=timezone.now
            )


class Post(models.Model):
    title = models.CharField(max_length=140)
    post = models.TextField(blank=True)
    slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(default=timezone.now)
    is_live = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True, db_constraint=False)
    creator = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    pebbles = models.ManyToManyField(
        Pebble,
        blank=True,
        null=True,
        db_constraint=False,
    )

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

    def get_post_url(self):
        pebbles = self.pebbles.all()
        if not pebbles:
            return None
        else:
            return "http://%s%s" % (
                pebbles[0].settings.primary_domain.url,
                reverse('postview', args=(self.slug,)),
            )

    def is_published(self):
        if self.is_live and self.published < timezone.now():
            return True
        return False


class Character(models.Model):
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    profile_pic_url = models.URLField(blank=True)
    pebbles = models.ManyToManyField(
        Pebble,
        blank=True,
        null=True,
        db_constraint=False,
    )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True)
    is_story = models.BooleanField(default=False)
    previous_tag = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='prev',
    )
    next_tag = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='next'
    )
    pebbles = models.ManyToManyField(
        Pebble,
        blank=True,
        null=True,
        db_constraint=False,
    )

    def get_first_comic(self):
        try:
            return Comic.published_comics.filter(
                tags__in=[self],
            ).order_by('published')[0]
        except:
            return None

    def __str__(self):
        return self.tag

    def __unicode__(self):
        return self.tag


class Contributor(models.Model):
    ARTIST = 0
    WRITER = 1
    CREATOR = 2
    ROLE_CHOICES = (
        (ARTIST, 'Artist'),
        (WRITER, 'Writer'),
        (CREATOR, 'Creator'),
    )

    post = models.ForeignKey('Post')
    contributor = models.ForeignKey(User)
    role = models.IntegerField(choices=ROLE_CHOICES)

    def __str__(self):
        return "%s:%s:%s" % (
            self.contributor,
            self.ROLE_CHOICES[self.role][1],
            self.post.title,
        )
