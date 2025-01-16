from wagtail.search.backends.elasticsearch7 import Elasticsearch7SearchBackend

from wagtail_extended_search.search_backend_concepts.boost.backends.backend import (
    BoostSearchQueryCompiler,
)
from wagtail_extended_search.search_backend_concepts.filtered.backends.backend import (
    FilteredSearchMapping,
    FilteredSearchQueryCompiler,
)
from wagtail_extended_search.search_backend_concepts.function_score.backends.backend import (
    FunctionScoreSearchQueryCompiler,
)
from wagtail_extended_search.search_backend_concepts.nested.backends.backend import (
    NestedSearchQueryCompiler,
)
from wagtail_extended_search.search_backend_concepts.only_fields.backends.backend import (
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
