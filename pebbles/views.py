from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import (
    FormView,
    TemplateView,
)
from petroglyphs.models import Setting

from comics.forms import ComicDeleteForm
from comics.models import Comic
from comics.views import (
    NeedsLoginMixin,
    NeedsPebbleMixin,
)

from pebbles.forms import (
    PebblePageForm,
    PebbleSettingsForm,
)

from pebbles.models import (
    Pebble,
    Domain,
    PebbleSettings,
    PebblePage,
)

from petroglyphs.models import Setting


class HomeView(TemplateView):
    template_name = 'main_home.html'


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)

        comic_dict = {}
        for pebble in pebbles:
            comic_dict[str(pebble.id)] = Comic.objects.filter(pebbles=pebble)

        context['pebbles'] = pebbles

        context['comics'] = comic_dict

        return context


class PebblePageView(NeedsPebbleMixin, TemplateView):
    template_name = "pebblepage.html"

    def get_context_data(self, **kwargs):
        context = super(PebblePageView, self).get_context_data(**kwargs)
        context['page'] = get_object_or_404(
            PebblePage,
            slug=kwargs['slug'],
            is_live=True,
            pebble=self.request.pebble,
        )
        context['pebble_settings'] = get_object_or_404(
            PebbleSettings,
            pebble=self.request.pebble,
        ).settings

        return context

class AddPageView(NeedsLoginMixin, FormView):
    template_name = "add_pebble_page.html"
    form_class = PebblePageForm

    def get_success_url(self):
        return reverse('dashview')

    def get_form_kwargs(self):
        kwargs = super(AddPageView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles

        return kwargs

    def form_valid(self, form):
        pebble = Pebble.objects.get(id=form.cleaned_data.get('pebble'))
        slug = form.cleaned_data.get('slug')
        pebble_page = PebblePage.objects.create(
            title=form.cleaned_data['title'],
            slug=slug,
            is_live=form.cleaned_data['is_live'],
            standalone=form.cleaned_data['standalone'],
            content=form.cleaned_data['content'],
            pebble=pebble,
        )

        return super(AddPageView, self).form_valid(form)


class EditPageView(NeedsLoginMixin, FormView):
    template_name = "add_pebble_page.html"
    form_class = PebblePageForm

    def get_success_url(self):
        return reverse('dashview')

    def get_context_data(self, **kwargs):
        context = super(EditPageView, self).get_context_data(**kwargs)
        context['is_editing'] = True

        return context

    def get_form_kwargs(self):
        self.page = get_object_or_404(PebblePage, id=self.kwargs.get('id'))
        kwargs = super(EditPageView, self).get_form_kwargs()
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        kwargs['pebbles'] = pebbles
        kwargs['selected_pebble'] = self.page.pebble.id

        return kwargs

    def get(self, request, *args, **kwargs):
        page = get_object_or_404(PebblePage, id=self.kwargs.get('id'))
        if not page.pebble or not page.pebble.can_edit(self.request.user):
            raise Http404()

        return super(EditPageView, self).get(request, *args, **kwargs)

    def get_initial(self):
        page = self.page

        initial = {
            'title': page.title,
            'is_live': page.is_live,
            'standalone': page.standalone,
            'content': page.content,
            'slug': page.slug,
            'pebble': page.pebble.id,
        }

        return initial

    def form_valid(self, form):
        page = self.page

        page.title = form.cleaned_data['title']
        page.slug = form.cleaned_data['slug']
        page.is_live = form.cleaned_data['is_live']
        page.standalone = form.cleaned_data['standalone']
        page.content = form.cleaned_data['content']
        page.pebble = Pebble.objects.get(id=form.cleaned_data['pebble'])

        return super(EditPageView, self).form_valid(form)


class DeleteView(NeedsLoginMixin, FormView):
    template_name = "delete_page.html"
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.page = get_object_or_404(PebblePage, id=self.kwargs.get('id'), pebble__in=pebbles)

        return super(DeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.get_pebbles_for_user(self.request.user)
        self.page = get_object_or_404(PebblePage, id=self.kwargs.get('id'), pebble__in=pebbles)

        return super(DeleteView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['page'] = self.page

        return context

    def form_valid(self, form):
        really_delete = form.cleaned_data.get('really_delete')

        if really_delete == 'yes':
            self.page.pebble = None
            self.page.save()

        return super(DeleteView, self).form_valid(form)


class EditPebbleView(NeedsLoginMixin, FormView):
    template_name = "pebble_edit.html"
    form_class = PebbleSettingsForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        self.pebble_settings = get_object_or_404(PebbleSettings, id=self.kwargs.get('id'))
        if not self.pebble_settings.pebble.can_edit(self.request.user):
            raise Http404()

        return super(EditPebbleView, self).get(request, *args, **kwargs)

    def get_initial(self):
        settings = self.pebble_settings.settings

        initial = {
            'site_title': settings.get('site_title'),
            'facebook_page': settings.get('facebook_page'),
            'twitter_page': settings.get('twitter_page'),
            'youtube_channel': settings.get('youtube_channel'),
            'tagline': settings.get('tagline'),
            'show_rss': settings.get('show_rss'),
            'copyright': settings.get('copyright'),
            'feed_description': settings.get('feed_description'),
            'feed_title': settings.get('feed_title'),
        }

        return initial

    def get_form_kwargs(self):
        self.pebble_settings = get_object_or_404(PebbleSettings, id=self.kwargs.get('id'))
        return super(EditPebbleView, self).get_form_kwargs()

    def form_valid(self, form):
        settings = self.pebble_settings.settings

        settings['site_title'] = form.cleaned_data.get('site_title')
        settings['facebook_page'] = form.cleaned_data.get('facebook_page')
        settings['twitter_page'] = form.cleaned_data.get('twitter_page')
        settings['youtube_channel'] = form.cleaned_data.get('youtube_channel')
        settings['tagline'] = form.cleaned_data.get('tagline')
        settings['show_rss'] = form.cleaned_data.get('show_rss')
        settings['copyright'] = form.cleaned_data.get('copyright')
        settings['feed_description'] = form.cleaned_data.get('feed_description')
        settings['feed_title'] = form.cleaned_data.get('feed_title')

        self.pebble_settings.settings = settings
        self.pebble_settings.save()

        return super(EditPebbleView, self).form_valid(form)

