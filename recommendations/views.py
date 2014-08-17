from django.views.generic import TemplateView
from comics.views import NeedsPebbleMixin
from recommendations.models import Recommendation

class RecommendationListView(NeedsPebbleMixin, TemplateView):
    template_name="recommendations.html"

    def get_context_data(self, **kwargs):
        context = super(RecommendationListView, self).get_context_data(**kwargs)

        pebble = self.request.pebble
        likes = Recommendation.objects.filter(pebble=pebble)

        comics = likes.filter(
            kind=Recommendation.TYPE_CHOICES[0][0],
        ).order_by('-post__published')

        games = likes.filter(
            kind=Recommendation.TYPE_CHOICES[1][0],
        ).order_by('-post__published')

        context['comics'] = comics
        context['games'] = games
        context['pebble_settings'] = pebble.settings.settings

        return context