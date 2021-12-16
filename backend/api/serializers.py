from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import CharField

from api.fields import PrimaryKeyRelatedFieldAlternative
from api.models import AmountIngredient, Ingredient, Recipe, Tag
from api.utilis import is_distinct
from users.models import CustomUser
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
    id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Ingredient.objects.all()
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


class AmountIngredientRecipeCreateUpdateSerializer(
    serializers.ModelSerializer
):
    id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Ingredient.objects.all()
    )
    amount = serializers.FloatField(required=True)

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "amount",
        )


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
    ingredients = AmountIngredientRecipeSerializer(
        source="amounts_ingredients", many=True
    )
    tags = PrimaryKeyRelatedFieldAlternative(
        queryset=Tag.objects.all(),
        serializer=TagSerializer,
        many=True,
    )

    def save_ingredients(self, recipe, amounts_ingredients):
        amounts_instance = []
        for amount_ingredient in amounts_ingredients:
            amount = amount_ingredient["amount"]
            ingredient = amount_ingredient["id"]
            amounts_instance.append(
                AmountIngredient(
                    amount=amount,
                    recipe=recipe,
                    ingredient=ingredient,
                )
            )
        AmountIngredient.objects.bulk_create(amounts_instance)

    def create(self, validated_data):
        # the transaction is needed to rollback the creation of amounts
        with transaction.atomic():
            amounts_ingredients = validated_data.pop("amounts_ingredients")
            saved_recipe = super().create(validated_data)
            self.save_ingredients(saved_recipe, amounts_ingredients)
        return saved_recipe

    def update(self, recipe, validated_data):
        # the transaction is needed to rollback the creation of amounts
        with transaction.atomic():
            amounts_ingredients = validated_data.pop("amounts_ingredients")
            saved_recipe = super().update(recipe, validated_data)
            if amounts_ingredients:
                saved_recipe.amounts_ingredients.all().delete()
                self.save_ingredients(recipe, amounts_ingredients)
        return saved_recipe

    def validate_ingredients(self, amounts_ingredients):
        ids_ingredients = [i["id"] for i in amounts_ingredients]
        if not is_distinct(ids_ingredients):
            raise serializers.ValidationError(
                "This field must be an unique ids of ingredients."
            )
        for amount_ingredient in amounts_ingredients:
            if amount_ingredient["amount"] < 0:
                raise serializers.ValidationError(
                    "This field must be an positive amount of ingredients."
                )
        return amounts_ingredients

    def validate_tags(self, ids_tags):
        if not is_distinct(ids_tags):
            raise serializers.ValidationError(
                "This field must be an unique ids of tags."
            )
        return ids_tags

    def validate_cooking_time(self, cooking_times):
        if cooking_times < 0:
            raise serializers.ValidationError(
                "This field must be positive."
            )
        return cooking_times


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
