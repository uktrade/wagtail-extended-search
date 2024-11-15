from bakerydemo.urls import *  # noqa: F403, F401
from django.urls import path
from overrides import views as search_views

for url in urlpatterns:  # noqa: F405
    if getattr(url, "name", None) == "search":
        urlpatterns.remove(url)

urlpatterns = [  # noqa: F405
    path("search/", search_views.search, name="search"),
] + urlpatterns
