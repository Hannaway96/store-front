"""
URLs for User routes
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterUserView, UserDetailViewSet, ProfileViewSet

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("<int:id>/", UserDetailViewSet.as_view(), name="user-detail"),
    path("<int:id>/profile/", ProfileViewSet.as_view(), name="profile"),
]
