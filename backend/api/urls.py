from django.urls import include, path
from films.views import SearchView
from api.recommendation_chat import RecommendationChatView

urlpatterns = [
    path("search/", SearchView.as_view(), name="film-search"),
    path("recommendations/chat/", RecommendationChatView.as_view(), name="recommendations-chat"),
    path("", include("films.urls")),
    path("auth/", include("users.urls")),
]