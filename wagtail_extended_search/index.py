# type: ignore  (type checking is unhappy about the mixin referencing fields it doesnt define)
import inspect
import logging
from typing import Type

from django.apps import apps
from django.core import checks
from django.db import models
from wagtail.search import index

from wagtail_extended_search.layers.function_score.index import ScoreFunction
from wagtail_extended_search.layers.model_field_name.index import BaseField
from wagtail_extended_search.layers.multi_query.index import MultiQueryIndexedField
from wagtail_extended_search.types import AnalysisType

logger = logging.getLogger(__name__)


#############################
# Wagtail basic overrides
#############################


class Indexed(index.Indexed):
    search_fields = []

    @classmethod
    def _check_search_fields(cls, **kwargs):
        errors = []
        for field in cls.get_search_fields():
            message = "{model}.search_fields contains non-existent field '{name}'"
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
                if isinstance(f, BaseField):
                    if f.model_field_name not in model_field_names:
                        if f.model_field_name not in processed_index_fields:
                            processed_index_fields[f.model_field_name] = []
                        model_field_names.append(f.model_field_name)
                    processed_index_fields[f.model_field_name].append(f)
                    print(f"ADDED {f.model_field_name} for {model_class}")
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
    def get_score_functions(cls):
        return [
            field
            for field in cls.get_indexed_fields()
            if isinstance(field, ScoreFunction)
        ]

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
    return [
        model
        for model in apps.get_models()
        if issubclass(model, index.Indexed) and not model._meta.abstract
        # and model.search_fields
    ]


def class_is_indexed(cls):
    """
    Overrides wagtail.search.index.class_is_indexed
    """
    return (
        issubclass(cls, index.Indexed)
        and issubclass(cls, models.Model)
        and not cls._meta.abstract
        # and cls.search_fields
    )


##################################
# END OF EXTRAS
##################################


#############################
# Digital Workspace code
#############################


class DWIndexedField(MultiQueryIndexedField):
    def __init__(
        self,
        *args,
        keyword: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.keyword = keyword

        if keyword:
            self.search = True

    def get_search_analyzers(self):
        analyzers = super().get_search_analyzers()
        if self.keyword:
            analyzers.add(AnalysisType.KEYWORD)
        return analyzers


def get_indexed_field_name(
    model_field_name: str,
    analyzer: AnalysisType,
):
    from wagtail_extended_search.settings import wagtail_extended_search_settings

    field_name_suffix = (
        wagtail_extended_search_settings["analyzers"][analyzer.value][
            "index_fieldname_suffix"
        ]
        or ""
    )
    return f"{model_field_name}{field_name_suffix}"
