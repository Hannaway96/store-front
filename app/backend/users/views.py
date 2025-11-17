"""
API Views for Users
"""

from core.models import Profile
from core.permissions import UserIsOwner, UserIsOwnerOrReadOnly
from core.serializers import ProfileSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class UserDetailViewSet(RetrieveUpdateAPIView):
    """
    View set for User
    GET, PATCH, PUT users/{user_id}/
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserIsOwner]


class ProfileViewSet(RetrieveUpdateAPIView):
    """
    View Set for Users Profile
    GET, PATCH, PUT users/{user_id}/profile/
    """

    lookup_field = "user__id"
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, UserIsOwnerOrReadOnly]
