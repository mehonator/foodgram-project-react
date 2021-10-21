from django.urls import include, path
from django.urls.conf import re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionCreateDestroy,
    SubscriptionList,
    TagViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router.urls)),
    path("users/subscriptions/", SubscriptionList.as_view()),
    re_path(
        r"users/(?P<user_id>\d+)/subscriptions",
        SubscriptionCreateDestroy.as_view(),
    ),
]
