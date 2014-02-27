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

from pebbles.views import DashboardView


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

