import mandrill
import base64
import hashlib
import datetime

from allauth.socialaccount.models import SocialToken

from mixpanel import Mixpanel

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
    PublishedPostManager,
)
from comics.forms import (
    ComicPostForm,
    ComicDeleteForm,
)
from comics import settings as site_settings

from pebbles.models import (
    Domain,
    Pebble,
    PebbleSettings,
)

from petroglyphs.models import Setting

from saltpeter.models import SocialPost


class NeedsLoginMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NeedsLoginMixin, self).dispatch(request, *args, **kwargs)

class NeedsPebbleMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.pebble:
            raise Http404()
        return super(NeedsPebbleMixin, self).dispatch(request, *args, **kwargs)



class ComicViewMixin(object):

    def get_comic(self):
        """
        This function exists to be mocked by testing. There must be a
        better way to do this.
        """
        return Comic.published_comics.filter(
            pebbles=self.request.pebble
            ).latest('published')

    def get(self, request, *args, **kwargs):

        self.pebble = self.request.pebble
        slug = kwargs.get('slug')
        comic_id = kwargs.get('id')
        
        if slug:
            self.post = get_object_or_404(Post.published_posts, pebbles=self.pebble, slug=slug)
            self.comic = get_object_or_404(Comic.published_comics, pebbles=self.pebble, post=self.post)
        elif comic_id:
            try:
                self.comic = Comic.published_comics.filter(pebbles=self.pebble).order_by('published')[int(comic_id) - 1]
                self.post = self.comic.post
            except IndexError:
                raise Http404()
        else:
            try:
                self.comic = self.get_comic()
                self.post = self.comic.post
            except Comic.DoesNotExist:
                self.empty = True

        return super(ComicViewMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComicViewMixin, self).get_context_data(**kwargs)
        pebble=self.request.pebble
        try:
            pebble_settings = PebbleSettings.objects.get(
                pebble=pebble
            ).settings
        except PebbleSettings.DoesNotExist:
            pebble_settings = None

        context['pebble_settings'] = pebble_settings

        if hasattr(self, 'empty'):
            return context
        
        last_read_comic = self.request.COOKIES.get('last_read_comic')
        hide_resume_link = self.request.COOKIES.get('hide_resume_link')
        slug = self.comic.post.slug

        if (
            last_read_comic and
            not hide_resume_link and
            last_read_comic != slug
        ):
            context['last_read_comic'] = self.request.COOKIES.get('last_read_comic')

        if pebble_settings and pebble_settings.get('show_disqus'):
            context['disqus_identifier'] = slug
            context['disqus_title'] = self.comic.title

        post = self.post
        comic = self.comic

        context['slug'] = slug
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
            last_comic = Comic.published_comics.filter(pebbles=pebble).latest('published')
            if last_comic != comic:
                context['last_comic'] = last_comic
        except Comic.DoesNotExist:
            pass
        try:            
            context['next'] = Comic.published_comics.filter(
                pebbles=pebble,
                published__gt=comic.published
            ).order_by('published')[0]
        except IndexError:
            pass

        return context

    def render_to_response(self, context, **kwargs):
        response = super(ComicViewMixin, self).render_to_response(context, **kwargs)
        if response.context_data.get('slug'):
            response.set_cookie(
                'last_read_comic',
                value=response.context_data.get('slug'),
                expires=timezone.now() + datetime.timedelta(days=7),
            )
            response.set_cookie(
                'hide_resume_link',
                value='true',
                max_age=3600,
            )
        return response


class HomeView(NeedsPebbleMixin, ComicViewMixin, TemplateView):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'pebble_settings'):
            self.pebble_settings = PebbleSettings.objects.get(pebble=request.pebble).settings
        if self.pebble_settings.get('is_blog'):
            slug = Post.published_posts.latest('published').slug
            kwargs['slug'] = slug
            return PostView.as_view()(request, *args, **kwargs)
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if hasattr(self,'empty'):
            return ['empty.html']
        return [self.template_name]


class ComicPostView(NeedsPebbleMixin, ComicViewMixin, TemplateView):
    template_name = "comicpostview.html"


class ComicListView(NeedsPebbleMixin, ListView):
    template_name = "comic_list.html"

    def get_queryset(self):
        return Comic.published_comics.filter(pebbles=self.request.pebble)

    def get_context_data(self, **kwargs):
        context = super(ComicListView, self).get_context_data(**kwargs)
        context['pebble_settings'] = PebbleSettings.objects.get(pebble=self.request.pebble).settings

        return context


class ComicPreviewView(NeedsLoginMixin, TemplateView):
    template_name = "comicpreview.html"

    def get_context_data(self, **kwargs):
        context = super(ComicPreviewView, self).get_context_data(**kwargs)
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        comic = get_object_or_404(Comic, id=self.kwargs['id'], pebbles__in=pebbles)
        post = comic.post

        context['post'] = post
        context['comic'] = comic
        context['hide_share'] = True

        return context


