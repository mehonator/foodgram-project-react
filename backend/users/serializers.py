from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

CustomUser = get_user_model()


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
        user_from_request = self.context['request'].user
        return user_from_request.follower.filter(leader=current_user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    leader = UserSerializer()
    # рецепты


class SubscriptionsSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True)
