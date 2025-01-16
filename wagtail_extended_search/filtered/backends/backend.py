from wagtail.search.backends.elasticsearch7 import Elasticsearch7Mapping

from wagtail_extended_search.base.backends.backend import ExtendedSearchQueryCompiler
from wagtail_extended_search.filtered.query import Filtered


class FilteredSearchMapping(Elasticsearch7Mapping):
    def get_field_column_name(self, field):
        if isinstance(field, str) and field == "content_type":
            return "content_type"
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
        compiled_filters = [self._process_lookup(*f) for f in query.filters]
        if len(compiled_filters) == 1:
            compiled_filters = compiled_filters[0]

        return {
            "bool": {
                "must": self._join_and_compile_queries(query.subquery, fields, boost),
                "filter": compiled_filters,
            }
        }

    def _process_lookup(self, field, lookup, value):
        # @TODO not pretty given get_field_column_name is already overridden
        if isinstance(field, str):
            column_name = field
        else:
            column_name = self.mapping.get_field_column_name(field)

        if lookup == "contains":
            return {"match": {column_name: value}}

        if lookup == "excludes":
            return {"bool": {"mustNot": {"terms": {column_name: value}}}}

        return super()._process_lookup(field, lookup, value)
