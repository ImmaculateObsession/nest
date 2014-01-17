import mandrill
import base64
import hashlib
import datetime

from allauth.socialaccount.models import SocialToken

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import get_current_site
from django.core import management
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.http import (
    HttpResponsePermanentRedirect,
    Http404,
)
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import (
    TemplateView,
    ListView,
    View,
    DetailView,
    FormView,
    CreateView,
)

from comics.models import (
    Post,
    Comic,
    PublishedComicManager,
)
from comics.forms import ComicPostForm
from comics import settings as site_settings

from pebbles.models import (
    Domain,
    Pebble,
    PebbleSettings,
)

from petroglyphs.models import Setting

from saltpeter.models import SocialPost


class StaffMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffMixin, self).dispatch(*args, **kwargs)


class ComicViewMixin(object):

    def get_comic(self):
        """
        This function exists to be mocked by testing. There must be a
        better way to do this.
        """
        return Comic.published_comics.filter(
            pebbles=self.request.pebble
            ).latest('published')

    # TODO: Pull this logic into a more testable function
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        
        if slug:
            pebble = self.request.pebble
            post = None
            try:
                post = Post.published_posts.get(
                    pebbles=pebble,
                    slug=slug
                )
            except Post.DoesNotExist:
                pass
            if post:
                self.comic = Comic.published_comics.get(pebbles=pebble, post=post)
                self.post = post
            else:
                try:
                    comic = Comic.published_comics.get(pebbles=pebble, id=int(slug))
                except Comic.DoesNotExist:
                    raise Http404
                if comic and Post.published_posts.get(pebbles=pebble, slug=slugify(comic.title)):
                    return HttpResponsePermanentRedirect(
                        reverse(
                            'comicpostview',
                            kwargs={'slug':slugify(comic.title)},
                        ),
                    )
        else:
            try:
                self.comic = self.get_comic()
                self.post = self.comic.post
            except Comic.DoesNotExist:
                self.empty = True

        return super(ComicViewMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComicViewMixin, self).get_context_data(**kwargs)

        try:
            pebble_settings = PebbleSettings.objects.get(
                pebble=self.request.pebble
            ).settings
        except PebbleSettings.DoesNotExist:
            pebble_settings = None

        context['pebble_settings'] = pebble_settings

        if hasattr(self, 'empty'):
            return context
        
        last_read_comic = self.request.COOKIES.get('last_read_comic')
        hide_resume_link = self.request.COOKIES.get('hide_resume_link')
        long_id = self.comic.post.slug if self.comic.post else self.comic.title

        if (
            last_read_comic and
            not hide_resume_link and
            last_read_comic != long_id
        ):
            context['last_read_comic'] = self.request.COOKIES.get('last_read_comic')

        if pebble_settings and pebble_settings.get('show_disqus'):
            context['disqus_identifier'] = long_id
            context['disqus_title'] = self.comic.title
        context['page_url'] = self.request.build_absolute_uri()

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
        if hasattr(self, 'empty'):
            self.template_name ="empty.html"
            return context

        pebble=self.request.pebble
        comic = self.comic
        context['comic'] = comic
        if comic.post:
            context['post'] = comic.post
            context['disqus_url'] = '%s/comic/%s/' % (
                site_settings.site_url(),
                comic.post.slug
            )
        else:
            context['disqus_url'] = site_settings.site_url()
        try:
            context['first_comic'] = Comic.published_comics.filter(
                pebbles=pebble,
                published__lt=comic.published,
            ).order_by('published')[0]
            context['previous'] = Comic.published_comics.filter(
                pebbles=pebble,
                published__lt=comic.published,
            ).order_by('-published')[0]
        except IndexError:
            pass

        return context

class ComicPostView(ComicViewMixin, TemplateView):
    template_name = "comicpostview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPostView, self).get_context_data(**kwargs)
        pebble = self.request.pebble
        post = self.post
        comic = self.comic

        context['post'] = post
        context['comic'] = comic
        context['disqus_url'] = '%s/comic/%s/' % (
            site_settings.site_url(),
            post.slug
        )

        try: 
            context['first_comic'] = Comic.published_comics.filter(
                pebbles=pebble,
                published__lt=comic.published,
            ).order_by('published')[0]
            context['previous'] = Comic.published_comics.filter(
                pebbles=pebble,
                published__lt=comic.published,
            ).order_by('-published')[0]
        except IndexError:
            pass

        try:
            last_comic = Comic.published_comics.latest('published')
            if last_comic != self.comic:
                context['last_comic'] = last_comic
            context['next'] = Comic.published_comics.filter(published__gt=comic.published).order_by('published')[0]
        except IndexError:
            pass
        
        return context


class ComicListView(ListView):
    template_name = "comic_list.html"
    queryset = Comic.published_comics.all()


class ComicPreviewView(StaffMixin, TemplateView):
    template_name = "comicpreview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPreviewView, self).get_context_data(**kwargs)
        comic = get_object_or_404(Comic, id=self.kwargs['id'])
        post = comic.post

        context['post'] = post
        context['comic'] = comic
        context['hide_share'] = True

        return context


