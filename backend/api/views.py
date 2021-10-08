from rest_framework import filters, mixins, viewsets

from api.models import Ingredient, Tag
from api.serializers import IngredientSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pass


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
