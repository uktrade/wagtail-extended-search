from django import forms
from django.contrib import admin

from wagtail_extended_search import settings
from wagtail_extended_search.models import Setting


class SettingAdminForm(forms.ModelForm):
    key = forms.ChoiceField(choices=[])

    class Meta:
        model = Setting
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["key"].choices = [
            (k, k) for k in settings.wagtail_extended_search_settings.all_keys
        ]


class SettingAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]
    form = SettingAdminForm


# FIXME: we need to register the admin in a different manner:
# admin_site.register(Setting, SettingAdmin)
