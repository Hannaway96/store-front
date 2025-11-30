"""
Core Application Models
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager for Users"""

    def create_user(self, email, password=None, **extra_fileds):
        """Create, save and return a user"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fileds)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a super user"""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the System"""

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD: str = "email"

    def __str__(self):
        return f"({self.email}): {self.first_name} {self.last_name}"


class Profile(models.Model):
    """User's Profile - Public Information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.user.email}): {self.display_name}"

class Brand(models.Model):
    """Product Brand Model"""
    name = models.CharField(blank=False)

    def __str__(self):
        return f"{self.name}"

class Category(models.Model):
    """Product Category Model"""
    name = models.CharField(blank=False)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    """Product Model"""

    sku = models.CharField(blank=False, null=False)
    title = models.CharField(blank=False, null=False)
    price = models.DecimalField(decimal_places=2, max_digits=6) #9999.99
    in_stock = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.sku}: {self.title}"
