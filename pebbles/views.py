from mixpanel import Mixpanel

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
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

from pebbles.forms import PebblePageForm

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

        pebbles = Pebble.objects.filter(creator=self.request.user)

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
        context['page'] = get_object_or_404(PebblePage, slug=kwargs['slug'])
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
        pebbles = Pebble.objects.filter(creator=self.request.user)
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
        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Page Added', {
            'pebble_id': pebble.id,
            'page_id': pebble_page.id,
            'is_live': form.cleaned_data.get('is_live', False),
            'standalone': form.cleaned_data.get('standalone', False),
        })

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
        pebbles = Pebble.objects.filter(creator=self.request.user)
        kwargs['pebbles'] = pebbles
        kwargs['selected_pebble'] = self.page.pebble.id

        return kwargs

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

        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Page Edited', {
            'pebble_id': page.pebble.id,
            'page_id': page.id,
            'is_live': form.cleaned_data.get('is_live', False),
            'standalone': form.cleaned_data.get('standalone', False),
        })

        return super(EditPageView, self).form_valid(form)


class DeleteView(NeedsLoginMixin, FormView):
    template_name = "delete_page.html"
    form_class = ComicDeleteForm

    def get_success_url(self):
        return reverse('dashview')

    def get(self, request, *args, **kwargs):
        pebbles = Pebble.objects.filter(creator=self.request.user)
        self.page = get_object_or_404(PebblePage, id=self.kwargs.get('id'), pebble__in=pebbles)

        return super(DeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pebbles = Pebble.objects.filter(creator=self.request.user)
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

        mp = Mixpanel(Setting.objects.get(key='mixpanel_key').value)
        mp.people_set(self.request.user.id, {
            'username': self.request.user.username,
            '$first_name': self.request.user.first_name,
            '$last_name': self.request.user.last_name,
            '$email': self.request.user.email,
        })
        mp.track(self.request.user.id, 'Page Deleted', {
            'page_id': self.page.id,
            'is_live': self.page.is_live,
        })

        return super(DeleteView, self).form_valid(form)


