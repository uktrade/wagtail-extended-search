from typing import TYPE_CHECKING, Optional, Type

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel, RelatedField
from modelcluster.fields import ParentalManyToManyField
from wagtail.search import index

from wagtail_extended_search.layers.model_field_name.index import ModelFieldNameMixin

if TYPE_CHECKING:
    from wagtail_extended_search.index import Indexed
    from wagtail_extended_search.layers.model_field_name.index import BaseField
    from wagtail_extended_search.layers.one_to_many.index import IndexedField


class RelatedFields(ModelFieldNameMixin, index.RelatedFields):
    def select_on_queryset(self, queryset):
        """
        This method runs either prefetch_related or select_related on the queryset
        to improve indexing speed of the relation.

        It decides which method to call based on the number of related objects:
         - single (eg ForeignKey, OneToOne), it runs select_related
         - multiple (eg ManyToMany, reverse ForeignKey) it runs prefetch_related
        """
        try:
            field = self.get_field(queryset.model)
        except FieldDoesNotExist:
            return queryset

        if isinstance(field, RelatedField) and not isinstance(
            field, ParentalManyToManyField
        ):
            if field.many_to_one or field.one_to_one:
                queryset = queryset.select_related(self.model_field_name)
            elif field.one_to_many or field.many_to_many:
                queryset = queryset.prefetch_related(self.model_field_name)

        elif isinstance(field, ForeignObjectRel):
            # Reverse relation
            if isinstance(field, OneToOneRel):
                # select_related for reverse OneToOneField
                queryset = queryset.select_related(self.model_field_name)
            else:
                # prefetch_related for anything else (reverse ForeignKey/ManyToManyField)
                queryset = queryset.prefetch_related(self.model_field_name)

        return queryset

    def generate_fields(
        self,
        cls,
        parent_field: Optional["BaseField"] = None,
        configuration_model: Optional[Type["Indexed"]] = None,
    ) -> list["BaseField"]:
        if parent_field:
            self.is_relation_of(parent_field)
        if configuration_model:
            self.configuration_model = configuration_model

        generated_fields = []
        for field in self.fields:
            if isinstance(field, IndexedField) or isinstance(field, RelatedFields):
                generated_fields += field.generate_fields(
                    cls,
                    parent_field=self,
                    configuration_model=self.configuration_model,
                )
            else:
                # is_relation_of won't work on Wagtail native fields
                field.is_relation_of(self)
                generated_fields.append(field)

        return [
            RelatedFields(
                field_name=self.field_name,
                model_field_name=self.model_field_name,
                parent_field=self.parent_field,
                configuration_model=self.configuration_model,
                fields=generated_fields,
            )
        ]

    def get_related_field(self, field_name):
        """
        Return the "child most" related field for a given field name.

        Example:
            `author.books.title` would return the title SearchField
        """
        for f in self.fields:
            if f.field_name == field_name:
                if isinstance(f, RelatedFields):
                    new_field_name = field_name.split(".")[1:]
                    return f.get_related_field(new_field_name)
                return f

    def __repr__(self) -> str:
        return f"<RelatedFields {self.field_name} fields={sorted([str(f) for f in self.fields])}>"
