from authentication import urls as auth_urls
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users import urls as user_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include(auth_urls)),
    path("users/", include(user_urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
