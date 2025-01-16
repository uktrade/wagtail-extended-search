import inspect

from wagtail.search import index


class ModelFieldNameMixin:
    def __init__(
        self,
        field_name,
        *args,
        model_field_name=None,
        parent_field=None,
        configuration_model=None,
        **kwargs,
    ):
        super().__init__(field_name, *args, **kwargs)
        self.model_field_name = model_field_name or field_name
        self.parent_field = parent_field
        self.configuration_model = configuration_model

    def get_field(self, cls):
        return cls._meta.get_field(self.model_field_name)

    def get_definition_model(self, cls):
        if self.configuration_model:
            return self.configuration_model

        if base_cls := super().get_definition_model(cls):
            return base_cls

        # Find where it was defined by walking the inheritance tree
        base_model_field_name = self.get_base_model_field_name()
        for base_cls in inspect.getmro(cls):
            if hasattr(base_cls, base_model_field_name):
                return base_cls

    def get_value(self, obj):
        if value := super().get_value(obj):
            return value

        value = getattr(obj, self.model_field_name, None)
        # if hasattr(value, "__call__"):  # noqa: B004
        #     value = value()
        return value

    #################################
    # RelatedField support in queries
    #################################

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


class BaseField(ModelFieldNameMixin, index.BaseField):
    def get_attname(self, cls):
        if self.model_field_name != self.field_name:
            return self.field_name
        return super().get_attname(cls)


class SearchField(index.SearchField, BaseField, index.BaseField): ...


class AutocompleteField(index.AutocompleteField, BaseField, index.BaseField): ...


class FilterField(index.FilterField, BaseField, index.BaseField): ...
