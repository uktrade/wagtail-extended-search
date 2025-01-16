from wagtail.search.index import SearchField
from wagtail.search.query import MATCH_NONE

from wagtail_extended_search.base.backends.backend import ExtendedSearchQueryCompiler
from wagtail_extended_search.index import RelatedFields
from wagtail_extended_search.only_fields.query import OnlyFields


class OnlyFieldSearchQueryCompiler(ExtendedSearchQueryCompiler):
    """
    Acting as a placeholder for upstream merges to Wagtail in a separate PR to
    the ExtendedSearchQueryCompiler; this exists to support the new OnlyFields
    SearchQuery
    """

    def get_searchable_fields(self, *args, only_model, **kwargs):
        if not only_model:
            return super().get_searchable_fields()
        return [
            f
            for f in only_model.get_search_fields(ignore_cache=True)
            if isinstance(f, SearchField) or isinstance(f, RelatedFields)
        ]

    def _compile_query(self, query, field, boost=1.0):
        """
        Override the parent method to handle specifics of the OnlyFields
        SearchQuery.
        """
        if not isinstance(query, OnlyFields):
            return super()._compile_query(query, field, boost)

        # FIXME: OnlyFields logic is breaking search
        return super()._compile_query(query.subquery, field, boost)

        remapped_fields = self._remap_fields(
            query.fields,
            get_searchable_fields__kwargs={
                "only_model": query.only_model,
            },
        )

        if isinstance(field, list) and len(field) == 1:
            field = field[0]

        if field.field_name == self.mapping.all_field_name and remapped_fields:
            # We are using the "_all_text" field proxy (i.e. the search()
            # method was called without the fields kwarg), but now we want to
            # limit the downstream fields compiled to those explicitly defined
            # in the OnlyFields query
            return self._join_and_compile_queries(
                query.subquery, remapped_fields, boost
            )

        elif field.field_name in query.fields:
            # Fields were defined explicitly upstream, and we are dealing with
            # one that's in the OnlyFields filter
            return self._compile_query(query.subquery, field, boost)

        else:
            # Exclude this field from any further downstream compilation: it
            # was defined in the search() method but has been excluded from
            # this part of the tree with an OnlyFields filter
            return self._compile_query(MATCH_NONE, field, boost)
