import inspect
from typing import TYPE_CHECKING, Optional, Type

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel, RelatedField
from modelcluster.fields import ParentalManyToManyField
from wagtail.search import index

from wagtail_extended_search.layers.model_field_name import (
    index as model_field_name_index,
)
from wagtail_extended_search.layers.one_to_many import index as one_to_many_index

if TYPE_CHECKING:
    from wagtail_extended_search.index import Indexed


class ModelFieldNameMixin(model_field_name_index.ModelFieldNameMixin):
    def __init__(
        self,
        field_name,
        *args,
        parent_field=None,
        **kwargs,
    ):
        super().__init__(field_name, *args, **kwargs)
        self.parent_field = parent_field

    def is_relation_of(self, field):
        """
        Allows post-init definiton of a field Relation (used for field name generation)
        """
        self.parent_field = field

    def get_base_field(self):
        """
        Returns the field on the indexed model that owns the relationship, or the field if no relation exists
        """
        if self.parent_field:
            return self.parent_field.get_base_field()
        return self

    def get_base_model_field_name(self):
        """
        Returns the model field name of the field on the model that owns the relationship, if any, or the field name if not.

        Examples (Book is the indexed model)
        Book -> Author -> First Name: this would return author
        Book -> Author -> Publisher -> Name: this would return author
        """
        return self.get_base_field().model_field_name

    def get_full_model_field_name(self):
        """
        Returns the full name of the field based on the relations in place, starting at the base indexed model.

        Examples (Book is the indexed model)
        Book -> Author -> First Name: this would return author.first_name
        Book -> Author -> Publisher -> Name: this would return author.publisher.name
        """
        if self.parent_field:
            return f"{self.parent_field.get_full_model_field_name()}.{self.model_field_name}"
        return self.model_field_name


class BaseField(ModelFieldNameMixin, model_field_name_index.BaseField): ...


class SearchField(BaseField, model_field_name_index.SearchField): ...


class AutocompleteField(BaseField, model_field_name_index.AutocompleteField): ...


class FilterField(BaseField, model_field_name_index.FilterField): ...


class RelatedFields(ModelFieldNameMixin, index.RelatedFields):
    def __init__(
        self,
        *args,
        related_fields_kwargs: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.related_fields_kwargs = related_fields_kwargs or {}

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
        *args,
        parent_field: Optional[BaseField] = None,
    ) -> list[BaseField]:
        if parent_field:
            self.is_relation_of(parent_field)

        if self.parent_field:
            if "parent_field" not in self.related_fields_kwargs:
                self.related_fields_kwargs["parent_field"] = self.parent_field

        generated_fields = []
        for field in self.fields:
            if isinstance(field, one_to_many_index.IndexedField) or isinstance(
                field, RelatedFields
            ):
                generated_fields += field.generate_fields(
                    cls,
                    **self.related_fields_kwargs,
                )
            else:
                # is_relation_of won't work on Wagtail native fields
                field.is_relation_of(self)
                generated_fields.append(field)

        return [
            self.__class__(
                field_name=self.field_name,
                model_field_name=self.model_field_name,
                fields=generated_fields,
                **self.related_fields_kwargs,
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


class IndexedField(one_to_many_index.IndexedField):
    search_field_class = SearchField
    autocomplete_field_class = AutocompleteField
    filter_field_class = FilterField

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_field = None

    def generate_fields(
        self,
        cls,
        parent_field: Optional[BaseField] = None,
    ) -> list[BaseField]:
        if parent_field:
            self.is_relation_of(parent_field)

        if self.parent_field:
            if "parent_field" not in self.search_kwargs:
                self.search_kwargs["parent_field"] = self.parent_field
            if "parent_field" not in self.autocomplete_kwargs:
                self.autocomplete_kwargs["parent_field"] = self.parent_field
            if "parent_field" not in self.filter_kwargs:
                self.filter_kwargs["parent_field"] = self.parent_field

        return super().generate_fields(cls)


class Indexed(index.Indexed):
    @classmethod
    def get_indexed_objects(cls):
        queryset = cls.objects.all()

        # Add prefetch/select related for RelatedFields
        for field in cls.get_search_fields():
            if isinstance(field, RelatedFields):
                queryset = field.select_on_queryset(queryset)

        return queryset
