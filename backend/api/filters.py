import django_filters

from api.constants import IS_FAVORITED_VALUES, IS_IN_SHOPING_CART_VALUES
from api.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter()
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = django_filters.CharFilter(method="get_is_favorited")
    is_in_shopping_cart = django_filters.CharFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited")

    def get_is_favorited(self, queryset, name, value):
        if IS_FAVORITED_VALUES[value]:
            return queryset.filter(users_chose_as_favorite=self.request.user)
        else:
            return queryset.exclude(users_chose_as_favorite=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if IS_IN_SHOPING_CART_VALUES[value]:
            return queryset.filter(users_put_in_cart=self.request.user)
        else:
            return queryset.exclude(users_put_in_cart=self.request.user)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]
