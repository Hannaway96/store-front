"""
Test User Actions
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.helpers import API_Client
from core.serializers import UserSerializer


def get_url(user_id):
    """Helper function to get url for a user"""
    return reverse("user-detail", args=[user_id])


class User_Actions_Unauthenticated(TestCase):
    """Test Actions while Unauthenticated"""

    def setUp(self):
        self.client = API_Client()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
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
        self.client = API_Client()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )
        self.other_user = get_user_model().objects.create_user(
            email="user_2@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
            first_name="Jane",
            last_name="Doe",
        )
        self.client.authorize(self.user)

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
            "date_of_birth": date(1990, 1, 1),
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

    def test_user_can_only_get_themself(self):
        """Test only owner of a user can GET"""
        url = get_url(self.other_user.id)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_patch_themself(self):
        """Test only owner can update user via PUT"""
        request = {
            "email": "user@mail.com",
        }
        url = get_url(self.other_user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_put_themself(self):
        """Test only owner can update user via PUT"""
        request = {
            "email": "user@mail.com",
            "first_name": "Jenny",
            "last_name": "Dane",
            "date_of_birth": date(1990, 1, 1),
        }
        url = get_url(self.other_user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
