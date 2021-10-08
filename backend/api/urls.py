from api.views import IngredientViewSet, RecipeViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredient")


urlpatterns = [
    path("", include(router.urls)),
]
