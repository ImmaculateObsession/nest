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
from comics.views import HomeView


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class HomeViewTests(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.comic = factories.ComicFactory.create(
            is_live=True,
            published=timezone.now(),
            creator=self.user
        )
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(reverse('comichomeview'))

    def test_home_view_response_200(self):
        HomeView.get_comic = MagicMock(return_value=self.comic)
        response = HomeView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)