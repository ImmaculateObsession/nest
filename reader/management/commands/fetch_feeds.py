import feedparser
import logging
from dateutil import parser
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from reader.models import Item, Collection

class Command(BaseCommand):
    help = "Fetch series in Reader db, populate items entries"

    def handle(self, *args, **kwargs):
        logger = logging.getLogger('loggly_logs')
        logger.info('Starting feed fetch job')
        collections = Collection.objects.all()
        for collection in collections:
            logger.info('Starting collection update: %s' % (collection))
            user_agent = settings.FEED_FETCHER_USER_AGENT % (
                collection.id,
                collection.readers,
            )
            feed = feedparser.parse(
                collection.feed_url,
                agent=user_agent,
            )
            feed_info = feed.feed
            for entry in feed.entries:
                result = Item.objects.get_or_create(
                    title=entry.title,
                    link=entry.link,
                    collection=collection,
                    published_on=parser.parse(entry.published),
                )
                item = result[0]
                item.description = entry.description
                item.save()
                if result[1]:
                    logger.info('Created item: %s' % (item))
            if feed_info.get('title') and collection.title != feed_info.title:
                collection.title = feed_info.title
            if (feed_info.get('subtitle') and
                collection.subtitle != feed_info.subtitle):
                collection.subtitle = feed_info.subtitle
            if feed_info.get('updated'):
                feed_updated = parser.parse(feed_info.updated)
                if collection.updated_on != feed_updated:
                    collection.updated_on = feed_updated

            collection.last_checked = timezone.now()
            collection.save()
            logger.info('Finished collection update: %s' % (collection))
        logger.info('Finished feed fetch job')
