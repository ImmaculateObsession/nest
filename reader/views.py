from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from reader.models import Item, Reader


class ReaderView(TemplateView):
    template_name = "reader/item.html"

    def get_context_data(self, **kwargs):
        context = super(ReaderView, self).get_context_data(**kwargs)

        subs = Reader.objects.filter(reader=self.request.user)

        if subs:
            try:
                current = subs[0].get_last_read()
                subs[0].last_read = current
                subs[0].save()
                left, right = current.get_siblings()
            except IndexError:
                current, left, right = None

            try:
                down = subs[1].get_last_read()
            except IndexError:
                down = None

            context.update({
                'object': current,
                'left': left,
                'right': right,
                'down': down,
            })

        return context


class ItemView(DetailView):
    model = Item
    template_name = "reader/item.html"

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        subs = Reader.objects.filter(reader=self.request.user)
        item = context['object']
        index = [i for i, x in enumerate(subs) if x.collection==item.collection][0]
        if index > 0:
            try:
                up = subs[index-1].get_last_read()
            except IndexError:
                up = None
        else:
            up = None

        try:
            down = subs[index+1].get_last_read()
        except IndexError:
            down = None

        left, right = item.get_siblings()

        subs[index].last_read = item
        subs[index].save()

        context.update({
            'up': up,
            'down': down,
            'left': left,
            'right': right,
        })

        return context
