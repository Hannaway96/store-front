"""
Core Application Models
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    CheckConstraint,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    ForeignKey,
    ImageField,
    IntegerField,
    ManyToManyField,
    Model,
    OneToOneField,
    Q,
    TextField,
)


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

    email = EmailField(max_length=255, unique=True)
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    date_of_birth = DateField()

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD: str = "email"

    def __str__(self):
        return f"({self.email}): {self.first_name} {self.last_name}"


class Profile(Model):
    """User's Profile - Public Information"""

    user = OneToOneField(User, on_delete=CASCADE, related_name="profile")
    display_name = CharField(max_length=100, blank=True)
    avatar = ImageField(upload_to="avatars/", blank=True, null=True)
    bio = TextField(max_length=500, blank=True)

    location = CharField(max_length=100, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.user.email}): {self.display_name}"


class Brand(Model):
    """Product Brand Model"""

    name = CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        constraints = [CheckConstraint(check=~Q(name=""), name="brand_name_not_empty")]

    def __str__(self):
        return f"{self.name}"


class Category(Model):
    """Product Category Model"""

    name = CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        constraints = [CheckConstraint(check=~Q(name=""), name="category_name_not_empty")]

    def __str__(self):
        return f"{self.name}"


class Product(Model):
    """Product Model"""

    brand = ForeignKey(Brand, related_name="products", on_delete=CASCADE)
    categories = ManyToManyField(Category, related_name="products")

    sku = CharField(max_length=50, unique=True, blank=False, null=False)
    title = CharField(blank=False, null=False)
    price = DecimalField(decimal_places=2, max_digits=6)  # 9999.99
    quantity = IntegerField(null=False, default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(sku=""), name="product_sku_not_empty"),
            CheckConstraint(check=~Q(title=""), name="product_title_not_empty"),
        ]

    def __str__(self):
        return f"{self.sku}: {self.title}"

    def in_stock(self):
        """check if item is in stock"""
        return self.quantity > 0
