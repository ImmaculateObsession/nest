import logging
import tweepy
from django.core.management.base import BaseCommand
from django.utils import timezone
from allauth.socialaccount.models import SocialToken, SocialApp
from facepy import GraphAPI

from comics.models import SocialPost
from comics import settings as site_settings

logger = logging.getLogger('post_to_social')


class Command(BaseCommand):
    help = "Posts new comics to social networks"

    def handle(self, *args, **options):
        potential_posts = SocialPost.objects.filter(
            posted=False,
            time_to_post__lte=timezone.now(),
        )
        twitter_app_creds = SocialApp.objects.filter(provider='twitter')[0]
        twitter_key = twitter_app_creds.client_id
        twitter_secret = twitter_app_creds.secret
        for post in potential_posts:
            user = post.user
            if post.comic:
                url = 'http://www.captainquail.com/comic/%s/' % (post.comic.post.slug)
            elif post.post:
                url = 'http://www.captainquail.com/post/%s/' % (post.post.slug)
            if post.social_network == 'facebook':
                token = None
                try:
                    token = SocialToken.objects.get(
                        account__user=user,
                        app__provider='facebook'
                    ).token
                except:
                    logger.exception('Error getting social token for %s!' % (post.social_network,))
                if token:
                    try:
                        graph = GraphAPI(token)
                        graph.post(
                            path='%s/links' % (site_settings.facebook_page_id()),
                            link=url,
                        )
                    except:
                        logger.exception('Post to %s failed' % (post.social_network,))
            if post.social_network == 'twitter':
                token = None
                try:
                    token = SocialToken.objects.get(
                        account__user=user,
                        app__provider='twitter'
                    )
                except:
                    logger.exception('Error getting social token for %s!' % (post.social_network,))
                if token:
                    try:
                        auth = tweepy.OAuthHandler(twitter_key, twitter_secret)
                        auth.set_access_token(token.token, token.token_secret)
                        api = tweepy.API(auth)
                        api.update_status('Test!')
                    except:
                        logger.exception('Post to %s failed' % (post.social_network,))
            logger.info('Post to %s successful' % (post.social_network,))

