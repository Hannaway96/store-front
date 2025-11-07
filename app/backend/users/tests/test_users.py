"""
Test Users API
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestUserAPI(TestCase):
    """Test Users API"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")

    def test_registration_success(self):
        """Test to verify a user is given tokens when registering for the first time"""
        req = {
            "email": "example@mail.com",
            "password": "password123",
            "password_confirm": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(self.register_url, req, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", res.data)
        self.assertIn("tokens", res.data)
        self.assertIsNotNone(res.data["tokens"]["refresh"])
        self.assertIsNotNone(res.data["tokens"]["access"])

    def test_registration_invalid_email(self):
        """Test to verify a user is rejected if their email is invalid"""
        req = {
            "email": "example!mail,com",
            "password": "password123",
            "password_confirm": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(self.register_url, req, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_passwords_dont_match(self):
        """Test to verify an error if the passwords don't match"""
        password = "password123"
        confirm = "password321"
        req = {
            "email": "example@mail.com",
            "password": password,
            "password_confirm": confirm,
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(self.register_url, req, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
