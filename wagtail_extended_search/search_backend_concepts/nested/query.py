from wagtail.search.query import SearchQuery


class Nested(SearchQuery):
    def __init__(self, subquery: SearchQuery, path: str) -> None:
        if not isinstance(subquery, SearchQuery):
            raise TypeError("The `subquery` parameter must be of type SearchQuery")

        if not isinstance(path, str):
            raise TypeError("The `path` parameter must be a string")

        self.subquery = subquery
        self.path = path

    def __repr__(self) -> str:
        return "<Nested {} path='{}'>".format(
            repr(self.subquery),
            self.path,
        )
