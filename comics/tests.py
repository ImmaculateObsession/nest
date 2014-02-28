"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from django import shortcuts

from mock import MagicMock

from comics import factories
from comics.views import (
    HomeView,
    ComicPostView,
    ComicAddView,
    ComicEditView,
)
from comics.models import Comic

from pebbles.factories import (
    PebbleFactory,
    PebbleSettingsFactory,
)
from pebbles.models import Pebble

from petroglyphs.models import Setting


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


class ComicAddTests(TestCase):

    def setUp(self):
        site_url = Setting.objects.create(
            key='site_url',
            value='http://www.inkpebble.com',
        )
        self.user = factories.UserFactory()
        request_factory = RequestFactory()
        self.request = request_factory.get(reverse('comicaddview'))
        self.request.META['HTTP_HOST'] = site_url.value

    def test_comic_add_response_200(self):
        self.request.user = self.user
        response = ComicAddView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_comic_add_render_success(self):
        self.request.user = self.user
        response = ComicAddView.as_view()(self.request)
        response.render()


class ComicEditTests(TestCase):
    """
    I will finish this test someday, but I'm hitting lower-hanging 
    fruit for now

    def setUp(self):
        site_url = Setting.objects.create(
            key='site_url',
            value='http://www.inkpebble.com',
        )
        self.user = factories.UserFactory()
        self.pebble = PebbleFactory.create(creator=self.user)
        self.comic = factories.ComicFactory.create(
            is_live=True,
            published=timezone.now(),
            creator=self.user,
            id=1,
        )
        # self.comic.pebbles.add(pebble)
        request_factory = RequestFactory()
        self.request = request_factory.get(
            reverse('comiceditview', kwargs={'id':self.comic.id}),
        )
        self.request.META['HTTP_HOST'] = site_url.value

    def test_comic_edit_response_200(self):
        shortcuts.get_object_or_404 = MagicMock(return_value=self.comic)
        self.comic.pebbles = MagicMock(return_value=[self.pebble])
        self.request.user = self.user
        response = ComicEditView.as_view()(self.request, id=self.comic.id)
        self.assertEqual(response.status_code, 200)
    """
    pass

