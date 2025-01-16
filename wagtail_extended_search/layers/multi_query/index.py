from wagtail_extended_search.layers.one_to_many.index import IndexedField
from wagtail_extended_search.types import AnalysisType


class MultiQueryIndexedField(IndexedField):
    def __init__(
        self,
        *args,
        tokenized: bool = False,
        explicit: bool = False,
        fuzzy: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tokenized = tokenized
        self.explicit = explicit
        self.fuzzy = fuzzy

        if tokenized or explicit or fuzzy:
            self.search = True

    def get_search_analyzers(self):
        analyzers = set()
        if self.tokenized:
            analyzers.add(AnalysisType.TOKENIZED)
        if self.explicit:
            analyzers.add(AnalysisType.EXPLICIT)
        if not analyzers and self.search:
            analyzers.add(AnalysisType.TOKENIZED)
        return analyzers

    def get_autocomplete_analyzers(self):
        analyzers = set()
        if self.autocomplete:
            analyzers.add(AnalysisType.NGRAM)
        return analyzers

    def get_filter_analyzers(self):
        analyzers = set()
        if self.filter:
            analyzers.add(AnalysisType.FILTER)
        return analyzers

    def get_search_field_variants(self, cls):
        from wagtail_extended_search import settings as search_settings
        from wagtail_extended_search.index import get_indexed_field_name

        field_settings_key = search_settings.get_settings_field_key(cls, self)
        field_boosts = search_settings.wagtail_extended_search_settings["boost_parts"][
            "fields"
        ]
        field_boost = field_boosts.get(field_settings_key)

        search_field_variants = []

        for analyzer in self.get_search_analyzers():
            variant_args = (get_indexed_field_name(self.model_field_name, analyzer),)
            variant_kwargs = {
                "es_extra": {
                    "analyzer": search_settings.wagtail_extended_search_settings[
                        "analyzers"
                    ][analyzer.value]["es_analyzer"]
                },
            }

            if field_boost is not None:
                variant_kwargs["boost"] = float(field_boost)

            search_field_variants.append((variant_args, variant_kwargs))

        return search_field_variants
