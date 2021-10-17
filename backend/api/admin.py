from django.contrib import admin

from api.models import AmountIngredient, Ingredient, Recipe, Tag


@admin.register(AmountIngredient)
class AmountAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass
