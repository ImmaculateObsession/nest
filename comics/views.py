import mandrill
import base64
import hashlib
import datetime

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
    ReferralHit,
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

    def get_context_data(self, **kwargs):
        context = super(ComicViewMixin, self).get_context_data(**kwargs)

        post = None
        if kwargs.get('slug'):
            post = get_object_or_404(
                Post,
                slug=self.kwargs['slug'],
                is_live=True
            )
            self.post = post

        self.comic = self.get_comic(post)
        last_read_comic = self.request.COOKIES.get('last_read_comic')
        hide_resume_link = self.request.COOKIES.get('hide_resume_link')
        long_id = self.comic.post.slug if self.comic.post else self.comic.title

        if (
            last_read_comic and
            not hide_resume_link and
            last_read_comic != long_id
        ):
            context['last_read_comic'] = self.request.COOKIES.get('last_read_comic')

        context['disqus_identifier'] = long_id

        return context

    def render_to_response(self, context, **kwargs):
        response = super(ComicViewMixin, self).render_to_response(context, **kwargs)
        if response.context_data.get('disqus_identifier'):
            response.set_cookie(
                'last_read_comic',
                value=response.context_data.get('disqus_identifier'),
                expires=timezone.now() + datetime.timedelta(days=7),
            )
            response.set_cookie(
                'hide_resume_link',
                value='true',
                max_age=3600,
            )
        return response


class HomeView(ComicViewMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        comic = self.comic
        context['comic'] = comic
        if comic.post:
            context['post'] = comic.post
            context['disqus_url'] = 'http://captainquail.com/comic/%s/' % (comic.post.slug)
        else:
            context['disqus_url'] = 'http://www.captainquail.com/'
        try:
            context['first_comic'] = Comic.published_comics.filter(published__lt=comic.published).order_by('published')[0]
            context['previous'] = Comic.published_comics.filter(published__lt=comic.published).order_by('-published')[0]
        except IndexError:
            pass
        context['disqus_title'] = comic.title

        return context

class ComicPostView(ComicViewMixin, TemplateView):
    template_name = "comicpostview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPostView, self).get_context_data(**kwargs)
        post = self.post
        comic = self.comic

        context['post'] = post
        context['comic'] = comic
        context['disqus_url'] = 'http://captainquail.com/comic/%s/' % (post.slug)

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
        context['disqus_title'] = comic.title
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
        context['disqus_identifier'] = post.slug
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
            management.call_command('dumpdata', 'comics', indent=4, stdout=f)
            
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
                    'to': [{'email': settings.ADMINS[0][1], 'name': settings.ADMINS[0][0]}],
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

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        codes = ReferralCode.objects.filter(user=self.user)
        context['codes'] = codes

        return context


class PlaygroundView(TemplateView):

    template_name = "playground.html"

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaygroundView, self).dispatch(*args, **kwargs)

class TagView(ListView):

    template_name = "tag_list.html"

    def get_queryset(self):
        return Comic.objects.filter(tags__tag__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['tag'] = self.kwargs['tag']

        return context

