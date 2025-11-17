"""
URLs for Users API Routes
"""

from django.urls import path

from .views import ProfileViewSet, UserDetailViewSet

urlpatterns = [
    path("<int:pk>/", UserDetailViewSet.as_view(), name="user-detail"),
    path("<int:user__id>/profile/", ProfileViewSet.as_view(), name="profile"),
]
