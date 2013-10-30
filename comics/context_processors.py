from django.conf import settings

def setting_injector(request):
    return {
        'MIXPANEL_KEY': settings.MIXPANEL_KEY,
    }