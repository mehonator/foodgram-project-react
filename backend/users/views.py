from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomLimitOffsetPagination
