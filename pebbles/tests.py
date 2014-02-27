"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from django.test.client import RequestFactory

from comics import factories

from pebbles.views import (
    DashboardView,
    HomeView,
)


class DashboardTest(TestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        request_factory = RequestFactory()
        self.request = request_factory.get(reverse('dashview'))

    def test_dashboard_view_logged_in(self):
        self.request.user = self.user
        response = DashboardView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)
        response.render()

    def test_dashboard_view_render_success(self):
        self.request.user = self.user
        response = DashboardView.as_view()(self.request)
        response.render()


class HomeTests(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        request = request_factory.get(reverse('home'))
        self.response = HomeView.as_view()(request)

    def test_home_response_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_render_success(self):
        self.response.render()

