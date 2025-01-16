from wagtail.search.query import Fuzzy, Phrase

from wagtail_extended_search.base.backends.backend import ExtendedSearchQueryCompiler


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

        if boost != 1.0:
            if "multi_match" in match_query:
                match_query["multi_match"]["boost"] = boost * fields[0].boost
            elif "match" in match_query:
                for field in fields:
                    match_query["match"][field.field_name]["boost"] = (
                        boost * field.boost
                    )

        return match_query

    def _compile_phrase_query(self, query, fields, boost=1.0):
        """
        Support boosting
        """
        match_query = super()._compile_phrase_query(query, fields)

        if boost != 1.0:
            if "multi_match" in match_query:
                match_query["multi_match"]["boost"] = boost * fields[0].boost
            elif "match_phrase" in match_query:
                for field in fields:
                    query = match_query["match_phrase"][field.field_name]
                    if isinstance(query, dict) and "boost" in query:
                        match_query["match_phrase"][field.field_name]["boost"] = (
                            boost * field.boost
                        )
                    else:
                        match_query["match_phrase"][field.field_name] = {
                            "query": query,
                            "boost": boost * field.boost,
                        }

        return match_query
