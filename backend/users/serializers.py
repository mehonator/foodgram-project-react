from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.models import CustomUser


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, current_user):
        user_from_request = self.context["request"].user
        if user_from_request.is_anonymous:
            return False
        return user_from_request.follower_subscriptions.filter(
            leader=current_user
        ).exists()
