from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # USERS
    path("api/", include("users.urls")),

    # FILMS
    path("api/", include("films.urls")),

    # SEARCH
    path("api/search/", include("search.urls")),
]
