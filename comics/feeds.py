from mixpanel import Mixpanel

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Post
from petroglyphs.models import Setting
from pebbles.models import Pebble

mp = Mixpanel(settings.MIXPANEL_KEY)
mp_id_set = Setting.objects.filter(key='mixpanel_id')

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
        return Post.published_posts.filter(pebbles=Pebble.objects.get(id=1)).order_by('-published')[:5]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        if item.comic:
            return reverse('comicpostview', args=[item.slug])
        return reverse('postview', args=[item.slug])

    def item_pubdate(self, item):
        return item.published

    def get_feed(self, obj, request):
        feed = super(LatestPostFeed, self).get_feed(obj, request)
        if mp_id_set:
            mp.track(mp_id_set[0], 'rss_hit', {
                'user_agent': request.META.get('HTTP_USER_AGENT', 'none'),
                'remote_addr': request.META.get('REMOTE_ADDR', 'none'),
                'http_host': request.META.get('HTTP_HOST', 'none'),
                })
        return feed
