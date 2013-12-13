from django.views.generic import View
from comics.views import HomeView


class HomeRedirectView(View):

    def dispatch(self, request, *args, **kwargs):

        if request.pebble:
            return HomeView.as_view()(request)