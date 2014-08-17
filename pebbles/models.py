from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


class PebbleManager(models.Manager):

    def get_pebbles_for_user(self, user):
        owned_pebbles = self.filter(creator=user)
        admin_pebbles = PebbleUser.objects.filter(user=user)
        pebbles = [pebble for pebble in owned_pebbles] + [pebble.pebble for pebble in admin_pebbles]
        return pebbles


class Pebble(models.Model):
    title = models.CharField(max_length=140, unique=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    objects = PebbleManager()

    def comics(self):
        # prevent circular import. icky
        from comics.models import Comic
        return Comic.objects.filter(pebbles=self)

    def comics_by_published(self):
        return self.comics().order_by('-published')

    def pages(self):
        return PebblePage.objects.filter(pebble=self)

    def pages_by_published(self):
        return self.pages().order_by('-id')

    def characters(self):
        from comics.models import Character
        return Character.objects.filter(pebbles=self)

    def posts(self):
        from comics.models import Post
        posts = Post.objects.filter(pebbles=self)
        posts = [post for post in posts if not post.comic]
        return posts

    def tags(self):
        from comics.models import Tag
        tags = Tag.objects.filter(pebbles__in=[self])
        return tags

    def about_page(self):
        #XXX: This is a hack to display a link to the about page. Better strategy needed.
        try:
            page = PebblePage.objects.get(
                pebble=self,
                title__in=['About', 'about'],
                is_live=True,
            )
        except PebblePage.DoesNotExist:
            page = None
        return page

    def can_edit(self, user):
        if user == self.creator:
            return True
        if PebbleUser.objects.filter(pebble=self, user=user).exists():
            return True
        return False

    @property
    def settings(self):
        return PebbleSettings.objects.get(pebble=self)

    def __str__(self):
        return self.title


class Domain(models.Model):
    url = models.CharField(max_length=140, unique=True)
    pebble = models.ForeignKey('Pebble', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s: %s' % (self.url, self.pebble)


class PebbleSettings(models.Model):
    pebble = models.ForeignKey('Pebble', null=True, on_delete=models.SET_NULL)
    primary_domain = models.ForeignKey('Domain',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
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


class PebbleUser(models.Model):
    pebble = models.ForeignKey('Pebble', blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_admin = models.BooleanField(default=False)
    permissions = JSONField(blank=True)

    def __str__(self):
        return '%s: %s' % (self.user, self.pebble)
