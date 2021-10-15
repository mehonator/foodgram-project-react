from django.db import transaction
from django.db.models.query import QuerySet
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import CharField
from users.serializers import CustomUserSerializer

from api.models import (
    AmountIngredient,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
)


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        optional_fields = ["color", "slug"]


class AmountIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="ingredient"
    )
    name = CharField(read_only=True, source="ingredient.name")
    measurement_unit = CharField(
        read_only=True, source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class AmountIngredientRecipeCreateUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.FloatField(required=True)


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = AmountIngredientRecipeSerializer(
        source="amounts_ingredients", many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "ingredients",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, current_recipe):
        user = self.context["request"].user
        return current_recipe.users_chose_as_favorite.filter(
            id=user.pk
        ).exists()

    def get_is_in_shopping_cart(self, current_recipe):
        user = self.context["request"].user
        return current_recipe.users_put_in_cart.filter(id=user.pk).exists()


class RecipeCreateUpdateSerializer(RecipeSerializer):
    ingredients = AmountIngredientRecipeCreateUpdateSerializer(many=True)

    def create(self, validated_data):
        # the transaction is needed to rollback the creation of amounts
        with transaction.atomic():
            ids_tags = [ord_dict["id"] for ord_dict in validated_data["tags"]]
            tags = get_list_or_404(Tag, pk__in=ids_tags)

            recipe = Recipe.objects.create(
                author=self.context["request"].user,
                name=validated_data["name"],
                image=validated_data["image"],
                text=validated_data["text"],
                cooking_time=validated_data["cooking_time"],
            )

            amounts_instance = []
            for ingredient_data in validated_data["ingredients"]:
                amount = ingredient_data["amount"]
                amounts_instance.append(
                    AmountIngredient(
                        amount=amount,
                        recipe=recipe,
                        ingredient=Ingredient.objects.get(
                            pk=ingredient_data["id"]
                        ),
                    )
                )
            AmountIngredient.objects.bulk_create(amounts_instance)
            recipe.tags.set(tags)

        return recipe

    def update(self, recipe, validated_data):
        # the transaction is needed to rollback the creation of amounts
        with transaction.atomic():
            pks_tags = [ord_dict["id"] for ord_dict in validated_data["tags"]]
            tags = get_list_or_404(Tag, pk__in=pks_tags)

            old_amounts_intstance = recipe.amounts_ingredients.all()
            old_amounts_intstance.delete()

            new_amounts_intstance = []
            for ingredient_data in validated_data["ingredients"]:
                amount = ingredient_data["amount"]
                new_amounts_intstance.append(
                    AmountIngredient(
                        amount=amount,
                        recipe=recipe,
                        ingredient=get_object_or_404(
                            Ingredient, pk=ingredient_data["id"]
                        ),
                    )
                )

            AmountIngredient.objects.bulk_create(new_amounts_intstance)
            recipe.name = validated_data["name"]
            recipe.image = validated_data["image"]
            recipe.text = validated_data["text"]
            recipe.cooking_time = validated_data["cooking_time"]
            recipe.tags.set(tags)
            recipe.save()

        return recipe
