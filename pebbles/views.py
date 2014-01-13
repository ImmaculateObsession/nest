from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect

from django.views.generic import TemplateView
from petroglyphs.models import Setting


class HomeView(TemplateView):
    template_name = 'main_home.html'
