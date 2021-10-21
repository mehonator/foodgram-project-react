from django.contrib.auth import get_user_model
import django_filters
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import CustomUser, Ingredient, Recipe, Subscription, Tag
from api.permissions import IsAuthor
from api.serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    TagSerializer,
    LeaderSubscriptionSerializer,
)

CustomUser = get_user_model()


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

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited")

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                users_chose_as_favorite=self.request.user
            )
        return Recipe.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipeSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "list": [AllowAny],
        "retriev": [AllowAny],
        "update": [IsAuthor],
        "destroy": [IsAuthor],
    }
    filter_class = RecipeFilter

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

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT"):
            return RecipeCreateUpdateSerializer
        else:
            return RecipeSerializer

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            permissions = []
            for permission in self.permission_classes_by_action[self.action]:
                permissions.append(permission())
            return permissions
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


class IngredientViewSet(ListRetrievDestroyViewSet):
    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class TagViewSet(ListRetrievViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class SubscriptionList(ListAPIView):
    serializer_class = LeaderSubscriptionSerializer

    def get_queryset(self):
        leaders = CustomUser.objects.filter(
            leader_subscriptions__follower=self.request.user
        ).all()
        return leaders


class SubscriptionCreateDestroy(GenericAPIView):
    def get(self, request, user_id):
        leader = get_object_or_404(CustomUser, id=user_id)

        subscription = Subscription.objects.create(
            follower=request.user, leader=leader
        )
        serializer = LeaderSubscriptionSerializer(
            data=request.data, instance=subscription
        )
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscription = get_object_or_404(
            Subscription, follower=request.user, leader_id=user_id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
