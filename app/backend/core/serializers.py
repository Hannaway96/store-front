"""
Custom Serializers for Models
"""

from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from .models import Brand, Category, Product, Profile

User = get_user_model()


class UserSerializer(ModelSerializer):
    """Serializer for User Model"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "date_of_birth"]
        read_only_fields = ["id"]


class ProfileSerializer(ModelSerializer):
    """Serializer for Profile Model"""

    class Meta:
        model = Profile
        fields = ["display_name", "bio", "location", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class BrandSerializer(ModelSerializer):
    """Serializer for Brand Model"""

    class Meta:
        model = Brand
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategorySerializer(ModelSerializer):
    """Serializer for Category Model"""

    class Meta:
        model = Category
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductSerializer(ModelSerializer):
    """Serializer for Product Model"""

    class Meta:
        model = Product
        fields = ["id", "sku", "title", "price", "quantity", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
