from django.core.management.base import BaseCommand
from django.utils import timezone
from allauth.socialaccount.models import SocialToken
from facepy import GraphAPI

from comics.models import SocialPost
from comics import settings as site_settings

class Command(BaseCommand):
    help = "Posts new comics to social networks"

    def handle(self, *args, **options):
        potential_posts = SocialPost.objects.filter(
            posted=False,
            time_to_post__lte=timezone.now(),
        )
        for post in potential_posts:
            user = post.user
            if post.comic:
                url = 'http://www.captainquail.com/comic/%s/' % (post.comic.post.slug)
            elif post.post:
                url = 'http://www.captainquail.com/post/%s/' % (post.post.slug)
            if post.social_network == 'facebook':
                token = SocialToken.objects.get(
                    account__user=user,
                    app__provider='facebook'
                ).token
                graph = GraphAPI(token)
                graph.post(
                    path='%s/links' % (site_settings.facebook_page_id()),
                    link=url,
                )

