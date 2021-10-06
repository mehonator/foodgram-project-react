from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Unit(models.Model):
    name = models.CharField(
        max_length=128, unique=True, blank=False, null=False
    )
    short_name = models.CharField(max_length=128, blank=False, null=False)

    def __str__(self):
        return self.name


class Amount(models.Model):
    amount = models.FloatField(min=0.0, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return str(self.amount)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=512, unique=True, blank=False, null=False
    )
    amount = models.ManyToManyField(Amount, related_name="ingredients")
    unit = models.ForeignKey(
        Unit,
        related_name="ingredients",
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.name} {self.amount} {self.unit.short_name}"


class Recipe(models.Model):
    name = models.CharField(
        max_length=512, unique=True, blank=False, null=False
    )
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")
    author = models.ForeignKey(
        CustomUser, related_name="recipes", blank=False, null=False
    )

    def __str__(self):
        return self.name
