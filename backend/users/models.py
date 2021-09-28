from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    USER = "user", _("User")
    ADMIN = "admin", _("Admin")


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff
