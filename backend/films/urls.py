from django.urls import path

from .views import FilmDetailView, FilmStreamingView, FilmTrailerView

urlpatterns = [
    path("films/<str:imdb_id>", FilmDetailView.as_view(), name="film-detail"),
    path("films/<str:imdb_id>/trailer", FilmTrailerView.as_view(), name="film-trailer"),
    path("films/<str:imdb_id>/streaming", FilmStreamingView.as_view(), name="film-streaming"),
]



