from django.views.generic import View
from comics.views import HomeView
from pebbles.views import HomeView as MainHomeView


class HomeRedirectView(View):

    def dispatch(self, request, *args, **kwargs):

        if request.pebble:
            return HomeView.as_view()(request)
        else:
            return MainHomeView.as_view()(request)