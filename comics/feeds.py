import logging

from mixpanel import Mixpanel

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.http import Http404
from comics.models import Post
from petroglyphs.models import Setting
from pebbles.models import Pebble, PebbleSettings

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
        log_string = "path='%s' host='%s' remote_addr='%s' user_agent='%s'" % (
            request.path,
            request.get_host(),
            request.META.get('REMOTE_ADDR'),
            request.META.get('HTTP_USER_AGENT'),
        )
        loggly_logger = logging.getLogger('loggly_logs')
        loggly_logger.info(log_string)
        self.request = request
        self.pebble = self.request.pebble
        if not self.pebble:
            raise Http404()
        self.pebble_settings = PebbleSettings.objects.get(pebble=self.pebble)
        feed = super(LatestPostFeed, self).get_feed(obj, request)
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.track('rss', 'rss_hit', {
            'pebble_id': self.request.pebble.id,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'http_host': request.META.get('HTTP_HOST'),
        })
        return feed
