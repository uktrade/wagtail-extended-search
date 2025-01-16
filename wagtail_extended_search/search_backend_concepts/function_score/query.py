from typing import Optional

from django.db import models
from wagtail.search.query import SearchQuery


class FunctionScore(SearchQuery):
    remapped_fields = None

    def __init__(
        self,
        model_class: models.Model,
        subquery: SearchQuery,
        function_name: str,
        function_params: dict,
        field: Optional[str] = None,
    ):
        if not isinstance(subquery, SearchQuery):
            raise TypeError("The `subquery` parameter must be of type SearchQuery")

        if not isinstance(function_name, str):
            raise TypeError("The `function_name` parameter must be a string")

        if not isinstance(function_params, dict):
            raise TypeError("The `function_params` parameter must be a dict")

        if field is not None and not isinstance(field, str):
            raise TypeError("The `field` parameter must be a string")

        self.model_class = model_class
        self.subquery = subquery
        self.function_name = function_name
        self.function_params = function_params
        self.field = field

    def __repr__(self):
        return "<FunctionScore {} function_name='{}' function_params='{}' field='{}' >".format(
            repr(self.subquery),
            self.function_name,
            self.function_params,
            self.field,
        )
