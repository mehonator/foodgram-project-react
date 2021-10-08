from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField
from autoslug import AutoSlugField
from transliterate import detect_language
from transliterate import slugify as trans_slugify
from django.utils.text import slugify as dj_slugify


CustomUser = get_user_model()


class NotFoundLangException(Exception):
    """Allow language:
    Armenian
    Bulgarian (beta)
    Georgian
    Greek
    Macedonian (alpha)
    Mongolian (alpha)
    Russian
    Serbian (alpha)
    Ukrainian (beta)"""

    pass


class MeasurementUnit(models.Model):
    name = models.CharField(
        max_length=128, unique=True, blank=False, null=False
    )

    def __str__(self):
        return self.name


class Amount(models.Model):
    amount = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self):
        return str(self.amount)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=512, unique=True, blank=False, null=False
    )
    amount = models.ManyToManyField(Amount, related_name="ingredients")
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        related_name="ingredients",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.name} {self.amount} {self.unit.short_name}"


class Recipe(models.Model):
    name = models.CharField(
        max_length=512, unique=True, blank=False, null=False
    )
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")
    author = models.ForeignKey(
        CustomUser,
        related_name="recipes",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


def transliterate_slugify(text: str):
    if text.isascii():
        return dj_slugify(text)

    if detect_language(text) is not None:
        return trans_slugify(text)

    raise NotFoundLangException("Invalid language")


def get_name(instance):
    return instance.name


class Tag(models.Model):
    name = models.CharField(
        max_length=512, unique=True, blank=False, null=False
    )
    color = ColorField(blank=True, null=True)
    slug = AutoSlugField(
        populate_from=get_name,
        slugify=transliterate_slugify,
        unique=True,
    )

