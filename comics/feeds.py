from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from comics.models import Post

class LatestPostFeed(Feed):
    title = "Quail Comics"
    link = "/feed/"
    description = "The Quail Comics Feed"
    description_template = "postfeed.html"

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
