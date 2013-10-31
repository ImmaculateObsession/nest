from petroglyphs.models import Setting

def setting_injector(request):

    context_dict = {}
    for setting in Setting.objects.filter(export_to_template=True):
        context_dict[setting.key.upper()] = str(setting.value)

    return context_dict
