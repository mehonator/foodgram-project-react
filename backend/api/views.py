import io
from collections import OrderedDict

from django.http.response import FileResponse
from fpdf import FPDF
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.constants import IS_FAVORITED_VALUES, IS_IN_SHOPING_CART_VALUES
from api.filters import IngredientFilter, RecipeFilter
from api.mixins import ListRetrievViewSet
from api.models import AmountIngredient, Ingredient, Recipe, Subscription, Tag
from api.pagintors import CustomLimitOffsetPagination
from api.permissions import IsAuthor
from api.serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    TagSerializer,
    UserWithRecipesSerializer,
)
from api.validations import ValidationResult, validate_query_params
from users.models import CustomUser


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipeSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "update": [IsAuthor],
        "partial_update": [IsAuthor],
        "destroy": [IsAuthor],
        "favorite": [IsAuthenticated],
    }
    filter_class = RecipeFilter
    pagination_class = CustomLimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return RecipeCreateUpdateSerializer
        else:
            return RecipeSerializer

    def get_permissions(self):
        try:
            permissions = []
            for permission in self.permission_classes_by_action[self.action]:
                permissions.append(permission())
            return permissions
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def validate_is_favorited(self):
        is_favorited: str = self.request.query_params.get("is_favorited")
        if is_favorited and is_favorited not in IS_FAVORITED_VALUES:
            return ValidationResult(
                False,
                "is_favorited",
                "Invalid value. Acceptable 'true' and 'false'",
            )
        return ValidationResult(True, "is_favorited", "")

    def validate_is_in_shoping_cart(self):
        is_in_shoping_cart: str = self.request.query_params.get(
            "is_in_shoping_cart"
        )
        if (
            is_in_shoping_cart
            and is_in_shoping_cart not in IS_IN_SHOPING_CART_VALUES
        ):
            return ValidationResult(
                False,
                "is_in_shoping_cart",
                "Invalid value. Acceptable 'true' and 'false",
            )
        return ValidationResult(True, "is_in_shoping_cart", "")

    @validate_query_params(
        [validate_is_favorited, validate_is_in_shoping_cart]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def add_recipe_in_category(
        self, queryset_users, curent_user, recipe
    ) -> Response:
        if queryset_users.filter(pk=curent_user.pk).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "the recipe has already been added"},
            )

        queryset_users.add(curent_user)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    def del_recipe_from_category(
        self, queryset_users, curent_user
    ) -> Response:
        if not queryset_users.filter(pk=curent_user.pk).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "Recipe not added"},
            )
        queryset_users.remove(curent_user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_recipe_category(
        self, request, recipe_pk, related_name_category: str
    ) -> Response:
        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "the recipe isn't exists"},
            )

        category_users = getattr(recipe, related_name_category)
        if request.method == "GET":
            return self.add_recipe_in_category(
                category_users, request.user, recipe
            )

        else:
            return self.del_recipe_from_category(category_users, request.user)

    @action(detail=True, methods=["get", "delete"], url_name="favorite")
    def favorite(self, request, pk=None):
        return self.handle_recipe_category(
            request, pk, "users_chose_as_favorite"
        )

    @action(detail=True, methods=["get", "delete"], url_name="shopping_cart")
    def shopping_cart(self, request, pk=None):
        return self.handle_recipe_category(request, pk, "users_put_in_cart")

    def get_accumulated_ingredients(self, recipes) -> OrderedDict:
        ingredients = {}
        amounts_ingredients = AmountIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            "amount", "ingredient__name", "ingredient__measurement_unit__name"
        )
        for amount_ingredient in amounts_ingredients:
            name = f"{amount_ingredient['ingredient__name']}"
            amount = amount_ingredient["amount"]
            measurement_unit = amount_ingredient[
                "ingredient__measurement_unit__name"
            ]

            ingredient = ingredients.get(name)
            if ingredient:
                ingredient["amount"] += amount
            else:
                ingredients[name] = {
                    "amount": amount,
                    "measurement_unit": measurement_unit,
                }

        return OrderedDict(
            sorted(ingredients.items(), key=lambda item: item[0])
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        recipes = request.user.shopping_cart_recipes.all()
        ingredients_amounts = self.get_accumulated_ingredients(recipes)
        pdf = FPDF()

        pdf.add_font(
            "DejaVu", "", "./api/fonts/DejaVuSansCondensed.ttf", uni=True
        )
        pdf.set_font("DejaVu", "", 14)
        pdf.add_page()
        for ingredient_name, amount_measurement in ingredients_amounts.items():
            text = (
                f'{ingredient_name} {amount_measurement["amount"]}'
                f' {amount_measurement["measurement_unit"]}'
            )
            pdf.cell(0, 10, txt=text, ln=1)

        string_file = pdf.output(dest="S")
        response = FileResponse(
            io.BytesIO(string_file.encode("latin1")),
            content_type="application/pdf",
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopong-list.pdf"'

        return response


class IngredientViewSet(ListRetrievViewSet):
    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_class = IngredientFilter


class TagViewSet(ListRetrievViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class SubscriptionList(ListAPIView):
    serializer_class = UserWithRecipesSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        leaders = CustomUser.objects.filter(
            leader_subscriptions__follower=self.request.user
        ).all()
        return leaders


class SubscriptionCreateDestroy(GenericAPIView):
    def delete(self, request, user_id):
        subscription = get_object_or_404(
            Subscription, follower=request.user, leader_id=user_id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, user_id):
        kwargs = {"context": self.get_serializer_context()}
        leader = get_object_or_404(CustomUser, id=user_id)

        Subscription.objects.create(follower=request.user, leader=leader)
        serializer = UserWithRecipesSerializer(instance=leader, **kwargs)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
