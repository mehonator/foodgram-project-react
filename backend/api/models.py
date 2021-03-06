from autoslug import AutoSlugField
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import CheckConstraint
from django.db.models.query_utils import Q

from api.utilis import transliterate_slugify
from users.models import CustomUser


class MeasurementUnit(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=128,
        unique=True,
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=512)
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name="Единица измерения",
        related_name="ingredients",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} {self.measurement_unit.name}"


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=512,
        unique=True,
    )
    color = ColorField(
        verbose_name="Цвет", format="hexa", blank=True, null=True
    )
    slug = AutoSlugField(
        verbose_name="Слаг",
        populate_from="name",
        slugify=transliterate_slugify,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=512,
        unique=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes",
        blank=True,
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор",
        related_name="recipes",
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
        upload_to=r"recipes/%Y/%m/%d/",
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления в минутах",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

    @property
    def count_favorite(self) -> int:  # noqa CCE001
        return self.users_put_in_cart.count()

    count_favorite.fget.short_description = "Количество добавлений в избранное"


class AmountIngredient(models.Model):
    amount = models.FloatField(
        validators=[MinValueValidator(0.0)], verbose_name="Количество"
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="amounts_ingredients",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="amounts_ingredients",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["recipe", "-amount", "ingredient"]
        verbose_name = "Количество ингредиентов"
        verbose_name_plural = "Количество ингредиентов"
        constraints = (
            CheckConstraint(check=Q(amount__gte=0.0), name="positive amount"),
        )

    def __str__(self):
        return f"{self.recipe.name} {self.ingredient} {self.amount}"


class Subscription(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        related_name="follower_subscriptions",
        verbose_name="подписчик",
        on_delete=models.CASCADE,
    )
    leader = models.ForeignKey(
        CustomUser,
        related_name="leader_subscriptions",
        verbose_name="Лидер",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "leader"], name="unique subscription"
            )
        ]

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.follower.get_username()}-{self.leader.get_username()}"

    def clean(self):
        if self.follower == self.leader:
            errors = {}
            errors["follower"] = "User cannot subscribe to himself"
            raise ValidationError(errors)
