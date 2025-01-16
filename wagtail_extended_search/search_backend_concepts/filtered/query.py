from wagtail.search.query import SearchQuery


class Filtered(SearchQuery):
    def __init__(self, subquery: SearchQuery, filters: list[tuple]) -> None:
        if not isinstance(subquery, SearchQuery):
            raise TypeError("The `subquery` parameter must be of type SearchQuery")

        if not isinstance(filters, list):
            raise TypeError("The `filters` parameter must be a list of thruples")

        if not isinstance(filters[0], tuple) or not len(filters[0]) == 3:
            raise TypeError("The `filters` parameter must be a list of thruples")

        self.subquery = subquery
        self.filters = filters

    def __repr__(self) -> str:
        return "<Filtered {} filters=[{}]>".format(
            repr(self.subquery),
            ", ".join([f"{f}" for f in self.filters]),
        )
