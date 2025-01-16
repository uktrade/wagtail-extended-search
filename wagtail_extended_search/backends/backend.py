from wagtail.search.backends.elasticsearch7 import Elasticsearch7SearchBackend

from wagtail_extended_search.boost.backends.backend import BoostSearchQueryCompiler
from wagtail_extended_search.filtered.backends.backend import (
    FilteredSearchMapping,
    FilteredSearchQueryCompiler,
)
from wagtail_extended_search.function_score.backends.backend import (
    FunctionScoreSearchQueryCompiler,
)
from wagtail_extended_search.nested.backends.backend import NestedSearchQueryCompiler
from wagtail_extended_search.only_fields.backends.backend import (
    OnlyFieldSearchQueryCompiler,
)


class CustomSearchMapping(
    FilteredSearchMapping,
): ...


class CustomSearchQueryCompiler(
    FunctionScoreSearchQueryCompiler,
    BoostSearchQueryCompiler,
    FilteredSearchQueryCompiler,
    OnlyFieldSearchQueryCompiler,
    NestedSearchQueryCompiler,
):
    mapping_class = CustomSearchMapping


class CustomSearchBackend(Elasticsearch7SearchBackend):
    query_compiler_class = CustomSearchQueryCompiler
    mapping_class = CustomSearchMapping


SearchBackend = CustomSearchBackend
