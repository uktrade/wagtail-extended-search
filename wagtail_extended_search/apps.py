from django.apps import AppConfig
from django.conf import settings as django_settings


class WagtailExtendedSearchConfig(AppConfig):
    name = "wagtail_extended_search"

    def ready(self):
        import wagtail_extended_search.signals  # noqa
        from wagtail_extended_search import query_builder, settings
        from wagtail_extended_search.index import get_indexed_models

        settings.settings_singleton.initialise_field_dict()
        settings.settings_singleton.initialise_env_dict()
        # FIXME: `APP_ENV` is not a general Django/Wagtail setting, this needs rethinking!
        # if django_settings.APP_ENV not in ["test", "build"]:
        #     settings.settings_singleton.initialise_db_dict()
        settings.wagtail_extended_search_settings = (
            settings.settings_singleton.to_dict()
        )
        query_builder.wagtail_extended_search_settings = (
            settings.wagtail_extended_search_settings
        )

        for model_class in get_indexed_models():
            if hasattr(model_class, "indexed_fields") and model_class.indexed_fields:
                query_builder.CustomQueryBuilder.build_search_query(model_class, True)
