from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

CustomUser = get_user_model()

app_name = "users"

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
