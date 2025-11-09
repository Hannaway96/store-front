"""
API Views for Users
"""

from core.models import Profile
from core.serializers import ProfileSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterRequestSerializer

User = get_user_model()


class UserRegisterView(CreateAPIView):
    """
    API View for Registering Users
    POST - users/regsiter
    """

    serializer_class = RegisterRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        """
        create function overrides POST logic
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Check if the error is due to an existing user
            if "email" in serializer.errors:
                for error in serializer.errors["email"]:
                    if hasattr(error, "code") and error.code == "user_exists":
                        return Response(
                            status=status.HTTP_409_CONFLICT,
                            data={"email": ["A user with this email already exists"]},
                        )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        user = serializer.save()
        refresh_token = RefreshToken.for_user(user)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
            },
        )


class UserDetailViewSet(RetrieveUpdateAPIView):
    """
    View set for User
    GET, PATCH, PUT users/{user_id}/
    """

    lookup_field = "id"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ProfileViewSet(RetrieveUpdateAPIView):
    """
    View Set for Users Profile
    GET, PATCH, PUT users/{user_id}/profile/
    """

    lookup_field = "user__id"
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
