"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone

from mock import MagicMock

from comics import factories
from comics.views import (
    HomeView,
    ComicPostView,
)

from pebbles.factories import (
    PebbleFactory,
    PebbleSettingsFactory,
)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class HomeViewTests(TestCase):

    def setUp(self):
        user = factories.UserFactory()
        comic = factories.ComicFactory.create(
            is_live=True,
            published=timezone.now(),
            creator=user
        )
        pebble = PebbleFactory.create(creator=user)
        pebble_settings = PebbleSettingsFactory.create(pebble=pebble)
        request_factory = RequestFactory()
        request = request_factory.get(reverse('comichomeview'))
        request.pebble = pebble
        HomeView.get_comic = MagicMock(return_value=comic)
        HomeView.pebble_settings = pebble_settings.settings
        self.response = HomeView.as_view()(request)


    def test_home_view_response_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_view_render_success(self):
        self.response.render()


class ComicViewTests(TestCase):

    def setUp(self):
        user = factories.UserFactory()
        comic = factories.ComicFactory.create(
            is_live=True,
            published=timezone.now(),
            creator=user
        )
        pebble = PebbleFactory.create(creator=user)
        pebble_settings = PebbleSettingsFactory.create(pebble=pebble)
        request_factory = RequestFactory()
        request = request_factory.get(
            reverse('comicpostview', args=(comic.post.slug,))
        )
        request.pebble = pebble
        ComicPostView.get_comic = MagicMock(return_value=comic)
        ComicPostView.pebble_settings = pebble_settings.settings
        self.response = ComicPostView.as_view()(request)

    def test_comic_view_response_200(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_comic_view_render_success(self):
        self.response.render()

