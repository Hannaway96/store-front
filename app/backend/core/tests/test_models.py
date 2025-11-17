"""
Test Models in the system
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from core.models import Profile


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new dummy user"""
    return get_user_model().objects.create_user(email=email, password=password, date_of_birth=date(1990, 1, 1))


class User_Model(TestCase):
    """Test User Model"""

    def test_create_user_with_email(self):
        """Test creating a user with an email is success"""
        email = "test@mail.com"
        password = "password123"
        user = create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_normalised_email(self):
        """Test emails are normalised when user is created"""
        emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["test2@Example.com", "test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in emails:
            user = create_user(email=email, password="sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user without an email raises an error"""
        with self.assertRaises(ValueError):
            create_user(email="", password="sample123")

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            email="example@mail.com",
            password="password123",
            date_of_birth=date(1990, 1, 1),
        )
        self.assertEqual(user.is_staff, True)
        self.assertEqual(user.is_superuser, True)


class Profile_Model(TestCase):
    """Test Profile Model"""

    def test_profile_requires_user(self):
        """Test a Profile must have an existing User"""
        with self.assertRaises(IntegrityError):
            Profile.objects.create(
                display_name="Test User",
                bio="Test bio",
            )
