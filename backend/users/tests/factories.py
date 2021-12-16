import factory

from ..models import CustomUser


class CustomUserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"username_{n}")
    email = factory.Sequence(lambda n: f"username_{n}@email.com")
    first_name = factory.Sequence(lambda n: f"Имя_{n}")
    last_name = factory.Sequence(lambda n: f"Фамилия_{n}")

    class Meta:
        model = CustomUser

    @staticmethod
    def user_to_dict(user: CustomUser, request_user: CustomUser) -> dict:
        is_subscribed = user.leader_subscriptions.filter(
            follower=request_user
        ).exists()
        return {
            "email": user.email,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_subscribed": is_subscribed,
        }
