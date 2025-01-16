from django.db import models
from wagtail.search.query import SearchQuery


class OnlyFields(SearchQuery):
    remapped_fields = None

    def __init__(
        self, subquery: SearchQuery, fields: list[str], only_model: models.Model
    ) -> None:
        if not isinstance(subquery, SearchQuery):
            raise TypeError("The `subquery` parameter must be of type SearchQuery")

        if not isinstance(fields, list):
            raise TypeError("The `fields` parameter must be a list")

        self.subquery = subquery
        self.only_model = only_model
        self.fields = fields

    def __repr__(self) -> str:
        return "<OnlyFields {} fields=[{}]>".format(
            repr(self.subquery),
            ", ".join([f"'{f}'" for f in self.fields]),
        )
