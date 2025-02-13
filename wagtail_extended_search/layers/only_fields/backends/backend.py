from typing import Optional

from wagtail.search.backends.elasticsearch7 import Field
from wagtail.search.index import SearchField
from wagtail.search.query import MATCH_NONE

from wagtail_extended_search import settings as search_settings
from wagtail_extended_search.layers.base.backends.backend import (
    ExtendedSearchQueryCompiler,
)
from wagtail_extended_search.layers.only_fields.query import OnlyFields
from wagtail_extended_search.layers.related_fields.index import RelatedFields


class OnlyFieldSearchQueryCompiler(ExtendedSearchQueryCompiler):
    """
    Acting as a placeholder for upstream merges to Wagtail in a separate PR to
    the ExtendedSearchQueryCompiler; this exists to support the new OnlyFields
    SearchQuery
    """

    def _remap_fields(
        self,
        fields,
        get_searchable_fields__args: Optional[tuple] = None,
        get_searchable_fields__kwargs: Optional[dict] = None,
    ):
        """
        Convert field names into index column names
        """
        if get_searchable_fields__args is None:
            get_searchable_fields__args = ()
        if get_searchable_fields__kwargs is None:
            get_searchable_fields__kwargs = {}

        if not fields:
            return super()._remap_fields(fields)

        remapped_fields = []

        searchable_fields = {
            f.field_name: f
            for f in self.get_searchable_fields(
                *get_searchable_fields__args,
                **get_searchable_fields__kwargs,
            )
        }

        for field_name in fields:
            field = searchable_fields.get(field_name)
            if field:
                field_name = self.mapping.get_field_column_name(field)
                remapped_fields.append(Field(field_name, field.boost or 1))
            else:
                # @TODO this works but ideally we'd move get_field_column_name to handle this directly
                field_name_parts = field_name.split(".")
                if field_name_parts[0] in searchable_fields:
                    parent_related_field = searchable_fields[field_name_parts[0]]
                    field_name = self.mapping.get_field_column_name(
                        parent_related_field
                    )
                    field_name_remainder = ".".join(field_name_parts[1:])
                    field_name = f"{field_name}.{field_name_remainder}"

                    # Get the field boost from the settings so it can be managed in the DB.
                    child_field = parent_related_field.get_related_field(
                        field_name_remainder
                    )
                    field_settings_key = search_settings.get_settings_field_key(
                        self.queryset.model, child_field
                    )
                    field_boost = float(
                        search_settings.wagtail_extended_search_settings["boost_parts"][
                            "fields"
                        ].get(field_settings_key, 1)
                    )
                    remapped_fields.append(Field(field_name, boost=field_boost))

        return remapped_fields

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
            return self._compile_query(MATCH_NONE, field, boost)
            # this part of the tree with an OnlyFields filter
            return self._compile_query(MATCH_NONE, field, boost)
            return self._compile_query(MATCH_NONE, field, boost)
