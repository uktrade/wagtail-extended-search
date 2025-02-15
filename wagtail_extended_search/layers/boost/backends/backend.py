from wagtail.search.query import Fuzzy, Phrase

from wagtail_extended_search.layers.base.backends.backend import (
    ExtendedSearchQueryCompiler,
)


class BoostSearchQueryCompiler(ExtendedSearchQueryCompiler):
    def _compile_query(self, query, field, boost=1.0):
        if isinstance(query, Fuzzy):
            return self._compile_fuzzy_query(query, [field], boost)
        if isinstance(query, Phrase):
            return self._compile_phrase_query(query, [field], boost)
        return super()._compile_query(query, field, boost)

    def _compile_fuzzy_query(self, query, fields, boost=1.0):
        """
        Support boosting
        """
        match_query = super()._compile_fuzzy_query(query, fields)

        if "multi_match" in match_query:
            if boost != 1.0:
                match_query["multi_match"]["boost"] = boost
        elif "match" in match_query:
            if boost != 1.0 or fields[0].boost != 1.0:
                match_query["match"][fields[0].field_name]["boost"] = (
                    boost * fields[0].boost
                )

        return match_query

    def _compile_phrase_query(self, query, fields, boost=1.0):
        """
        Support boosting
        """
        match_query = super()._compile_phrase_query(query, fields)

        if "multi_match" in match_query:
            if boost != 1.0:
                match_query["multi_match"]["boost"] = boost
        elif "match_phrase" in match_query:
            if boost != 1.0 or fields[0].boost != 1.0:
                query = match_query["match_phrase"][fields[0].field_name]
                if isinstance(query, dict) and "boost" in query:
                    match_query["match_phrase"][fields[0].field_name]["boost"] = (
                        boost * fields[0].boost
                    )
                else:
                    match_query["match_phrase"][fields[0].field_name] = {
                        "query": query,
                        "boost": boost * fields[0].boost,
                    }

        return match_query