class PostView(TemplateView):
    template_name = "postview.html"

    def get_context_data (self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        pebble = self.request.pebble
        post = get_object_or_404(Post, pebbles=pebble, slug=self.kwargs['slug'], is_live=True)
        context['post'] = post
        context['disqus_identifier'] = post.slug
        context['disqus_url'] = '%s/post/%s/' % (
            site_settings.site_url(),
            post.slug
        )
        context['disqus_title'] = post.title
        return context


class PostPreviewView(StaffMixin, TemplateView):
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
                    'from_name': site_settings.site_title(),
                    'html': "Here's the backup",
                    'subject': 'Backup of %s' % (site_settings.site_url()),
                    'to': [{'email': settings.ADMINS[0][1], 'name': settings.ADMINS[0][0]}],
                }
                result = mandrill_client.messages.send(message=message, async=False)

                messages.add_message(self.request, messages.SUCCESS, 'Backup emailed.')

            except mandrill.Error, e:
                print 'A mandrill error occurred: %s - %s' % (e.__class__, e)

        return redirect('/admin', permanent=False)


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

        return context


class PlaygroundView(TemplateView):

    template_name = "playground.html"

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaygroundView, self).dispatch(*args, **kwargs)

class StaticPageView(TemplateView):
    template_name = "base.html"

    def dispatch(self, *args, **kwargs):
        template = kwargs.get('template')
        self.template_name = template if template else self.template_name
        return super(StaticPageView, self).dispatch(*args, **kwargs)

class TagView(ListView):

    template_name = "tag_list.html"

    def get_queryset(self):
        return Comic.objects.filter(tags__tag__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['tag'] = self.kwargs['tag']

        return context


class ComicAddView(StaffMixin, FormView):

    form_class = ComicPostForm
    template_name = "add_comic.html"

    def dispatch(self, request, *args, **kwargs):

        main_domain = Setting.objects.get(key='site_url').value
        url = 'http://%s%s' % (main_domain, reverse('comicaddview'))

        if request.META.get('HTTP_HOST') != main_domain:
            return HttpResponsePermanentRedirect(url)

        return super(ComicAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('comicpreviewview', kwargs={'id': self.comic_id})

    def get_form_kwargs(self):
        kwargs = super(ComicAddView, self).get_form_kwargs()
        pebbles = Pebble.objects.filter(creator=self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ComicAddView, self).get_context_data(**kwargs)

        try:
            fb_token = SocialToken.objects.get(
                account__user=self.request.user,
                app__provider='facebook'
            ).token
        except: 
            fb_token = None

        try:
            tw_token = SocialToken.objects.get(
                account__user=self.request.user,
                app__provider='twitter'
            )
        except:
            tw_token = None

        context['fb_token'] = fb_token
        context['tw_token'] = tw_token

        return context


    def form_valid(self, form):
        slug = form.cleaned_data.get('slug')
        if slug == '':
            if Post.objects.filter(slug=slug).exists():
                slug = '%s-%s' % (
                    slugify(form.cleaned_data['title']),
                    timezone.now().strftime('%Y%m%d'),
                )
            else: 
                slug = slugify(form.cleaned_data['title'])
        self.slug = slug

        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        domain = Domain.objects.filter(pebble=pebble)[0]
        self.domain = domain

        post = Post.objects.create(
            title=form.cleaned_data['title'],
            published=form.cleaned_data['published'],
            post=form.cleaned_data['post'],
            slug=self.slug,
            is_live=form.cleaned_data.get('is_live', False),
        )
        post.pebbles.add(pebble)

        comic = Comic.objects.create(
            title=form.cleaned_data['title'],
            published=form.cleaned_data['published'],
            is_live=form.cleaned_data.get('is_live', False),
            post=post,
            alt_text=form.cleaned_data.get('alt_text', ''),
            image_url=form.cleaned_data['image_url'],
            image_url_large=form.cleaned_data.get('image_url_large', ''),
        )
        comic.pebbles.add(pebble)

        self.comic_id = comic.id

        if form.cleaned_data.get('post_to_social'):
            if form.cleaned_data.get('facebook_post_message'):
                facebook_post = SocialPost.objects.create(
                    user=self.request.user,
                    url='%s%s' % (
                        domain.url,
                        reverse('comicpostview', kwargs={'slug': self.slug}),
                    ),
                    message=form.cleaned_data.get('facebook_post_message'),
                    time_to_post=form.cleaned_data.get('social_post_time'),
                    social_network=SocialPost.FACEBOOK,
                )

            if form.cleaned_data.get('twitter_post_message'):
                twitter_post = SocialPost.objects.create(
                    user=self.request.user,
                    url='%s%s' % (
                        domain.url,
                        reverse('comicpostview', kwargs={'slug':self.slug}),
                    ),
                    message=form.cleaned_data.get('twitter_post_message'),
                    time_to_post=form.cleaned_data.get('social_post_time'),
                    social_network=SocialPost.TWITTER,
                )

        return super(ComicAddView, self).form_valid(form)


class ShareView(TemplateView):
    template_name = "share.html"

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)

        current_site = get_current_site(self.request)

        pebble = self.request.pebble
        pebble_settings = PebbleSettings.objects.get(pebble=pebble).settings

        slug = self.request.COOKIES.get('last_read_comic')
        if slug:
            try:
                comic = Comic.published_comics.get(
                    pebbles=pebble,
                    post__slug=slug,
                )
            except Comic.DoesNotExist:
                comic = None

            if comic:
                context['url_to_share'] = '%s%s/comic/%s' % ('http://', pebble_settings.get('default_domain'), comic.post.slug)
                context['image_url'] = comic.image_url
                context['title'] = comic.title

        else:
            comic = Comic.published_comics.filter(pebbles=pebble).latest('published')
            context['url_to_share'] = '%s%s' % ('http://', pebble_settings.get('default_domain'))
            context['image_url'] = comic.image_url
            context['title'] = comic.title

        context.update({
            'pebble_settings': pebble_settings
            })

        return context
