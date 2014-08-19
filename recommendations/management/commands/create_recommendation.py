import logging
from bs4 import BeautifulSoup
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from recommendations.models import Recommendation
from comics.models import Post
from pebbles.models import PebbleSettings

class Command(BaseCommand):
    help = "Creates recommendation from new posts"

    def handle(self, *args, **options):
        logger = logging.getLogger('loggly_logs')
        logger.info('Starting recommendation create job')
        time_to_check_from = timezone.now() - timedelta(days=7)
        posts = Post.published_posts.filter(
            published__gte=time_to_check_from
        )
        for post in posts:
            soup = BeautifulSoup(post.post)
            for link in soup.find_all('a'):
                if link.attrs.get('data-rec'):
                    kind = link.attrs.get('data-rec')
                    url = link.attrs.get('href')
                    if not Recommendation.objects.filter(
                        kind=kind,
                        post=post,
                        url=url,
                    ).exists():
                        pebble = post.pebbles.all()[0]
                        rec = Recommendation.objects.create(
                            kind=int(kind),
                            post=post,
                            pebble=pebble,
                            name=link.text,
                            url=url,
                        )
                        logger.info("Recommendation created: %s" % (rec,))
                        try:
                            settings = PebbleSettings.objects.get(pebble=pebble).settings
                            settings['last_updated_recs'] = timezone.now()
                        except PebbleSettings.DoesNotExist:
                            logger.error("Pebble '%s' has no pebble settings!" % (pebble,))
                    else:
                        logger.warning("Recommendation already exists: '%s: %s'" % (kind, url))
        logger.info("Ending recommendation create job")

