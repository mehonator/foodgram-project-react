from django.contrib import admin

from api.models import (
    AmountIngredient,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
)


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
    search_fields = ["name"]


class AmountAdminStackedInline(admin.StackedInline):
    model = AmountIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ("pub_date", "count_favorite")
    inlines = (AmountAdminStackedInline,)
    fields = (
        "name",
        "author",
        "count_favorite",
        "tags",
        "image",
        "text",
        "cooking_time",
    )
    search_fields = ["name", "author__username", "tags__name"]
