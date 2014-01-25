from mixpanel import Mixpanel

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Post
from petroglyphs.models import Setting
from pebbles.models import Pebble, PebbleSettings

class LatestPostFeed(Feed):
    link = "/feed/"
    description_template = "postfeed.html"

    def description(self):
        return self.pebble_settings.get('feed_description')

    def title(self):
        return self.pebble_settings.get('feed_title')

    def items(self):
        return Post.published_posts.filter(pebbles=self.pebble).order_by('-published')[:5]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        if item.comic:
            return reverse('comicpostview', args=[item.slug])
        return reverse('postview', args=[item.slug])

    def item_pubdate(self, item):
        return item.published

    def get_feed(self, obj, request):
        self.request = request
        self.pebble = self.request.pebble
        self.pebble_settings = PebbleSettings.objects.get(pebble=self.pebble).settings
        feed = super(LatestPostFeed, self).get_feed(obj, request)
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.track('rss', 'rss_hit', {
            'pebble_id': self.request.pebble.id,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'none'),
            'remote_addr': request.META.get('REMOTE_ADDR', 'none'),
            'http_host': request.META.get('HTTP_HOST', 'none'),
        })
        return feed
