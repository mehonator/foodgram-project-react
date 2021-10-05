from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    USER = "user", _("User")
    ADMIN = "admin", _("Admin")


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, unique=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)
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


class Subscription(models.Model):
    follower = models.ForeignKey(
        CustomUser, related_name="follower", on_delete=models.CASCADE
    )
    leader = models.ForeignKey(
        CustomUser, related_name="leader", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("follower", "leader"),)

    def __str__(self):
        return f"{self.follower.get_username()}-{self.leader.get_username()}"
