"""
API Views for Users
"""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterRequestSerializer,
    UserSerializer,
)


class RegisterUserView(APIView):
    """
    Public endpoint (no authentication required)
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=RegisterRequestSerializer,
        responses={
            201: UserSerializer,
            400: None,  # Schema inferred from examples
            409: None,  # Schema inferred from examples
        },
        examples=[
            OpenApiExample(
                "Successful Registration",
                value={
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                    },
                    "tokens": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    },
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Validation Error - Password Mismatch",
                value={"non_field_errors": ["Passwords Provided don't match"]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Validation Error - Invalid Email",
                value={"email": ["Enter a valid email address"]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Validation Error - Password Too Short",
                value={"password": ["Ensure this field has at least 8 characters."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "User Already Exists",
                value={"email": ["A user with this email already exists"]},
                response_only=True,
                status_codes=["409"],
            ),
        ],
    )
    def post(self, request):
        """
        POST - Register a new user
        """
        serializer = RegisterRequestSerializer(data=request.data)
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

# class UserInfoView():
#     """Get User info"""