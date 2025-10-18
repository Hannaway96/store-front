from django.urls import path
from .views import health, ping_redis

urlpatterns = [
    path("health/", health, name="health"),
    path("redis/", ping_redis, name="redis"),
]