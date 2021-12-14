from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Admin"


class CustomUser(AbstractUser):
    email = models.EmailField("email address", unique=True)
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
        "password",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff
