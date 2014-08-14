from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.http import Http404
from comics.models import Post
from pebbles.models import PebbleSettings

class LatestPostFeed(Feed):
    description_template = "postfeed.html"

    def link(self):
        return 'http://' + self.pebble_settings.primary_domain.url

    def feed_url(self):
        return 'http://' + self.pebble_settings.primary_domain.url + '/feed/'

    def description(self):
        return self.pebble_settings.settings.get('feed_description', 'Comic Feed')

    def title(self):
        return self.pebble_settings.settings.get('feed_title', self.pebble.title)

    def items(self):
        return Post.published_posts.filter(pebbles=self.pebble).order_by('-published')[:5]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        url = self.pebble_settings.primary_domain.url
        if item.comic:
            return 'http://' + url + reverse('comicpostview', args=[item.slug])
        return 'http://' + url + reverse('postview', args=[item.slug])

    def item_pubdate(self, item):
        return item.published

    def get_feed(self, obj, request):
        self.request = request
        self.pebble = self.request.pebble
        if not self.pebble:
            raise Http404()
        self.pebble_settings = PebbleSettings.objects.get(pebble=self.pebble)
        feed = super(LatestPostFeed, self).get_feed(obj, request)
        return feed
