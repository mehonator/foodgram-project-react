from django.contrib.auth import get_user_model
from rest_framework import pagination
from rest_framework.decorators import action

from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination

CustomUser = get_user_model()


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomLimitOffsetPagination
