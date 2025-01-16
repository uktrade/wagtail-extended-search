from wagtail_extended_search.base.backends.backend import ExtendedSearchQueryCompiler
from wagtail_extended_search.search_backend_concepts.function_score.query import (
    FunctionScore,
)


class FunctionScoreSearchQueryCompiler(ExtendedSearchQueryCompiler):
    def _compile_query(self, query, field, boost=1.0):
        if isinstance(query, FunctionScore):
            return self._compile_function_score_query(query, [field], boost)
        return super()._compile_query(query, field, boost)

    def _compile_function_score_query(self, query, fields, boost=1.0):
        if query.function_name == "script_score":
            params = query.function_params
        else:  # it's a decay query
            score_functions = {
                f.function_name: f for f in query.model_class.get_score_functions()
            }
            score_func = score_functions[query.function_name]

            # This is in place of get_field_column_name to build the name of the indexed field.
            remapped_field_name = score_func.get_score_name() + "_filter"
            params = {remapped_field_name: query.function_params["_field_name_"]}

        return {
            "function_score": {
                "query": self._join_and_compile_queries(query.subquery, fields, boost),
                query.function_name: params,
            }
        }
