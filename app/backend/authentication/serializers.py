"""
Custom Serializers for Authentication views
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from core.models import Profile
from core.serializers import UserSerializer

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    """Serializer for Auth Tokens"""

    access = serializers.CharField(help_text="Access Token")
    refresh = serializers.CharField(help_text="Refresh Token")


class RegisterResponseSerializer(serializers.Serializer):
    """Serializer for Registration Response"""

    user = UserSerializer()
    tokens = TokenSerializer()


class RegisterRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "date_of_birth",
        ]
        extra_kwargs = {
            "email": {"validators": []},  # Remove default validators including uniqueness
        }

    def too_young(self, date) -> bool:
        today = date.today()
        age = today.year - date.year - ((today.month, today.day) < (date.month, date.day))
        return age < 18

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address") from None

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists", code="user_exists"
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords Provided don't match")

        if attrs["date_of_birth"] and self.too_young(attrs["date_of_birth"]):
            raise serializers.ValidationError("User must be 18 or older", code="dob_error")

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            date_of_birth=validated_data.get("date_of_birth"),
        )
        Profile.objects.create(user=user)
        return user
