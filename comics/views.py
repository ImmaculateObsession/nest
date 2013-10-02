import mandrill
import base64
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core import management
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    ListView,
    View,
    DetailView,
)

from comics.models import (
    Post,
    Comic,
    ReferralCode,
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


class ComicBackupView(View):

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        with open(str(settings.PROJECT_ROOT) + '/dump.json', 'w') as f:
            management.call_command('dumpdata', indent=4, stdout=f)
            
        with open(str(settings.PROJECT_ROOT) + '/dump.json', 'r') as f: 
            data = base64.b64encode(f.read())

            try:
                mandrill_client = mandrill.Mandrill(settings.EMAIL_HOST_PASSWORD)
                message = {
                    'attachments': [{
                        'content': data,
                        'name': 'dump.json',
                        'type': 'application/json'
                    }],
                    'auto_html': None,
                    'auto_text': None,
                    'from_email': 'site@quailcomics.com',
                    'from_name': 'Quail Comics Site',
                    'html': "Here's the backup",
                    'subject': 'Backup of quailcomics.com',
                    'to': [{'email': 'philip@immaculateobsession.com' , 'name': 'Philip James'}],
                }
                result = mandrill_client.messages.send(message=message, async=False)

                messages.add_message(self.request, messages.SUCCESS, 'Backup emailed.')

            except mandrill.Error, e:
                print 'A mandrill error occurred: %s - %s' % (e.__class__, e)

        return redirect('/admin', permanent=False)

        return super(RedirectView, self).dispatch(*args, **kwargs)


class CreateRefCodeView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        referral_code = ReferralCode.objects.create(
            code=hashlib.sha1(
                str(user) + str(timezone.now())
            ).hexdigest()[:6],
            user=self.request.user,
            is_active=True,
            campaign='First Round of Shirts',
        )

        return redirect('/accounts/profile/')



class ProfileView(DetailView):
    template_name="profile.html"
    model = User

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.user = self.request.user
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.user

