from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from api.models import Ingredient, Recipe, Tag
from api.permissions import IsAuthor
from api.serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "list": [AllowAny],
        "retriev": [AllowAny],
        "update": [IsAuthor],
        "destroy": [IsAuthor],
    }

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
        instance = self.get_object()
        update_serializer = RecipeCreateUpdateSerializer(
            instance, data=request.data, partial=False,
        )
        update_serializer.is_valid(raise_exception=True)
        instance = update_serializer.save(author=self.request.user)
        retrieve_serializer = RecipeSerializer(
            instance=instance, *args, **kwargs
        )

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


class IngredientViewSet(ListRetrievDestroyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class TagViewSet(ListRetrievViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
