from django.shortcuts import render
from rest_framework import mixins, viewsets
from api.models import Ingredient
from api.serializers import IngredientSerializer
from rest_framework import filters


class RecipeViewSet(viewsets.ModelViewSet):
    pass


class ListAndRetrievViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class IngredientViewSet(ListAndRetrievViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
