import datetime

from allauth.socialaccount.models import SocialToken

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
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
    FormView,
)

from comics.models import (
    Post,
    Comic,
    Character,
    Tag,
)
from comics.forms import (
    ComicPostForm,
    ComicDeleteForm,
    CharacterForm,
    PostForm,
    TagForm,
)
from comics import settings as site_settings

from pebbles.models import (
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

    def get_context_data(self, **kwargs):
        context = super(NeedsPebbleMixin, self).get_context_data(**kwargs)
        context['pebble_characters'] = self.request.pebble.characters()
        context['about_page'] = self.request.pebble.about_page()

        return context


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
        pebble = self.request.pebble
        try:
            pebble_settings_obj = PebbleSettings.objects.get(
                pebble=pebble,
            )
            pebble_settings = pebble_settings_obj.settings
            primary_url = pebble_settings_obj.primary_domain.url
        except (PebbleSettings.DoesNotExist, AttributeError):
            pebble_settings = None
            primary_url = None

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

        post = self.post
        comic = self.comic

        try:
            context['tags'] = comic.tags.all()
        except ValueError:
            pass

        context['slug'] = slug
        context['post'] = post
        context['comic'] = comic
        context['writers'] = comic.writers()
        context['artists'] = comic.artists()
        context['creators'] = comic.creators()

        if pebble_settings and pebble_settings.get('show_disqus'):
            context['disqus_identifier'] = slug
            context['disqus_title'] = self.comic.title
            context['disqus_url'] = 'http://%s/comic/%s/' % (
                primary_url,
                post.slug,
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

        try:
            story_tag = comic.tags.filter(is_story=True)[0]
            story_start = story_tag.get_first_comic()
            if story_start == comic:
                try: 
                    context['chapter_backward'] = story_tag.previous_tag.get_first_comic()
                except AttributeError:
                    pass
            else:
                context['chapter_backward'] = story_start
        except (IndexError, ValueError) as e:
            pass

        try:
            story_tag = comic.tags.filter(is_story=True)[0]
            context['chapter_forward'] = story_tag.next_tag.get_first_comic()
        except (IndexError, AttributeError, ValueError) as e:
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
        if hasattr(self, 'empty'):
            return ['empty.html']
        return [self.template_name]


class ComicPostView(NeedsPebbleMixin, ComicViewMixin, TemplateView):
    template_name = "comicpostview.html"


class ComicListView(NeedsPebbleMixin, ListView):
    template_name = "comic_list.html"

    def get_queryset(self):
        return Comic.published_comics.filter(pebbles=self.request.pebble).order_by('published')

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

    def get_context_data(self, **kwargs):
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
        post = get_object_or_404(Post, id=self.kwargs['id'])
        context['post'] = post
        return context


class StaticPageView(TemplateView):
    template_name = "base.html"

    def dispatch(self, *args, **kwargs):
        template = kwargs.get('template')
        self.template_name = template if template else self.template_name
        return super(StaticPageView, self).dispatch(*args, **kwargs)


class TaggedComicView(ListView):

    template_name = "tag_list.html"


    def get_queryset(self):
        self.tag = get_object_or_404(
            Tag,
            id=self.kwargs['id'],
            pebbles__in=[self.request.pebble],
        )
        return Comic.objects.filter(
            tags__in=[self.tag],
            pebbles__in=[self.request.pebble],
        )

    def get_context_data(self, **kwargs):
        context = super(TaggedComicView, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        pebble_settings = PebbleSettings.objects.get(pebble=self.request.pebble).settings
        context['pebble_settings'] = pebble_settings

        return context

class TagListView(ListView):

    template_name = "tags.html"

    def get_queryset(self, **kwargs):
        return Tag.objects.filter(pebbles__in=[self.request.pebble])

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        pebble_settings = PebbleSettings.objects.get(pebble=self.request.pebble).settings
        context['pebble_settings'] = pebble_settings

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

    def get_form_kwargs(self):
        kwargs = super(ComicEditBaseView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles
        tags = Tag.objects.filter(pebbles__in=pebbles)
        kwargs['tags'] = tags
        return kwargs


class ComicAddView(ComicEditBaseView):
    url_name = 'comicaddview'

    def get_success_url(self):
        return reverse('comicpreviewview', kwargs={'id': self.comic_id})

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        slug = form.cleaned_data.get('slug')
        if not slug or slug == '':
            slug = slugify(form.cleaned_data['title'])
        if Post.objects.filter(pebbles=pebble, slug=slug).exists():
            slug = '%s-%s' % (slug, timezone.now().strftime('%Y%m%d'))
        self.slug = slug

        domain = PebbleSettings.objects.get(pebble=pebble).primary_domain

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

        tags = Tag.objects.filter(id__in=form.cleaned_data.get('tags'))
        for tag in tags:
            post.tags.add(tag)
            comic.tags.add(tag)

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
        kwargs['selected_pebble'] = self.comic.pebbles.all()[0].id
        tags = self.comic.tags.all()
        if tags:
            kwargs['selected_tags'] = tags

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

        comic.tags.clear()
        post.tags.clear()
        tags = Tag.objects.filter(id__in=form.cleaned_data.get('tags'))
        for tag in tags:
            post.tags.add(tag)
            comic.tags.add(tag)

        if pebble not in comic.pebbles.all():
            comic.pebbles.add(pebble)
        
        return super(ComicEditView, self).form_valid(form)


class ShareView(TemplateView):
    template_name = "share.html"

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)

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


class ComicDeleteView(NeedsLoginMixin, FormView):
    template_name = "delete_comic.html"
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(ComicDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.comic = get_object_or_404(Comic, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(ComicDeleteView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComicDeleteView, self).get_context_data(**kwargs)
        context['comic'] = self.comic

        return context

    def form_valid(self, form):
        really_delete = form.cleaned_data.get('really_delete')

        if really_delete == 'yes':
            pebbles = self.comic.pebbles.all()
            for pebble in pebbles:
                self.comic.pebbles.remove(pebble)
                self.comic.post.pebbles.remove(pebble)

        return super(ComicDeleteView, self).form_valid(form)


class CharacterAddView(NeedsLoginMixin, FormView):
    form_class = CharacterForm
    template_name = "edit_character.html"

    def get_success_url(self):
        return reverse('dashview')

    def get_form_kwargs(self):
        kwargs = super(CharacterAddView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        character = Character.objects.create(
            name=form.cleaned_data.get('name'),
            description=form.cleaned_data.get('description'),
            profile_pic_url=form.cleaned_data.get('profile_pic_url'),
        )
        character.pebbles.add(pebble)

        return super(CharacterAddView, self).form_valid(form)


class CharacterEditView(NeedsLoginMixin, FormView):
    form_class = CharacterForm
    template_name = "edit_character.html"

    def get_success_url(self):
        return reverse('dashview')

    def get_context_data(self, **kwargs):
        context = super(CharacterEditView, self).get_context_data(**kwargs)
        context['is_editing'] = True

        return context

    def get(self, request, *args, **kwargs):
        self.character = get_object_or_404(Character, id=self.kwargs.get('id'))
        pebbles = self.character.pebbles.all()
        for pebble in pebbles:
            if not pebble.can_edit(self.request.user):
                raise Http404()

        return super(CharacterEditView, self).get(request, *args, **kwargs)

    def get_initial(self):
        character = self.character

        initial = {
            'name': character.name,
            'description': character.description,
            'profile_pic_url': character.profile_pic_url,
        }

        return initial

    def get_form_kwargs(self):
        self.character = get_object_or_404(Character, id=self.kwargs.get('id'))
        kwargs = super(CharacterEditView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles
        kwargs['selected_pebble'] = self.character.pebbles.all()[0].id

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))

        character = self.character

        character.name = form.cleaned_data.get('name')
        character.description = form.cleaned_data.get('description')
        character.profile_pic_url = form.cleaned_data.get('profile_pic_url')
        character.save()

        if pebble not in character.pebbles.all():
            character.pebbles.add(pebble)

        return super(CharacterEditView, self).form_valid(form)


class CharacterView(NeedsPebbleMixin, TemplateView):
    template_name = "characterview.html"

    def get_context_data(self, **kwargs):
        context = super(CharacterView, self).get_context_data(**kwargs)
        pebble = self.request.pebble
        character = get_object_or_404(Character, pebbles=pebble, id=self.kwargs['id'])
        context['character'] = character
        pebble_settings = PebbleSettings.objects.get(pebble=pebble).settings
        context['pebble_settings'] = pebble_settings
        return context


class CharacterListView(NeedsPebbleMixin, TemplateView):
    template_name = "characterlist.html"

    def get_context_data(self, **kwargs):
        context = super(CharacterListView, self).get_context_data(**kwargs)
        pebble = self.request.pebble
        characters = pebble.characters()
        context['characters'] = characters
        pebble_settings = PebbleSettings.objects.get(pebble=pebble).settings
        context['pebble_settings'] = pebble_settings
        return context


class CharacterDeleteView(NeedsLoginMixin, FormView):
    template_name = 'character_delete.html'
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.character = get_object_or_404(Character, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(CharacterDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.character = get_object_or_404(Character, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(CharacterDeleteView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CharacterDeleteView, self).get_context_data(**kwargs)
        context['character'] = self.character

        return context

    def form_valid(self, form):
        really_delete = form.cleaned_data.get('really_delete')

        if really_delete == 'yes':
            pebbles = self.character.pebbles.all()
            for pebble in pebbles:
                self.character.pebbles.remove(pebble)

        return super(CharacterDeleteView, self).form_valid(form)


class PostAddView(NeedsLoginMixin, FormView):
    template_name = "post_edit.html"
    form_class = PostForm

    def get_success_url(self):
        return reverse('dashview')

    def get_form_kwargs(self):
        kwargs = super(PostAddView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        post = Post.objects.create(
            title=form.cleaned_data.get('title'),
            slug=form.cleaned_data.get('slug'),
            published=form.cleaned_data.get('published'),
            is_live=form.cleaned_data.get('is_live'),
            post=form.cleaned_data.get('post'),
            creator = self.request.user,
        )
        post.pebbles.add(pebble)

        return super(PostAddView, self).form_valid(form)


class PostEditView(NeedsLoginMixin, FormView):
    template_name = "post_edit.html"
    form_class = PostForm

    def get(self, request, *args, **kwargs):
        self.thispost = get_object_or_404(Post, id=self.kwargs.get('id'))
        pebbles = self.thispost.pebbles.all()
        for pebble in pebbles:
            if not pebble.can_edit(self.request.user):
                raise Http404()

        return super(PostEditView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.thispost = get_object_or_404(Post, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(PostEditView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashview')

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['is_editing'] = True

        return context

    def get_form_kwargs(self):
        kwargs = super(PostEditView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def get_initial(self):
        post = self.thispost

        initial = {
            'title': post.title,
            'slug': post.slug,
            'post': post.post,
            'is_live': post.is_live,
            'publised': post.published,
        }

        return initial

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))

        post = self.thispost
        post.title = form.cleaned_data.get('title')
        post.slug = form.cleaned_data.get('slug')
        post.post = form.cleaned_data.get('post')
        post.is_live = form.cleaned_data.get('is_live')
        post.published = form.cleaned_data.get('published')
        post.save()

        if pebble not in post.pebbles.all():
            post.pebbles.add(pebble)

        return super(PostEditView, self).form_valid(form)


class PostDeleteView(NeedsLoginMixin, FormView):
    template_name = "post_delete.html"
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.thispost = get_object_or_404(Post, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(PostDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.thispost = get_object_or_404(Post, id=self.kwargs.get('id'), pebbles__in=pebbles)

        return super(PostDeleteView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)
        context['post'] = self.thispost

        return context

    def form_valid(self, form):
        really_delete = form.cleaned_data.get('really_delete')

        if really_delete == 'yes':
            pebbles = self.thispost.pebbles.all()
            for pebble in pebbles:
                self.thispost.pebbles.remove(pebble)

        return super(PostDeleteView, self).form_valid(form)


class LiveComicView(TemplateView):
    template_name="main_home.html"


class TagAddView(NeedsLoginMixin, FormView):
    form_class = TagForm
    template_name = "tag_edit.html"

    def get_success_url(self):
        return reverse('dashview')

    def get_form_kwargs(self):
        kwargs = super(TagAddView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        tags = Tag.objects.filter(pebbles__in=pebbles)
        kwargs['pebbles'] = pebbles
        kwargs['tags'] = tags
        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        tag = Tag.objects.create(
            tag=form.cleaned_data.get('tag'),
            description=form.cleaned_data.get('description'),
            header_image=form.cleaned_data.get('header_image'),
        )
        tag.pebbles.add(pebble)

        return super(TagAddView, self).form_valid(form)


class TagEditView(NeedsLoginMixin, FormView):
    form_class = TagForm
    template_name = "tag_edit.html"

    def get_success_url(self):
        return reverse('dashview')

    def get_context_data(self, **kwargs):
        context = super(TagEditView, self).get_context_data(**kwargs)
        context['is_editing'] = True
        return context

    def get(self,request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, id=self.kwargs.get('id'))
        pebbles = self.tag.pebbles.all()
        for pebble in pebbles:
            if not pebble.can_edit(self.request.user):
                raise Http404()

        return super(TagEditView, self).get(request, *args, **kwargs)

    def get_initial(self):
        tag = self.tag

        initial = {
            'tag': tag.tag,
            'description': tag.description,
            'header_image': tag.header_image,
        }
        return initial

    def get_form_kwargs(self):
        self.tag = get_object_or_404(Tag, id=self.kwargs.get('id'))
        kwargs = super(TagEditView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        tags = Tag.objects.filter(pebbles__in=pebbles)
        kwargs['pebbles'] = pebbles
        kwargs['tags'] = tags
        kwargs['selected_pebble'] = self.tag.pebbles.all()[0].id

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        tag = self.tag
        tag.tag = form.cleaned_data.get('tag')
        tag.description = form.cleaned_data.get('description')
        tag.header_image = form.cleaned_date.get('header_image')
        tag.save()

        if pebble not in tag.pebbles.all():
            tag.pebbles.add(pebble)

        return super(TagEditView, self).form_valid(form)

