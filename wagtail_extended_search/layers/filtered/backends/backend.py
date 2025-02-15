from django.db import DEFAULT_DB_ALIAS
from django.db.models.sql import Query
from django.db.models.sql.constants import MULTI
from wagtail.search.backends.elasticsearch7 import Elasticsearch7Mapping

from wagtail_extended_search.layers.base.backends.backend import (
    ExtendedSearchQueryCompiler,
)
from wagtail_extended_search.layers.filtered.query import Filtered


class FilteredSearchMapping(Elasticsearch7Mapping):
    def get_field_column_name(self, field):
        if isinstance(field, str) and field == "content_type_id":
            return "content_type_id"
        return super().get_field_column_name(field)


class FilteredSearchQueryCompiler(ExtendedSearchQueryCompiler):
    def _compile_query(self, query, field, boost=1.0):
        if isinstance(query, Filtered):
            return self._compile_filtered_query(query, [field], boost)
        return super()._compile_query(query, field, boost)

    def _compile_filtered_query(self, query, fields, boost=1.0):
        """
        Add OS DSL elements to support Filtered fields
        """
        processed_filters = [self._process_filter(*f) for f in query.filters]

        return {
            "bool": {
                "must": self._join_and_compile_queries(query.subquery, fields, boost),
                "filter": self._connect_filters(processed_filters, "AND", False),
            }
        }

    def _process_lookup(self, field, lookup, value):
        # @TODO not pretty given get_field_column_name is already overridden
        # if isinstance(field, str):
        #     column_name = field
        # else:
        # column_name = self.mapping.get_field_column_name(field)

        column_name = self.mapping.get_field_column_name(field)

        if lookup == "notin":
            if isinstance(value, Query):
                db_alias = self.queryset._db or DEFAULT_DB_ALIAS
                resultset = value.get_compiler(db_alias).execute_sql(result_type=MULTI)
                value = [row[0] for chunk in resultset for row in chunk]

            elif not isinstance(value, list):
                value = list(value)

            in_query = {
                "terms": {
                    column_name: value,
                }
            }

            return {"bool": {"mustNot": in_query}}

        return super()._process_lookup(field, lookup, value)
