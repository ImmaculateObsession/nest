from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from comics.models import (
    Comic,
    Post,
    Contributor
)


class ProfileView(DetailView):
    template_name="profile.html"
    model = User

    def dispatch(self, *args, **kwargs):
        if kwargs.get('username'):
            self.user = get_object_or_404(User, username=kwargs.get('username'))
        elif self.request.user:
            self.user = self.request.user
        else:
            raise Http404()
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.user

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        contributions = Contributor.objects.filter(contributor=self.user)

        comics = Comic.published_comics.filter(
            post__contributor__in=contributions
        ).order_by('-published')

        posts = Post.published_posts.filter(
            contributor__in=contributions
        ).exclude(
            id__in=comics.values_list('post')
        ).order_by('-published')

        context['posts'] = posts
        context['comics'] = comics

        return context