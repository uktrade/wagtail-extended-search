from typing import TYPE_CHECKING, Optional, Type

from wagtail_extended_search.layers.model_field_name.index import (
    AutocompleteField,
    BaseField,
    FilterField,
    SearchField,
)

if TYPE_CHECKING:
    from wagtail_extended_search.index import Indexed


class IndexedField(BaseField):
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
        parent_field: Optional[BaseField] = None,
        configuration_model: Optional[Type["Indexed"]] = None,
    ) -> list[BaseField]:
        if parent_field:
            self.is_relation_of(parent_field)
        if configuration_model:
            self.configuration_model = configuration_model

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

            if "parent_field" not in kwargs:
                kwargs["parent_field"] = self.parent_field

            if "configuration_model" not in kwargs:
                kwargs["configuration_model"] = self.configuration_model

            generated_fields.append(SearchField(*variant_args, **kwargs))
        return generated_fields

    def generate_autocomplete_fields(self, cls) -> list[AutocompleteField]:
        generated_fields = []
        for variant_args, variant_kwargs in self.get_autocomplete_field_variants(cls):
            kwargs = self.autocomplete_kwargs.copy()
            kwargs.update(variant_kwargs)

            if "model_field_name" not in kwargs:
                kwargs["model_field_name"] = self.model_field_name

            if "parent_field" not in kwargs:
                kwargs["parent_field"] = self.parent_field

            if "configuration_model" not in kwargs:
                kwargs["configuration_model"] = self.configuration_model

            generated_fields.append(AutocompleteField(*variant_args, **kwargs))
        return generated_fields

    def generate_filter_fields(self, cls) -> list[FilterField]:
        generated_fields = []
        for variant_args, variant_kwargs in self.get_filter_field_variants(cls):
            kwargs = self.filter_kwargs.copy()
            kwargs.update(variant_kwargs)

            if "model_field_name" not in kwargs:
                kwargs["model_field_name"] = self.model_field_name

            if "parent_field" not in kwargs:
                kwargs["parent_field"] = self.parent_field

            if "configuration_model" not in kwargs:
                kwargs["configuration_model"] = self.configuration_model

            generated_fields.append(FilterField(*variant_args, **kwargs))
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
