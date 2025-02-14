# type: ignore  (type checking is unhappy about the mixin referencing fields it doesnt define)
import logging
from typing import Type

from django.apps import apps
from wagtail.search import index

from wagtail_extended_search.layers.indexed_fields import index as indexed_fields_index
from wagtail_extended_search.layers.multi_query.index import MultiQueryIndexedField
from wagtail_extended_search.types import AnalysisType

logger = logging.getLogger(__name__)


#############################
# Wagtail basic overrides
#############################


class Indexed(indexed_fields_index.Indexed): ...


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
