from mixpanel import Mixpanel

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Post
from petroglyphs.models import Setting
from pebbles.models import Pebble

class LatestPostFeed(Feed):
    link = "/feed/"
    description_template = "postfeed.html"

    def description(self):
        feed_description = Setting.objects.filter(key='feed_description')
        return feed_description[0] if feed_description else 'Site Feed'

    def title(self):
        feed_title = Setting.objects.filter(key='feed_title')
        return feed_title[0].value if feed_title else 'Site Feed'

    def items(self):
        return Post.published_posts.filter(pebbles=self.request.pebble).order_by('-published')[:5]

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
        feed = super(LatestPostFeed, self).get_feed(obj, request)
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.track('rss', 'rss_hit', {
            'pebble_id': self.request.pebble.id,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'none'),
            'remote_addr': request.META.get('REMOTE_ADDR', 'none'),
            'http_host': request.META.get('HTTP_HOST', 'none'),
        })
        return feed
