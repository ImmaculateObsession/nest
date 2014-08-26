import feedparser
from django.views.generic import TemplateView



class ReaderView(TemplateView):
    template_name = "reader/reader.html"

    def get_context_data(self, **kwargs):
        context = super(ReaderView, self).get_context_data(**kwargs)

        feed = feedparser.parse(
            'http://www.captainquail.com/feed/',
            agent='Inkpebble/1.0 +http://www.inkpebble.com/',
        )

        context['entries'] = feed.entries

        return context
