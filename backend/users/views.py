from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

CustomUser = get_user_model()


class Pagination(LimitOffsetPagination):
    default_limit = 10
    max_page_size = 100


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination
    #добавить серилизатор сюда
    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
