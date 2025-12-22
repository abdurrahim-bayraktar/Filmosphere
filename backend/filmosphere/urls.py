from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns =[
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/", include("users.urls")),  # auth endpoints için
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    #test icin yine bu da
    path('api-auth/', include('rest_framework.urls')),
 ] 


