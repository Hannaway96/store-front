"""
Test User Registration
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


class User_Registration(TestCase):
    """Test User Registration"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register")

    def create_valid_request(self):
        """Helper function to create a payload for a valid regsitration"""
        return {
            "email": "valid@mail.com",
            "password": "password123",
            "password_confirm": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_registration_success_with_tokens(self):
        """Test to verify a user is given tokens when registering for the first time"""
        request = self.create_valid_request()
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIsNotNone(response.data["tokens"]["refresh"])
        self.assertIsNotNone(response.data["tokens"]["access"])

    def test_registration_success_with_user_in_db(self):
        """Test to verify a user is added to the database when registered"""
        request = self.create_valid_request()
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.all().count(), 1)

    def test_invalid_email(self):
        """Test to verify a user is rejected if their email is invalid"""
        request = self.create_valid_request()
        request["email"] = "invalid!mail,com"
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        validation_error = str(response.data["email"][0])
        self.assertEqual(validation_error, "Enter a valid email address.")

    def test_passwords_dont_match(self):
        """Test to verify an error if the passwords don't match"""
        request = self.create_valid_request()
        request["password_confirm"] = "incorrectPassword123"
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exists(self):
        """Test to verify registration fails when user already exists"""
        get_user_model().objects.create_user(
            email="valid@mail.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )
        request = self.create_valid_request()
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
