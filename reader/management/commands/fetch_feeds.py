import feedparser
import logging
from datetime import datetime
from dateutil import parser
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from reader.models import Item, Collection
from time import mktime

class Command(BaseCommand):
    help = "Fetch series in Reader db, populate items entries"

    def handle(self, *args, **kwargs):
        collections = Collection.objects.all()
        for collection in collections:
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
                item = Item.objects.get_or_create(
                    title=entry.title,
                    link=entry.link,
                    collection=collection,
                    published_on=parser.parse(entry.published),
                )[0]
                item.description = entry.description
                item.save()
            if feed_info.title and collection.title != feed_info.title:
                collection.title = feed_info.title
            if (feed_info.subtitle and
                collection.subtitle != feed_info.subtitle):
                collection.subtitle = feed_info.subtitle
            feed_updated = parser.parse(feed_info.updated)
            if collection.updated_on != feed_updated:
                collection.updated_on = feed_updated

            collection.last_checked = timezone.now()
            collection.save()
