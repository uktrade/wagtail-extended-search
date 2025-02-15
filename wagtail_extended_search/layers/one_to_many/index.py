from typing import Optional

from wagtail_extended_search.layers.model_field_name.index import (
    AutocompleteField,
    BaseField,
    FilterField,
    SearchField,
)


class IndexedField(BaseField):
    search_field_class = SearchField
    autocomplete_field_class = AutocompleteField
    filter_field_class = FilterField

    def __init__(
        self,
        *args,
        boost: float = 1.0,
        proximity: bool = False,
        search: bool = False,
        search_kwargs: Optional[dict] = None,
        autocomplete: bool = False,
        autocomplete_kwargs: Optional[dict] = None,
        filter: bool = False,
        filter_kwargs: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.boost = boost
        self.proximity = proximity
        self.search = search
        self.search_kwargs = search_kwargs or {}
        self.autocomplete = autocomplete
        self.autocomplete_kwargs = autocomplete_kwargs or {}
        self.filter = filter
        self.filter_kwargs = filter_kwargs or {}

    def generate_fields(
        self,
        cls,
    ) -> list[BaseField]:
        generated_fields = []

        if self.search:
            generated_fields += self.generate_search_fields(cls)
        if self.autocomplete:
            generated_fields += self.generate_autocomplete_fields(cls)
        if self.filter:
            generated_fields += self.generate_filter_fields(cls)

        return generated_fields

    def generate_search_fields(self, cls) -> list[SearchField]:
        generated_fields = []
        for variant_args, variant_kwargs in self.get_search_field_variants(cls):
            kwargs = self.search_kwargs.copy()
            kwargs.update(variant_kwargs)

            if "model_field_name" not in kwargs:
                kwargs["model_field_name"] = self.model_field_name

            if "boost" not in kwargs:
                kwargs["boost"] = self.boost

            generated_fields.append(self.search_field_class(*variant_args, **kwargs))
        return generated_fields

    def generate_autocomplete_fields(self, cls) -> list[AutocompleteField]:
        generated_fields = []
        for variant_args, variant_kwargs in self.get_autocomplete_field_variants(cls):
            kwargs = self.autocomplete_kwargs.copy()
            kwargs.update(variant_kwargs)

            if "model_field_name" not in kwargs:
                kwargs["model_field_name"] = self.model_field_name

            generated_fields.append(
                self.autocomplete_field_class(*variant_args, **kwargs)
            )
        return generated_fields

    def generate_filter_fields(self, cls) -> list[FilterField]:
        generated_fields = []
        for variant_args, variant_kwargs in self.get_filter_field_variants(cls):
            kwargs = self.filter_kwargs.copy()
            kwargs.update(variant_kwargs)

            if "model_field_name" not in kwargs:
                kwargs["model_field_name"] = self.model_field_name

            generated_fields.append(self.filter_field_class(*variant_args, **kwargs))
        return generated_fields

    def get_search_field_variants(self, cls) -> list[tuple[tuple, dict]]:
        """
        Override this in order to customise the args and kwargs passed to SearchField on creation or to create more than one, each with different kwargs
        """
        if self.search:
            return [
                ((self.model_field_name,), {}),
            ]
        return []

    def get_autocomplete_field_variants(self, cls) -> list[tuple[tuple, dict]]:
        """
        Override this in order to customise the args and kwargs passed to AutocompleteField on creation or to create more than one, each with different kwargs
        """
        if self.autocomplete:
            return [
                ((self.model_field_name,), {}),
            ]
        return []

    def get_filter_field_variants(self, cls) -> list[tuple[tuple, dict]]:
        """
        Override this in order to customise the args and kwargs passed to FilterField on creation or to create more than one, each with different kwargs
        """
        if self.filter:
            return [
                ((self.model_field_name,), {}),
            ]
        return []
