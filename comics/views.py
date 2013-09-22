from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView,
    ListView,
)

from comics.models import (
    Post,
    Comic,
)

class PreviewView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PreviewView, self).dispatch(*args, **kwargs)

class ComicViewMixin(object):

    def get_comic(self, post=None):
        if post: 
            return Comic.published_comics.get(post=post)
        else:
            return Comic.published_comics.latest('published')

class HomeView(ComicViewMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        comic = self.get_comic()
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

class ComicPostView(ComicViewMixin, TemplateView):
    template_name = "comicpostview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPostView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'], is_live=True)
        comic = self.get_comic(post=post)

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


class ComicPreviewView(PreviewView):
    template_name = "comicpostview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPreviewView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        comic = Comic.objects.get(post=post)

        context['post'] = post
        context['comic'] = comic

        return context


class PostView(TemplateView):
    template_name = "postview.html"

    def get_context_data (self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'], is_live=True)
        context['post'] = post
        context['disqus_indentifier'] = post.slug
        return context


class PostPreviewView(PreviewView):
    template_name = "postview.html"

    def get_context_data(self, **kwargs):
        context = super(PostPreviewView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        context['post'] = post
        return context

