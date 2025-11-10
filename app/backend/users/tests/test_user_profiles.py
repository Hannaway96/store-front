"""
Test Profile Actions
"""

from datetime import date

from core.models import Profile
from core.serializers import ProfileSerializer
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def get_url(user_id):
    """Helper function to get profile url for a user"""
    return reverse("profile", args=[user_id])


class Profile_Actions_Unauthenticated(TestCase):
    """Test Actions while Unauthenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
        )
        self.profile = Profile.objects.create(
            user=self.user,
            display_name="John Doe",
            bio="Test bio",
        )
        self.profile.save()

    def test_get_profile_fail(self):
        """Test getting a profile"""
        url = get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_fail(self):
        """Test updating a profile via PATCH fails when unauthenticated"""
        request = {"bio": "Updated bio"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_profile_fail(self):
        """Test updating a profile via PUT fails when unauthenticated"""
        request = {
            "display_name": "Updated Name",
            "bio": "Updated bio",
        }
        url = get_url(self.user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class Profile_Actions_Authenticated(TestCase):
    """Test Actions while Authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user_1@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )
        token = self.get_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.profile = Profile.objects.create(
            user=self.user,
            display_name="John Doe",
            bio="Test bio",
        )

    def get_access_token(self, user):
        """Helper function to get auth tokens for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_profile(self):
        """Test getting a profile"""
        url = get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(serializer.data["display_name"], self.profile.display_name)
        self.assertEqual(serializer.data["bio"], self.profile.bio)

    def test_patch_profile(self):
        """Test updating a profile via PATCH"""
        request = {"bio": "Updated bio"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertNotEqual(serializer.data["bio"], self.profile.bio)

        self.profile.refresh_from_db()
        self.assertEqual(serializer.data["bio"], self.profile.bio)
        self.assertEqual(serializer.data["display_name"], self.profile.display_name)

    def test_put_profile(self):
        """Test updating a profile via PUT"""
        request = {
            "display_name": "Jane Doe",
            "bio": "Updated bio",
            "location": "New York",
        }
        url = get_url(self.user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertNotEqual(serializer.data["display_name"], self.profile.display_name)
        self.assertNotEqual(serializer.data["bio"], self.profile.bio)

        self.profile.refresh_from_db()
        self.assertEqual(serializer.data["display_name"], self.profile.display_name)
        self.assertEqual(serializer.data["bio"], self.profile.bio)
