"""
Test Models in the system
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from core.models import Brand, Category, Product, Profile


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new dummy user"""
    return get_user_model().objects.create_user(
        email=email, password=password, date_of_birth=date(1990, 1, 1)
    )


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


class Product_Model(TestCase):
    """Test Product Model"""

    def test_create(self):
        """Test a successful product creation"""
        apple = Brand.objects.create(name="Apple")
        apple.save()

        product = Product.objects.create(
            brand=apple,
            sku="aplmbprom5",
            title="MacBook Pro M5",
            price="1.50",
            quantity=5,
        )
        product.save()

        all_products = Product.objects.all()
        first_product = all_products.first()

        self.assertEqual(all_products.count(), 1)
        self.assertEqual(product, first_product)
        self.assertEqual(product.brand, apple)

    def test_create_fail_no_brand(self):
        """Test creating a product without a brand, fails"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(sku="pr", title="Item 1", price="1.50", quantity=2)

    def test_create_fail_no_sku(self):
        """Test creating a product without a sku, fails"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                brand=Brand.objects.create(name="Brand"),
                sku="",
                title="Item 1",
                price="1.00",
                quantity=1,
            )

    def test_create_fail_no_title(self):
        """Test creatiung a product without a title, fails"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                brand=Brand.objects.create(name="Apple"), sku="sku", price="1.00", quantity=1
            )


class Brand_Model(TestCase):
    """Test the Brand Model"""

    def test_create(self):
        """Test creating a Brand successfully"""
        apple = Brand.objects.create(name="Apple")
        apple.save()

        brands = Brand.objects.all()
        self.assertEqual(brands.count(), 1)
        self.assertEqual(brands.first(), apple)

    def test_create_fails_no_name(self):
        """Test creating a Brand with no name, fails"""

        with self.assertRaises(IntegrityError):
            Brand.objects.create(name="")


class Category_Model(TestCase):
    """Test the Category Model"""

    def test_create(self):
        """Test creating a Category successfully"""

        category = Category.objects.create(name="Laptops")
        category.save()

        categories = Category.objects.all()
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first(), category)

    def test_create_fails_no_name(self):
        """Test creating a Category with no name, fails"""

        with self.assertRaises(IntegrityError):
            Category.objects.create(name="")
