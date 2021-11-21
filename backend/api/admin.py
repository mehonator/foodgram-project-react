from django.contrib import admin

from api.models import AmountIngredient
from api.models import Ingredient
from api.models import MeasurementUnit
from api.models import Recipe
from api.models import Tag


@admin.register(AmountIngredient)
class AmountAdmin(admin.ModelAdmin):
    pass


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


class AmountAdminStackedInline(admin.StackedInline):
    model = AmountIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ("pub_date",)
    inlines = (AmountAdminStackedInline,)
    fields = (
        "name",
        "author",
        "tags",
        "image",
        "text",
        "cooking_time",
    )
