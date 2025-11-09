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
        )
        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),
            address="1 random street",
            postcode="BT474BN",
        )
        self.profile.save()

    def test_get_profile_fail(self):
        """Test getting a profile"""
        url = get_url(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_fail(self):
        """Test updating a profile via PATCH fails when unauthenticated"""
        request = {"address": "2 another street"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_profile_fail(self):
        """Test updating a profile via PUT fails when unauthenticated"""
        request = {
            "date_of_birth": date(1996, 7, 16),
            "address": "2 another street",
            "postcode": "BT488BY",
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
            first_name="John",
            last_name="Doe",
        )
        token = self.get_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),
            address="1 random street",
            postcode="BT474BN",
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
        self.assertEqual(serializer.data["address"], self.profile.address)
        self.assertEqual(serializer.data["postcode"], self.profile.postcode)
        self.assertEqual(
            serializer.data["date_of_birth"], str(self.profile.date_of_birth)
        )

    def test_patch_profile(self):
        """Test updating a profile via PATCH"""
        request = {"address": "2 another street"}
        url = get_url(self.user.id)
        response = self.client.patch(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertNotEqual(serializer.data["address"], self.profile.address)

        self.profile.refresh_from_db()
        self.assertEqual(serializer.data["address"], self.profile.address)
        self.assertEqual(serializer.data["postcode"], self.profile.postcode)
        self.assertEqual(
            serializer.data["date_of_birth"], str(self.profile.date_of_birth)
        )

    def test_put_profile(self):
        """Test updating a profile via PUT"""
        request = {
            "date_of_birth": date(1996, 7, 16),
            "address": "2 another street",
            "postcode": "BT488BY",
        }
        url = get_url(self.user.id)
        response = self.client.put(url, request, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializer(response.data)
        self.assertEqual(serializer.data, response.data)
        self.assertNotEqual(serializer.data["address"], self.profile.address)
        self.assertNotEqual(serializer.data["postcode"], self.profile.postcode)
        self.assertNotEqual(
            serializer.data["date_of_birth"], str(self.profile.date_of_birth)
        )

        self.profile.refresh_from_db()
        self.assertEqual(serializer.data["address"], self.profile.address)
        self.assertEqual(serializer.data["postcode"], self.profile.postcode)
        self.assertEqual(
            serializer.data["date_of_birth"], str(self.profile.date_of_birth)
        )
