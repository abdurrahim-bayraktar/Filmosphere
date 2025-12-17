from django.urls import include, path

from films.views import SearchView

urlpatterns = [
    path("search/", SearchView.as_view(), name="film-search"),
    path("", include("films.urls")),
    path("auth/", include("users.urls")),
]



