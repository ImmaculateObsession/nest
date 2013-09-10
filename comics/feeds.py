from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Comic

class LatestComicPostFeed(Feed):
    title = "Quail Comics"
    link = "/feed/"
    description = "The Quail Comics Feed"
    description_template = "comicpostfeed.html"

    def items(self):
        return Comic.published_comics.order_by('-published')[:5]

    def item_title(self, item):
        return item.title

    def description(self, item):
        return item

    def item_link(self, item):
        return reverse('comicpostview', args=[item.post.slug])

    def item_pubdate(self, item):
        return item.published
