"""
Tests for the Django Admin Dashboard
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client as HttpTestClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class Admin_Site(TestCase):
    """Tests for Django Admin"""

    def setUp(self):
        """Create user and client"""
        self.client = HttpTestClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
        )
        self.client.force_login(self.admin_user)
        self.basic_user = get_user_model().objects.create_user(
            email="basic@example.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
        )

    def test_user_list(self):
        """Test that users are listed on page"""
        url: str = reverse("admin:core_user_changelist")
        res: HttpResponse = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, self.admin_user)
        self.assertContains(res, self.basic_user)

    def test_user_edit_page(self):
        """Test the edit user page works"""
        url = reverse("admin:core_user_change", args=[self.basic_user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test the create user page works"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
