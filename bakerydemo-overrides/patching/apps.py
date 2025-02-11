from django.apps import AppConfig


class PatchingConfig(AppConfig):
    name = "overrides.patching"
    verbose_name = "Patching"

    def ready(self):
        from bakerydemo.blog.models import BlogPage
        from wagtail.models import Page
        from wagtail.search.index import Indexed

        from wagtail_extended_search.index import DWIndexedField
        from wagtail_extended_search.index import Indexed as WESIndexed

        # BlogPage should inherit from Page and Indexed
        print("Patching Page")
        if Indexed in Page.__bases__:
            Page.__bases__ = tuple(base for base in Page.__bases__ if base != Indexed)
        if WESIndexed not in Page.__bases__:
            Page.__bases__ += (WESIndexed,)

        Page.indexed_fields = [
            DWIndexedField("title", search=True),
        ]
        BlogPage.indexed_fields = [
            DWIndexedField("title", search=True, keyword=True),
        ]
