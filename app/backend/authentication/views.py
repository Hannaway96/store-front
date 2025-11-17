"""
Views for Authentication
"""

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterRequestSerializer, RegisterResponseSerializer


class RegistrationView(CreateAPIView):
    """
    API View for Registering new Users
    POST - auth/regsiter
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
        token = RefreshToken.for_user(user)
        res = RegisterResponseSerializer(
            {
                "user": user,
                "tokens": {
                    "refresh": str(token),
                    "access": str(token.access_token),
                },
            }
        )
        return Response(status=status.HTTP_201_CREATED, data=res.data)
