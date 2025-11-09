"""
Custom Serializers for Models
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User Model"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile Model"""

    class Meta:
        model = Profile
        fields = [
            "date_of_birth",
            "address",
            "postcode",
            "display_name",
            "bio",
            "location",
        ]
