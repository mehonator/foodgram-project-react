from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

CustomUser = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", "last_name")


class SubscriptionSerializer(serializers.ModelSerializer):
    leader = UserSerializer()
    # рецепты


class SubscriptionsSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True)
