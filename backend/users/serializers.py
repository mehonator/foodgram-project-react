from django.contrib.auth import get_user_model
from rest_framework import serializers

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="pk", read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "id",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    leader = UserSerializer()
    # рецепты


class SubscriptionsSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True)
