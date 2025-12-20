import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def imdb_search(request):
    """
    Proxy endpoint for IMDbAPI.dev search:
    https://api.imdbapi.dev/search/titles?query=xxx&limit=10
    """
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"results": []})

    url = "https://api.imdbapi.dev/search/titles"
    params = {
        "query": query,
        "limit": 10
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Normalize for frontend
        titles = data.get("titles", []) or []

        results = []
        for item in titles:
            primary_image = item.get("primaryImage") or {}

            results.append({
                "imdb_id": item.get("id"),
                "title": item.get("primaryTitle"),
                "year": item.get("startYear"),
                "image": primary_image.get("url"),
                "type": item.get("titleType")
            })

        return JsonResponse({"results": results})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
