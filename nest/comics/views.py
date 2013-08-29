from django.views.generic import TemplateView

from comics.models import (
    Post,
    Comic,
)

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        comic = Comic.objects.latest('published')
        context['comic'] = comic
        if comic.post:
            context['post'] = comic.post
        else:
            try:
                context['post'] = Post.objects.latest('published')
            except Post.DoesNotExist:
                pass
        return context