# type: ignore  (type checking is unhappy about the mixin referencing fields it doesnt define)
import logging
from typing import Optional

from django.db import models

from wagtail_extended_search.layers.function_score import index as function_score_index
from wagtail_extended_search.layers.indexed_fields import index as indexed_fields_index
from wagtail_extended_search.layers.multi_query import index as multi_query_index
from wagtail_extended_search.types import AnalysisType

logger = logging.getLogger(__name__)


#############################
# Wagtail basic overrides
#############################


class Indexed(function_score_index.Indexed, indexed_fields_index.Indexed): ...


class ScoreFunction(function_score_index.ScoreFunction):
    configuration_model: Optional[models.Model] = None

    def get_score_name(self):
        if not self.configuration_model:
            raise AttributeError(
                "The configuration_model attribute must be set on the "
                "ScoreFunction instance to use it."
            )
        score_name = super().get_score_name()
        if self.configuration_model != self.configuration_model.get_root_index_model():
            score_name = (
                self.configuration_model._meta.app_label
                + "_"
                + self.configuration_model.__name__.lower()
                + "__"
                + score_name
            )
        return score_name


##################################
# END OF EXTRAS
##################################


#############################
# Digital Workspace code
#############################


class DWIndexedField(multi_query_index.IndexedField, indexed_fields_index.IndexedField):
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
