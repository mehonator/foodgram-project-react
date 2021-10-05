from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination

CustomUser = get_user_model()


class Pagination(LimitOffsetPagination):
    default_limit = 10
    max_page_size = 100


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination
