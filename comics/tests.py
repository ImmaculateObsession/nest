"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone

from mock import MagicMock, patch

from comics import factories
from comics.views import (
    HomeView,
    ComicPostView,
    ComicAddView,
    CharacterAddView,
    CharacterListView,
)

from pebbles.factories import (
    PebbleFactory,
    PebbleSettingsFactory,
)

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
        comic = factories.ComicFactory(
            is_live=True,
            published=timezone.now(),
            creator=user
        )
        pebble = PebbleFactory(creator=user)
        pebble_settings = PebbleSettingsFactory(pebble=pebble)
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
        comic = factories.ComicFactory(
            is_live=True,
            published=timezone.now(),
            creator=user
        )
        pebble = PebbleFactory(creator=user)
        pebble_settings = PebbleSettingsFactory(pebble=pebble)
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


class CharacterAddTests(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        request_factory = RequestFactory()
        self.request = request_factory.get(reverse('characteraddview'))

    def test_character_add_response_200(self):
        self.request.user = self.user
        response = CharacterAddView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_character_add_render_success(self):
        self.request.user = self.user
        response = CharacterAddView.as_view()(self.request)
        response.render()

class CharacterListViewTests(TestCase):

    def setUp(self):
        pebble = PebbleFactory()
        request_factory = RequestFactory()
        self.request = request_factory.get(reverse('characterlistview'))
        self.request.pebble = pebble

    @patch('pebbles.models.PebbleSettings.objects.get')
    def test_character_list_empty_response_200(self, MagicMock):
        self.request.pebble.characters = MagicMock(return_value=[])
        response = CharacterListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    @patch('pebbles.models.PebbleSettings.objects.get')
    def test_character_list_empty_redner_success(self, MagicMock):
        self.request.pebble.characters = MagicMock(return_value=[])
        response = CharacterListView.as_view()(self.request)
        response.render()

    @patch('pebbles.models.PebbleSettings.objects.get')
    def test_character_list_with_character_response_200(self, MagicMock):
        self.request.pebble.characters = MagicMock(
            return_value=[factories.CharacterFactory()],
        )
        response = CharacterListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    @patch('pebbles.models.PebbleSettings.objects.get')
    def test_character_list_with_character_render_success(self, MagicMock):
        self.request.pebble.characters = MagicMock(
            return_value=[factories.CharacterFactory()],
        )
        response = CharacterListView.as_view()(self.request)
        response.render()
