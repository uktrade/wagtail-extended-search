from wagtail.search.index import SearchField

from wagtail_extended_search.base.backends.backend import ExtendedSearchQueryCompiler
from wagtail_extended_search.index import RelatedFields
from wagtail_extended_search.nested.query import Nested


class NestedSearchQueryCompiler(ExtendedSearchQueryCompiler):
    def get_searchable_fields(self, *args, **kwargs):
        return [
            f
            for f in self.queryset.model.get_search_fields()
            if isinstance(f, SearchField) or isinstance(f, RelatedFields)
        ]

    def _compile_query(self, query, field, boost=1.0):
        if isinstance(query, Nested):
            return self._compile_nested_query(query, [field], boost)
        return super()._compile_query(query, field, boost)

    def _compile_nested_query(self, query, fields, boost=1.0):
        """
        Add OS DSL elements to support Nested fields
        """
        return {
            "nested": {
                "path": query.path,
                "query": self._join_and_compile_queries(query.subquery, fields, boost),
            }
        }
