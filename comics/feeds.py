from mixpanel import Mixpanel
import keen

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Post

mp = Mixpanel(settings.MIXPANEL_KEY)


class LatestPostFeed(Feed):
    link = "/feed/"
    description = "The Quail Comics Feed"
    description_template = "postfeed.html"

    def title(self):
        return "The Adventures of Captain Quail"

    def items(self):
        return Post.published_posts.order_by('-published')[:5]

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
        mp.track('quailcomics', 'rss_hit', {
            'user_agent': request.META.get('HTTP_USER_AGENT', 'none'),
            'remote_addr': request.META.get('REMOTE_ADDR', 'none'),
            'http_host': request.META.get('HTTP_HOST', 'none'),
            })
        return feed
