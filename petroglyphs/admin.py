from django.contrib import admin
from petroglyphs.models import Setting


class SettingAdmin(admin.ModelAdmin):

    def queryset(self, request):
        return Setting.objects.filter(show_in_admin=True)

admin.site.register(Setting, SettingAdmin)