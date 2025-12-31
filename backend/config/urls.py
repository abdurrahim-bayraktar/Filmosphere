from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    """Root endpoint - shows API is running."""
    return JsonResponse({
        "status": "ok",
        "message": "Filmosphere API is running!",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/",
            "films": "/api/films/",
            "search": "/api/search/?q=<query>",
        }
    })


urlpatterns = [
    path("", api_root, name="api-root"),  # Root URL
    path("admin/", admin.site.urls),

    # USERS
    path("api/", include("users.urls")),

    # FILMS
    path("api/", include("films.urls")),

    # SEARCH
    path("api/search/", include("search.urls")),
]
