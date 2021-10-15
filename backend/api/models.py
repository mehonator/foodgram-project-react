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


class Ingredient(models.Model):
    name = models.CharField(max_length=512, blank=False, null=False)
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        related_name="ingredients",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.name} {self.measurement_unit.name}"


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


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=512,
        unique=True,
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Тэги", related_name="recipes", blank=True
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор",
        related_name="recipes",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    users_chose_as_favorite = models.ManyToManyField(
        CustomUser,
        verbose_name="Избранные рецепты",
        related_name="favorite_recipes",
        blank=True,
    )
    users_put_in_cart = models.ManyToManyField(
        CustomUser,
        verbose_name="Рецепты в корзине",
        related_name="shopping_cart_recipes",
        blank=True,
    )
    image = models.ImageField(
        upload_to=r'recipes/%Y/%m/%d/',
        verbose_name="Изображение",
        unique=False,
        blank=True,
        null=True,
    )
    text = models.TextField(verbose_name="Описание", blank=False, null=False)
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления в минутах",
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    recipe = models.ForeignKey(
        Recipe,
        related_name="amounts_ingredients",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="amounts_ingredients",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return str(self.amount)
