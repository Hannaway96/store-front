"""
API Views for Users
"""

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from serializers import RegisterSerializer, UserSerializer

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class RegisterUserView(APIView):
    """
    POST - Register a new user
    Public endpoint (no authentication required)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh_token = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh_token),
                        "access": str(refresh_token.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
