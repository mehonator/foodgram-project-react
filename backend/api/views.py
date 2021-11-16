from collections import namedtuple, OrderedDict
from enum import Enum
from typing import List
import io
from django.http.response import FileResponse

from fpdf import FPDF
import django_filters
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.models import CustomUser, Ingredient, Recipe, Subscription, Tag
from api.permissions import IsAuthor
from api.serializers import (
    IngredientSerializer,
    UserWithRecipesSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    TagSerializer,
)

CustomUser = get_user_model()


class IsFavoritedEnum(Enum):
    no = 0
    yes = 1


class IsShopingCartEnum(Enum):
    no = 0
    yes = 1


ValidationResult = namedtuple(
    "ValidationResult", ["is_valid", "query_param", "error_msg"]
)


def validate_query_params(validators: List):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            params_errors = {}
            for validate in validators:
                validation = validate(self)
                if not validation.is_valid:
                    params_errors[
                        validation.query_param
                    ] = validation.error_msg

            if params_errors:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=params_errors,
                )

            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class ListRetrievDestroyViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class ListRetrievViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter()
    tags = django_filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = django_filters.NumberFilter(method="get_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited")

    def get_is_favorited(self, queryset, name, value):
        if value == IsFavoritedEnum.yes.value:
            return queryset.filter(users_chose_as_favorite=self.request.user)
        elif value == IsFavoritedEnum.no.value:
            return queryset.exclude(users_chose_as_favorite=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == IsShopingCartEnum.yes.value:
            return queryset.filter(users_put_in_cart=self.request.user)
        elif value == IsShopingCartEnum.no.value:
            return queryset.exclude(users_put_in_cart=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipeSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "list": [AllowAny],
        "retriev": [AllowAny],
        "update": [IsAuthor],
        "destroy": [IsAuthor],
        "favorite": [IsAuthenticated],
    }
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT"):
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
        is_favorited = self.request.query_params.get("is_favorited", None)
        is_favorited_values = [enum.value for enum in IsFavoritedEnum]
        if is_favorited and int(is_favorited) not in is_favorited_values:
            return ValidationResult(
                False, "is_favorited", "Invalid value. Acceptable 0 and 1"
            )
        return ValidationResult(True, "is_favorited", "")

    def validate_is_in_shoping_cart(self):
        is_in_shoping_cart = self.request.query_params.get(
            "is_in_shoping_cart", None
        )
        is_in_shoping_cart_values = [enum.value for enum in IsShopingCartEnum]
        if (
            is_in_shoping_cart
            and int(is_in_shoping_cart) not in is_in_shoping_cart_values
        ):
            return ValidationResult(
                False,
                "is_in_shoping_cart",
                "Invalid value. Acceptable 0 and 1",
            )
        return ValidationResult(True, "is_in_shoping_cart", "")

    @validate_query_params(
        [validate_is_favorited, validate_is_in_shoping_cart]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        create_serializer = RecipeCreateUpdateSerializer(
            data=request.data, *args, **kwargs
        )
        create_serializer.is_valid(raise_exception=True)
        recipe = create_serializer.save(author=self.request.user)

        retrieve_serializer = RecipeSerializer(
            instance=recipe, *args, **kwargs
        )
        headers = self.get_success_headers(retrieve_serializer.data)
        return Response(
            retrieve_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        kwargs.pop("pk")

        instance = self.get_object()
        update_serializer = RecipeCreateUpdateSerializer(
            instance,
            data=request.data,
            partial=False,
        )
        update_serializer.is_valid(raise_exception=True)
        instance = update_serializer.save(author=self.request.user)
        retrieve_serializer = RecipeSerializer(
            instance=instance, data=request.data, *args, **kwargs
        )
        retrieve_serializer.is_valid(raise_exception=True)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(retrieve_serializer.data)

    @action(detail=True, methods=["get", "delete"], url_name="favorite")
    def favorite(self, request, pk=None):
        recipe_queryset = Recipe.objects.filter(pk=pk)
        if not recipe_queryset.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "the recipe isn't exists"},
            )

        recipe = recipe_queryset[0]
        users_favorite = recipe.users_chose_as_favorite
        if request.method == "GET":
            if users_favorite.filter(pk=request.user.pk).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "errors": "the recipe has already"
                        "been added to favorites"
                    },
                )

            users_favorite.add(request.user)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                status=status.HTTP_201_CREATED, data=serializer.data
            )

        else:
            if not users_favorite.filter(pk=request.user.pk).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Recipe not added to favorites"},
                )
            users_favorite.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get", "delete"], url_name="shopping_cart")
    def shopping_cart(self, request, pk=None):
        recipe_queryset = Recipe.objects.filter(pk=pk)
        if not recipe_queryset.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "the recipe isn't exists"},
            )

        recipe = recipe_queryset[0]
        users_putted_in_cart = recipe.users_put_in_cart
        if request.method == "GET":
            if users_putted_in_cart.filter(pk=request.user.pk).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "errors": "the recipe has already"
                        "been added to shopping cart"
                    },
                )

            users_putted_in_cart.add(request.user)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                status=status.HTTP_201_CREATED, data=serializer.data
            )

        else:
            if not users_putted_in_cart.filter(pk=request.user.pk).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Recipe not added to shopping cart"},
                )
            users_putted_in_cart.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_accumulated_ingredients(self, recipes) -> OrderedDict:
        ingredients = {}
        for recipe in recipes:
            for amount_ingredient in recipe.amounts_ingredients.all():
                name = f"{amount_ingredient.ingredient.name}"
                amount = amount_ingredient.amount
                measurement_unit = (
                    amount_ingredient.ingredient.measurement_unit.name
                )

                ingredient = ingredients.get(name, None)
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
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class TagViewSet(ListRetrievViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class SubscriptionList(ListAPIView):
    serializer_class = UserWithRecipesSerializer

    def get_queryset(self):
        leaders = CustomUser.objects.filter(
            leader_subscriptions__follower=self.request.user
        ).all()
        return leaders


class SubscriptionCreateDestroy(GenericAPIView):
    def get(self, request, user_id):
        kwargs = {"context": self.get_serializer_context()}
        leader = get_object_or_404(CustomUser, id=user_id)

        Subscription.objects.create(follower=request.user, leader=leader)
        serializer = UserWithRecipesSerializer(instance=leader, **kwargs)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscription = get_object_or_404(
            Subscription, follower=request.user, leader_id=user_id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
