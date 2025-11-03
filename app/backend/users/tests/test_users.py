"""
Test Users API
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import reverse


class TestUserAPI(TestCase):
    """Test Users API"""

    def test_registration_passwords_dont_match(self):
        """Test to verify an error if the passwords don't match"""
        password = "password123"
        confirm = "password321"

        # Need to call the register API endpoint now to verify it's hittable
        self.assertEqual(password, confirm)
