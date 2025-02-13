from typing import Union

from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchQueryCompiler,
    Field,
)
from wagtail.search.query import Fuzzy, MatchAll, Not, Phrase, PlainText


class ExtendedSearchQueryCompiler(Elasticsearch7SearchQueryCompiler):
    """
    Acting as a placeholder for upstream merges to Wagtail in a PR; this class
    doesn't change any behaviour but instead assigns responsibility for
    particular aspects to smaller methods to make it easier to override. In the
    PR maybe worth referencing https://github.com/wagtail/wagtail/issues/5422
    """

    def __init__(self, *args, **kwargs):
        """Remove this when we get wagtail PR 11018 merged & deployed"""
        super().__init__(*args, **kwargs)
        self.remapped_fields = self.remapped_fields or [
            Field(self.mapping.all_field_name)
        ]

    def get_boosted_fields(self, fields):
        """
        This is needed because we are backporting to strings WAY TOO EARLY
        """
        boostable_fields = [self.to_field(f) for f in fields]

        return super().get_boosted_fields(boostable_fields)

    def _join_and_compile_queries(self, query, fields, boost=1.0):
        """
        Handle a generalised situation of one or more queries that need
        compilation and potentially joining as siblings. If more than one field
        then compile a query for each field then combine with disjunction
        max (or operator which takes the max score out of each of the
        field queries)
        """
        if len(fields) == 1:
            return self._compile_query(query, fields[0], boost)
        else:
            field_queries = []
            for field in fields:
                field_queries.append(self._compile_query(query, field, boost))

            return {"dis_max": {"queries": field_queries}}

    def to_string(self, field: Union[str, Field]) -> str:
        if isinstance(field, Field):
            return field.field_name
        return field

    def to_field(self, field: Union[str, Field]) -> Field:
        if isinstance(field, Field):
            return field
        return Field(field)

    def _compile_plaintext_query(self, query, fields, boost=1.0):
        return super()._compile_plaintext_query(query, fields, boost)

    def _compile_fuzzy_query(self, query, fields):
        return super()._compile_fuzzy_query(query, fields)

    def _compile_phrase_query(self, query, fields):
        return super()._compile_phrase_query(query, fields)

    def get_inner_query(self):
        """
        This is a brittle override of the Elasticsearch7SearchQueryCompiler.
        get_inner_query, acting as a stand in for getting these changes merged
        upstream. It exists in order to break out the _join_and_compile_queries
        method
        """
        fields = [self.to_field(f) for f in self.remapped_fields]

        if len(fields) == 0:
            # No fields. Return a query that'll match nothing
            return {"bool": {"mustNot": {"match_all": {}}}}

        # Handle MatchAll and PlainText separately as they were supported
        # before "search query classes" was implemented and we'd like to
        # keep the query the same as before
        if isinstance(self.query, MatchAll):
            return {"match_all": {}}

        elif isinstance(self.query, PlainText):
            return self._compile_plaintext_query(self.query, fields)

        elif isinstance(self.query, Phrase):
            return self._compile_phrase_query(self.query, fields)

        elif isinstance(self.query, Fuzzy):
            return self._compile_fuzzy_query(self.query, fields)

        elif isinstance(self.query, Not):
            return {
                "bool": {
                    "mustNot": [
                        self._compile_query(self.query.subquery, field)
                        for field in fields
                    ]
                }
            }

        else:
            return self._join_and_compile_queries(self.query, fields)
