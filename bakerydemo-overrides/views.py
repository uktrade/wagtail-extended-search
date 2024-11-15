from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page

from wagtail_extended_search.query_builder import CustomQueryBuilder


def search(request):
    # Search
    search_query = request.GET.get("q", None)

    search_results = Page.objects.none()

    if search_query:
        built_query = CustomQueryBuilder.get_search_query(Page, search_query)
        if built_query:
            search_results = Page.objects.live().search(built_query)
            query = Query.get(search_query)
            # Record hit
            query.add_hit()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(
        request,
        "search/search_results.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
