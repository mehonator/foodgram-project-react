from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

CustomUser = get_user_model()

app_name = "users"

router_v1 = DefaultRouter()
router_v1.register("users", UserViewSet, basename="user")

v1_urls = [
    path("", include(router_v1.urls)),
]

urlpatterns = [
    path("", include(v1_urls)),
]
