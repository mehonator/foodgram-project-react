from users.permissions import IsAdmin
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

CustomUser = get_user_model()


class Pagination(LimitOffsetPagination):
    default_limit = 10
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
    lookup_field = "username"

    def get_permissions(self):
        if (self.action == "list" and self.method in ("GET", "POST")) or (
            self.action == "retrieve" and self.method == "GET"
        ):
            permission_classes = [AllowAny]
        elif self.action == "me":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(
        methods=["GET", "PUT", "PATCH"],
        detail=False,
    )
    def me(self, request):
        if request.method == "GET":
            user_me = self.request.user
            serializer = self.get_serializer(user_me)
            return Response(serializer.data)

        user_me = self.request.user

        serializer = self.get_serializer(
            user_me,
            data=self.request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
