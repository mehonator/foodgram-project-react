from django.contrib.auth import get_user_model
from rest_framework.decorators import action

from djoser.views import UserViewSet

CustomUser = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(["get"], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
