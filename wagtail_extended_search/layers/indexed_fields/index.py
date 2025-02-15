# type: ignore  (type checking is unhappy about the mixin referencing fields it doesnt define)
import inspect
import logging
from typing import Optional, Type

from django.apps import apps
from django.db import models
from wagtail.search import index

from wagtail_extended_search.layers.function_score import index as function_score_index
from wagtail_extended_search.layers.model_field_name import (
    index as model_field_name_index,
)
from wagtail_extended_search.layers.one_to_many import index as one_to_many_index
from wagtail_extended_search.layers.related_fields import index as related_fields_index

logger = logging.getLogger(__name__)


class ModelFieldNameMixin(related_fields_index.ModelFieldNameMixin):
    def __init__(
        self,
        field_name,
        *args,
        configuration_model=None,
        **kwargs,
    ):
        super().__init__(field_name, *args, **kwargs)
        self.configuration_model = configuration_model

    def get_definition_model(self, cls):
        if self.configuration_model:
            return self.configuration_model

        if base_cls := super().get_definition_model(cls):
            return base_cls

        # Find where it was defined by walking the inheritance tree
        base_model_field_name = self.get_base_model_field_name()
        for base_cls in inspect.getmro(cls):
            if hasattr(base_cls, base_model_field_name):
                return base_cls


class BaseField(ModelFieldNameMixin, related_fields_index.BaseField): ...


class SearchField(BaseField, related_fields_index.SearchField): ...


class AutocompleteField(BaseField, related_fields_index.AutocompleteField): ...


class FilterField(BaseField, related_fields_index.FilterField): ...


class RelatedFields(ModelFieldNameMixin, related_fields_index.RelatedFields):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def generate_fields(
        self,
        cls,
        *args,
        configuration_model: Optional[Type["Indexed"]] = None,
        **kwargs,
    ) -> list[BaseField]:
        if configuration_model:
            self.configuration_model = configuration_model

        if self.configuration_model:
            if "configuration_model" not in self.related_fields_kwargs:
                self.related_fields_kwargs["configuration_model"] = (
                    self.configuration_model
                )

        return super().generate_fields(cls, *args, **kwargs)


class IndexedField(related_fields_index.IndexedField):
    search_field_class = SearchField
    autocomplete_field_class = AutocompleteField
    filter_field_class = FilterField

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.configuration_model = None

    def generate_fields(
        self,
        cls,
        *args,
        configuration_model: Optional[Type["Indexed"]] = None,
        **kwargs,
    ):
        if configuration_model:
            self.configuration_model = configuration_model

        if self.configuration_model:
            if "configuration_model" not in self.search_kwargs:
                self.search_kwargs["configuration_model"] = self.configuration_model
            if "configuration_model" not in self.autocomplete_kwargs:
                self.autocomplete_kwargs["configuration_model"] = (
                    self.configuration_model
                )
            if "configuration_model" not in self.filter_kwargs:
                self.filter_kwargs["configuration_model"] = self.configuration_model

        return super().generate_fields(cls, *args, **kwargs)


def class_is_indexed(cls):
    """
    Overrides wagtail.search.index.class_is_indexed
    """
    # TODO: Need to create a method for marking a class that inherits from
    # Indexed as not being part of the index. This was previously achieved
    # by setting search_fields to a falsy value.
    return (
        issubclass(cls, index.Indexed)
        and issubclass(cls, models.Model)
        and not cls._meta.abstract
        # and cls.search_fields
    )


class Indexed(
    related_fields_index.Indexed,
    model_field_name_index.Indexed,
    # index.Indexed,
):
    indexed_fields = []

    @classmethod
    def get_indexed_fields(cls, as_dict: bool = False):
        processed_index_fields = {}
        class_mro = list(inspect.getmro(cls))
        class_mro.reverse()
        for model_class in class_mro:
            if not class_is_indexed(model_class):
                continue
            if not issubclass(model_class, Indexed):
                continue
            if not model_class.has_unique_index_fields():
                continue

            model_field_names = []

            for f in model_class.indexed_fields:
                f.configuration_model = model_class
                if isinstance(f, model_field_name_index.BaseField):
                    if f.model_field_name not in model_field_names:
                        if f.model_field_name not in processed_index_fields:
                            processed_index_fields[f.model_field_name] = []
                        model_field_names.append(f.model_field_name)
                    processed_index_fields[f.model_field_name].append(f)
                else:
                    if f.field_name not in model_field_names:
                        if f.field_name not in processed_index_fields:
                            processed_index_fields[f.field_name] = []
                        model_field_names.append(f.field_name)
                    processed_index_fields[f.field_name].append(f)

        if as_dict:
            return processed_index_fields
        return [f for v in processed_index_fields.values() for f in v]

    @classmethod
    def generate_from_indexed_fields(cls):
        processed_index_fields = cls.get_indexed_fields(as_dict=True)

        # @TODO doesn't support SearchFields in indexed_fields (for now ?)
        for k, v in processed_index_fields.items():
            processed_index_fields[k] = []
            for f in v:
                processed_index_fields[k] += f.generate_fields(cls)
        return processed_index_fields

    processed_search_fields = {}

    @classmethod
    def get_search_fields(cls, ignore_cache=False):
        if cls not in cls.processed_search_fields:
            cls.processed_search_fields[cls] = []
        if cls.processed_search_fields[cls] and not ignore_cache:
            return cls.processed_search_fields[cls]

        search_fields = super().get_search_fields()
        processed_fields = {}

        for f in search_fields:
            pfn_key = getattr(f, "model_field_name", f.field_name)
            if pfn_key not in processed_fields:
                processed_fields[pfn_key] = []
            processed_fields[pfn_key].append(f)

        processed_fields |= cls.generate_from_indexed_fields()

        processed_search_fields = [f for v in processed_fields.values() for f in v]
        cls.processed_search_fields[cls] = processed_search_fields
        return processed_search_fields

    @classmethod
    def has_unique_index_fields(cls):
        # @TODO [DWPF-1066] this doesn't account for a diverging MRO
        parent_model = cls.indexed_get_parent()
        parent_indexed_fields = getattr(parent_model, "indexed_fields", [])
        return cls.indexed_fields != parent_indexed_fields

    @classmethod
    def get_root_index_model(cls):
        class_mro = list(inspect.getmro(cls))
        class_mro.reverse()
        for model in class_mro:
            if model != Indexed and issubclass(model, Indexed):
                return model
        return cls


def get_indexed_models() -> list[Type[Indexed]]:
    """
    Overrides wagtail.search.index.get_indexed_models
    """
    # TODO: Need to create a method for marking a class that inherits from
    # Indexed as not being part of the index. This was previously achieved
    # by setting search_fields to a falsy value.
    return [
        model
        for model in apps.get_models()
        if issubclass(model, index.Indexed) and not model._meta.abstract
        # and model.search_fields
    ]
