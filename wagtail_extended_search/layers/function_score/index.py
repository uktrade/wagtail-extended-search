from typing import Optional

from django.db import models
from wagtail.search import index

from wagtail_extended_search.layers.related_fields.index import BaseField, FilterField


class ScoreFunction:
    SUPPORTED_FUNCTIONS = ["script_score", "gauss", "exp", "linear"]

    def __init__(self, function_name, **kwargs) -> None:
        if function_name not in self.SUPPORTED_FUNCTIONS:
            raise AttributeError(
                f"Function {function_name} is not supported, expecting one of {', '.join(self.SUPPORTED_FUNCTIONS)}"
            )
        self.function_name = kwargs["function_name"] = function_name

        if function_name == "script_score":
            if "script" not in kwargs and "source" not in kwargs:
                raise AttributeError(
                    "The 'script_score' function type requires passing either a 'script' or a 'source' parameter"
                )

            if "script" in kwargs:
                if (
                    not isinstance(kwargs["script"], dict)
                    or "source" not in kwargs["script"]
                ):
                    raise AttributeError(
                        "The 'script' parameter must be a dict containing a 'source' key"
                    )
                self.script = kwargs["script"]
            elif "source" in kwargs:
                self.script = {"source": kwargs["source"]}

            self.params = {"script": self.script}

        else:  # it's a decay function
            if "field_name" not in kwargs:
                raise AttributeError(
                    f"The '{function_name}' function requires a 'field_name' parameter"
                )
            if "scale" not in kwargs:
                raise AttributeError(
                    f"The '{function_name}' function requires a 'scale' parameter"
                )
            if "decay" not in kwargs:
                # optional for ES, but we want explicit values in the config
                raise AttributeError(
                    f"The '{function_name}' function requires a 'decay' parameter"
                )
            self.field_name = kwargs["field_name"]
            self.scale = kwargs["scale"]
            self.decay = kwargs["decay"]
            self.params = {
                # TODO look into this field_name, see comment below
                "_field_name_": {  # NB important this is the model field name
                    "scale": self.scale,
                    "decay": self.decay,
                }
            }
            if "offset" in kwargs:
                self.offset = kwargs["offset"]
                self.params["_field_name_"]["offset"] = self.offset
            if "origin" in kwargs:
                self.origin = kwargs["origin"]
                self.params["_field_name_"]["origin"] = self.origin

    def get_score_name(self):
        return f"{self.field_name}_scorefunction"

    def generate_fields(
        self,
        parent_field: Optional[BaseField] = None,
    ) -> list[BaseField]:
        generated_fields = []

        if self.field_name:
            generated_fields.append(
                FilterField(
                    self.get_score_name(),
                    model_field_name=self.field_name,
                    parent_field=parent_field,
                )
            )

        return generated_fields


class Indexed(index.Indexed):
    @classmethod
    def get_score_functions(cls):
        return [
            field
            for field in cls.get_indexed_fields()
            if isinstance(field, ScoreFunction)
        ]
