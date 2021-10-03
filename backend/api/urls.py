from api.views import RecipeViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("users", RecipeViewSet, basename="user")

v1_urls = [
    path("", include(router_v1.urls)),
]

urlpatterns = [
    path("", include(v1_urls)),
]
