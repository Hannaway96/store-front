"""
Test User Refresh Tokens
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from ..serializers import RegisterResponseSerializer


class Test_User_Refresh_Tokens(TestCase):
    """Test User Refresh_Tokens"""

    def setUp(self):
        self.client = APIClient()
        self.login = reverse("login")
        self.url = reverse("refresh")
        self.valid_user = get_user_model().objects.create_user(
            email="valid@mail.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )

    def test_authed_user_can_refresh(self):
        """Test that an authed user can refresh their tokens"""
        login_request = {
            "email": self.valid_user.email,
            "password": "password123",
        }
        login_response = self.client.post(self.login, login_request, format="json")

        self.assertIn("refresh", login_response.data)
        self.assertIn("access", login_response.data)

        refresh_token = login_response.data["refresh"]
        refresh_request = {"refresh": refresh_token}
        refresh_response = self.client.post(self.url, refresh_request, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
        self.assertIn("refresh", refresh_response.data)
