from django.db import transaction
from django.shortcuts import get_list_or_404
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import CharField

from api.models import AmountIngredient
from api.models import CustomUser
from api.models import Ingredient
from api.models import Recipe
from api.models import Tag
from users.serializers import CustomUserSerializer


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


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


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
    tags = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        # the transaction is needed to rollback the creation of amounts
        with transaction.atomic():
            tags_ids = validated_data["tags"]
            tags = get_list_or_404(Tag, pk__in=tags_ids)

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
            tags_ids = validated_data.pop("tags", None)
            if tags_ids:
                tags = get_list_or_404(Tag, pk__in=tags_ids)
                recipe.tags.set(tags)
            
            ingredients = validated_data.pop("ingredients", None)
            if ingredients:
                recipe.amounts_ingredients.all().delete()
                new_amounts_intstance = []
                for ingredient in ingredients:
                    id, amount = ingredient.values()
                    new_amounts_intstance.append(
                        AmountIngredient(
                            amount=amount,
                            recipe=recipe,
                            ingredient=get_object_or_404(
                                Ingredient, pk=id
                            ),
                        )
                    )
                AmountIngredient.objects.bulk_create(new_amounts_intstance)

            for attribute, value in validated_data.items():
                setattr(recipe, attribute, value)
            recipe.save()
        return recipe


class UserWithRecipesSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMinifiedSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, leader) -> bool:
        request = self.context.get("request")
        if request:
            request_user = request.user
        else:
            request_user = self.context["test_request_user"]
        return leader.leader_subscriptions.filter(
            follower=request_user
        ).exists()

    def get_recipes_count(self, leader) -> int:
        return leader.recipes.count()
