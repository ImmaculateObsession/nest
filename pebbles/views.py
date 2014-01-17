from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from petroglyphs.models import Setting

from comics.models import Comic

from pebbles.models import (
    Pebble,
    Domain,
    PebbleSettings,
)


class HomeView(TemplateView):
    template_name = 'main_home.html'


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        pebbles = Pebble.objects.filter(creator=self.request.user)

        comic_dict = {}
        for pebble in pebbles:
            comic_dict[str(pebble.id)] = Comic.objects.filter(pebbles=pebble)

        context['pebbles'] = pebbles

        context['comics'] = comic_dict

        return context

