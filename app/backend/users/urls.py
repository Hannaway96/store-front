"""
URLs for Users API Routes
"""

from django.urls import path

from .views import ProfileViews, UserDetailViews

urlpatterns = [
    path("<int:pk>/", UserDetailViews.as_view(), name="user-detail"),
    path("<int:user__id>/profile/", ProfileViews.as_view(), name="profile"),
]
