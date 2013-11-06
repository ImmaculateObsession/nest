from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Posts new comics to social networks"

    def handle(self, *args, **options):
        pass