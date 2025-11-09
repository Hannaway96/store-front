"""
Test User Actions
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

#TODO Write more User Action Tests for PATCH PUT

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

    def test_get_user(self):
        """Test getting a user fails while unauthenticated"""
        url = get_url(self.user.id)
        response = self.client.get(url)
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
