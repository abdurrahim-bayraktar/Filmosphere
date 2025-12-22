from django.urls import path
from .views import imdb_search

urlpatterns = [
    path("imdb/", imdb_search, name="imdb-search"),
]
