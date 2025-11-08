"""
API Views for Users
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)
from .serializers import RegisterSerializer, UserSerializer


@extend_schema_view(
    create=extend_schema(
        request=RegisterSerializer,
        responses={
            201: {
                "user": UserSerializer,
                "tokens": {"refresh": OpenApiTypes.STR, "access": OpenApiTypes.STR},
            },
            400: {},
            409: {}
        },
    )
)
class RegisterUserView(APIView):
    """
    Public endpoint (no authentication required)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        POST - Register a new user
        """
        serializer = RegisterSerializer(data=request.data)
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