class PostView(NeedsPebbleMixin, TemplateView):
    template_name = "postview.html"

    def get_context_data (self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        pebble = self.request.pebble
        post = get_object_or_404(Post.published_posts, pebbles=pebble, slug=self.kwargs['slug'])
        context['post'] = post

        pebble_settings = PebbleSettings.objects.get(pebble=pebble).settings
        context['pebble_settings'] = pebble_settings
        
        if pebble_settings.get('show_disqus'):
            context['disqus_identifier'] = post.slug
            context['disqus_url'] = '%s/post/%s/' % (
                site_settings.site_url(),
                post.slug
            )
            context['disqus_title'] = post.title

        try: 
            context['first_post'] = Post.published_posts.filter(
                pebbles=pebble,
                published__lt=post.published,
            ).order_by('published')[0]
            context['previous'] = Post.published_posts.filter(
                pebbles=pebble,
                published__lt=post.published,
            ).order_by('-published')[0]
        except IndexError:
            pass

        try:
            last_post = Post.published_posts.filter(pebbles=pebble).latest('published')
            if last_post != post:
                context['last_post'] = last_post
        except Comic.DoesNotExist:
            pass
        try:            
            context['next'] = Post.published_posts.filter(
                pebbles=pebble,
                published__gt=post.published
            ).order_by('published')[0]
        except IndexError:
            pass

        return context


class PostPreviewView(NeedsLoginMixin, TemplateView):
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

class ComicEditBaseView(NeedsLoginMixin, FormView):
    form_class = ComicPostForm
    template_name = "add_comic.html"
    url_name = 'dashview'

    def dispatch(self, request, *args, **kwargs):

        main_domain = Setting.objects.get(key='site_url').value
        url = 'http://%s%s' % (main_domain, reverse(self.url_name))

        if request.META.get('HTTP_HOST') != main_domain:
            return HttpResponsePermanentRedirect(url)

        return super(ComicEditBaseView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComicEditBaseView, self).get_context_data(**kwargs)

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

class ComicAddView(ComicEditBaseView):
    url_name = 'comicaddview'

    def get_success_url(self):
        return reverse('comicpreviewview', kwargs={'id': self.comic_id})

    def get_form_kwargs(self):
        kwargs = super(ComicAddView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        slug = form.cleaned_data.get('slug')
        if not slug or slug == '':
            slug = slugify(form.cleaned_data['title'])
        if Post.objects.filter(pebbles=pebble, slug=slug).exists():
            slug = '%s-%s' % (slug, timezone.now().strftime('%Y%m%d'))
        self.slug = slug

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
                    url='http://%s%s' % (
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
                    url='http://%s%s' % (
                        domain.url,
                        reverse('comicpostview', kwargs={'slug':self.slug}),
                    ),
                    message=form.cleaned_data.get('twitter_post_message'),
                    time_to_post=form.cleaned_data.get('social_post_time'),
                    social_network=SocialPost.TWITTER,
                )
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Comic Added', {
            'pebble_id': pebble.id,
            'comic_id': comic.id,
            'posted_to_facebook': bool(form.cleaned_data.get('facebook_post_message')),
            'posted_to_twitter': bool(form.cleaned_data.get('twitter_post_message')),
            'is_live': form.cleaned_data.get('is_live', False),
        })
        return super(ComicAddView, self).form_valid(form)


class ComicEditView(ComicEditBaseView):

    def get_success_url(self):
        return reverse('comiceditview', kwargs={'id': self.kwargs.get('id')})

    def get_context_data(self, **kwargs):
        context = super(ComicEditView, self).get_context_data(**kwargs)
        context['is_editing'] = True
        context['comic_id'] = self.comic.id

        return context

    def get_initial(self):
        comic = self.comic
        post = comic.post

        initial = {
            'title': post.title,
            'image_url': comic.image_url,
            'alt_text': comic.alt_text,
            'published': comic.published,
            'is_live': comic.is_live,
            'slug': post.slug,
            'post': post.post,
            'pebble': comic.pebbles.all()[0].id
        }

        return initial

    def get_form_kwargs(self):
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'))
        kwargs = super(ComicEditView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles
        kwargs['selected_pebble'] = self.comic.pebbles.all()[0].id

        return kwargs

    def get(self, request, *args, **kwargs):
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'))
        pebbles = self.comic.pebbles.all()
        for pebble in pebbles:
            if not pebble.can_edit(self.request.user):
                raise Http404()

        return super(ComicEditView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        slug = form.cleaned_data.get('slug')
        if not slug or slug == '':
            slug = slugify(form.cleaned_data['title'])
        if Post.objects.filter(pebbles=pebble, slug=slug).exists():
            if self.comic.post not in Post.objects.filter(pebbles=pebble, slug=slug):
                slug = '%s-%s' % (slug, timezone.now().strftime('%Y%m%d'))
        self.slug = slug

        comic = self.comic
        post = comic.post

        post.title = form.cleaned_data['title']
        post.published = form.cleaned_data['published']
        post.post = form.cleaned_data['post']
        post.slug = self.slug
        post.is_live = form.cleaned_data.get('is_live', False)
        post.save()

        if pebble not in post.pebbles.all():
            post.pebbles.add(pebble)

        comic.title=form.cleaned_data['title']
        comic.published=form.cleaned_data['published']
        comic.is_live=form.cleaned_data.get('is_live', False)
        comic.alt_text=form.cleaned_data.get('alt_text', '')
        comic.image_url=form.cleaned_data['image_url']
        comic.image_url_large=form.cleaned_data.get('image_url_large', '')
        comic.save()

        if pebble not in comic.pebbles.all():
            comic.pebbles.add(pebble)
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Comic Edited', {
            'pebble_id': pebble.id,
            'comic_id': comic.id,
            'is_live': form.cleaned_data.get('is_live', False),
        })

        return super(ComicEditView, self).form_valid(form)


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


class DeleteView(NeedsLoginMixin, FormView):
    template_name = "delete_comic.html"
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(DeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(DeleteView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['comic'] = self.comic

        return context

    def form_valid(self, form):
        really_delete = form.cleaned_data.get('really_delete')

        if really_delete == 'yes':
            pebbles = self.comic.pebbles.all()
            for pebble in pebbles:
                self.comic.pebbles.remove(pebble)
                self.comic.post.pebbles.remove(pebble)

        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Comic Deleted', {
            'comic_id': self.comic.id,
            'is_live': self.comic.is_live,
        })

        return super(DeleteView, self).form_valid(form)
