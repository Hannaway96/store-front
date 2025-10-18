from django.http import JsonResponse
from django.core.cache import cache

def health(request):
    return JsonResponse({"status": "ok"})

def ping_redis(request):
    cache.set("hello", "world", timeout=30)
    return JsonResponse({"redis": cache.get("hello", None)})