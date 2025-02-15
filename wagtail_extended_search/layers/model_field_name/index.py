from django.core import checks
from wagtail.search import index


class ModelFieldNameMixin:
    def __init__(
        self,
        field_name,
        *args,
        model_field_name=None,
        **kwargs,
    ):
        super().__init__(field_name, *args, **kwargs)
        self.model_field_name = model_field_name or field_name


class BaseField(ModelFieldNameMixin, index.BaseField): ...


class SearchField(index.SearchField, BaseField, index.BaseField): ...


class AutocompleteField(index.AutocompleteField, BaseField, index.BaseField): ...


class FilterField(index.FilterField, BaseField, index.BaseField): ...


class Indexed(index.Indexed):
    @classmethod
    def _check_search_fields(cls, **kwargs):
        errors = []
        for field in cls.get_search_fields():
            message = "{model}.search_fields contains non-existent field '{name}'"
            # Note: When this is moved into Wagtail Core, we just need to check
            # field.model_field_name as that will default back to field_name.
            if not cls._has_field(field.field_name) and not cls._has_field(
                field.model_field_name
            ):
                errors.append(
                    checks.Warning(
                        message.format(model=cls.__name__, name=field.field_name),
                        obj=cls,
                        id="wagtailsearch.W004",
                    )
                )
        return errors

    @classmethod
    def get_searchable_search_fields(cls):
        return [
            field for field in cls.get_search_fields() if isinstance(field, SearchField)
        ]

    @classmethod
    def get_autocomplete_search_fields(cls):
        return [
            field
            for field in cls.get_search_fields()
            if isinstance(field, AutocompleteField)
        ]

    @classmethod
    def get_filterable_search_fields(cls):
        return [
            field for field in cls.get_search_fields() if isinstance(field, FilterField)
        ]
