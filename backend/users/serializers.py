from django.contrib.auth import get_user_model
from rest_framework import serializers

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
        )
