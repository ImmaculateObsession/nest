from django.shortcuts import get_object_or_404
from django.views.generic import (
    TemplateView,
    ListView,
)

from comics.models import (
    Post,
    Comic,
)

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        comic = Comic.published_comics.latest('published')
        context['comic'] = comic
        if comic.post:
            context['post'] = comic.post
            context['disqus_indentifier'] = comic.post.slug
        else:
            context['disqus_indentifier'] = comic.title
        try:
            context['first_comic'] = Comic.published_comics.filter(published__lt=comic.published).order_by('published')[0]
            context['previous'] = Comic.published_comics.filter(published__lt=comic.published).order_by('-published')[0]
        except IndexError:
            pass

        return context

class ComicPostView(TemplateView):
    template_name = "comicpostview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPostView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'], is_live=True)
        comic = Comic.published_comics.get(post=post)

        context['post'] = post
        context['comic'] = comic
        context['disqus_indentifier'] = post.slug

        try: 
            context['first_comic'] = Comic.published_comics.filter(published__lt=comic.published).order_by('published')[0]
            context['previous'] = Comic.published_comics.filter(published__lt=comic.published).order_by('-published')[0]
        except IndexError:
            pass

        try:
            context['last_comic'] = Comic.published_comics.latest('published')
            context['next'] = Comic.published_comics.filter(published__gt=comic.published).order_by('published')[0]
        except IndexError:
            pass

        return context


class ComicListView(ListView):
    template_name = "comic_list.html"
    queryset = Comic.published_comics.all()

class PostView(TemplateView):
    template_name = "postview.html"

    def get_context_data (self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'], is_live=True)
        context['post'] = post
        context['disqus_indentifier'] = post.slug
        return context

