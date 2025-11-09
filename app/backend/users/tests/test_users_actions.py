"""
Test User Actions
"""

from core.serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def get_url(user_id):
    """Helper function to get url for a user"""
    return reverse("user-detail", args=[user_id])


class User_Actions_Unauthenticated(TestCase):
    """Test Actions while Unauthenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )

    def test_get_user_fail(self):
        """Test getting a user fails when unauthenticated"""
        url = get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_fail(self):
        """Test updating a user via patch fails when unauthenticated"""
        request = {"first_name": "Josh", "last_name": "Doe"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_fail(self):
        """Test updating a user via put fails when unauthenticated"""
        request = {
            "email": "user_1@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        url = get_url(self.user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class User_Actions_Authenticated(TestCase):
    """Test User Actions while Authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )
        token = self.get_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def get_access_token(self, user):
        """Helper function to get auth tokens for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_user(self):
        """Test an existing is returned by ID"""
        url = get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_user(self):
        """Test updating a user via PATCH"""
        request = {"first_name": "Josh", "last_name": "Doe"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(serializer.data["first_name"], request["first_name"])
        self.assertEqual(serializer.data["last_name"], request["last_name"])
        self.assertNotEqual(serializer.data["first_name"], self.user.first_name)

        self.user.refresh_from_db()
        self.assertEqual(serializer.data["first_name"], self.user.first_name)
        self.assertEqual(serializer.data["last_name"], self.user.last_name)

    def test_put_user(self):
        """Test updating a user via PUT"""
        request = {
            "email": "user_1@mail.com",
            "first_name": "Jenny",
            "last_name": "Dane",
        }
        url = get_url(self.user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(serializer.data["email"], request["email"])
        self.assertEqual(serializer.data["first_name"], request["first_name"])
        self.assertEqual(serializer.data["last_name"], request["last_name"])
        self.assertNotEqual(serializer.data["first_name"], self.user.first_name)
        self.assertNotEqual(serializer.data["last_name"], self.user.last_name)

        self.user.refresh_from_db()
        self.assertEqual(serializer.data["email"], self.user.email)
        self.assertEqual(serializer.data["first_name"], self.user.first_name)
        self.assertEqual(serializer.data["last_name"], self.user.last_name)
