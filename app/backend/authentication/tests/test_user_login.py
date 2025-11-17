"""
Test User Login
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class User_Login(TestCase):
    """Test User Login"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")

    def create_user(self, **kwargs):
        """Helper Function to create a valid user"""
        user = get_user_model().objects.create_user(**kwargs)
        return user

    def test_user_logs_in_success(self):
        """Test that an existing user can login"""
        self.create_user(
            email="user@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )

        request = {"email": "user@mail.com", "password": "password123"}
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_does_not_exist(self):
        """Test that a user can't login if they haven't regsitered"""
        request = {"email": "notExist@mail.com", "password": "password123"}
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_incorrect_password(self):
        """Test that a user can't login with an incorrect password"""
        user = self.create_user(
            email="user@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )
        request = {"email": "user@mail.com", "password": "wrongPassword123"}
        response = self.client.post(self.url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(get_user_model().check_password(user, request["password"]))
