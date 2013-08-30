from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from comics.models import (
    Post,
    Comic,
)

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        comic = Comic.objects.latest('published')
        context['comic'] = comic
        if comic.post:
            context['post'] = comic.post
        else:
            try:
                context['post'] = Post.objects.latest('published')
            except Post.DoesNotExist:
                pass

        context['first_comic'] = Comic.objects.filter(published__lt=comic.published).order_by('published')[0]
        return context

class ComicPostView(TemplateView):
    template_name = "comic.html"

    def get_context_data(self, **kwargs):
        context = super(ComicView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        comic = Comic.objects.get(post=post)

        context['post'] = post
        context['comic'] = comic

        context['first_comic'] = Comic.objects.filter(published__lt=comic.published).order_by('published')[0]
        context['last_comic'] = Comic.objects.latest('published')
        context['previous'] = Comic.objects.filter(published__lt=comic.published).order_by('-published')[0]
        context['next'] = Comic.objects.filter(published__gt=comic.published).order_by('published')[0]

        return context

class ComicDetailView(TemplateView):
    pass