from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=200, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    birth_date = models.DateField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or ""


class ConfirmationCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='confirmation')
    code = models.CharField(max_length=6)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
