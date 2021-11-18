from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import Role
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.views import CustomLimitOffsetPagination as Pagination

CustomUser = get_user_model()

USER = {
    "username": "Test_urser",
    "email": "test_user@email.ru",
    "first_name": "vasya",
    "last_name": "pupkin",
    "password": "password_user",
}

ADMIN = {
    "username": "Admin",
    "email": "admin@adminemail.com",
    "first_name": "Администратор",
    "last_name": "Администраторов",
    "password": "password_admin",
}
NAMES_PATHS = {
    "user-list": "/api/users/",
    "user-me": "/api/users/me/",
    "reset_password": "/api/users/set_password/",
    "login": "/api/auth/token/login/",
    "logout": "/api/auth/token/logout/",
    "my-subscriptions": "/api/users/subscriptions/",
}


class UsersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = CustomUser.objects.create_user(
            username=USER["username"],
            email=USER["email"],
            first_name=USER["first_name"],
            last_name=USER["last_name"],
            password=USER["password"],
        )
        token = Token.objects.create(user=cls.user)
        cls.auth_user_client = APIClient()
        cls.auth_user_client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )
        cls.admin = CustomUser.objects.create_user(
            username=ADMIN["username"],
            email=ADMIN["email"],
            first_name=ADMIN["first_name"],
            last_name=ADMIN["last_name"],
            role=Role.ADMIN,
        )

    def test_me(self):
        """Проверка записи о себе"""
        response = UsersTests.auth_user_client.get(NAMES_PATHS["user-me"])
        self.assertEqual(
            response.data["username"], USER["username"], "Неккоретный username"
        )
        self.assertEqual(response.data["email"], USER["email"])
        self.assertEqual(response.data["first_name"], USER["first_name"])
        self.assertEqual(response.data["last_name"], USER["last_name"])
        self.assertTrue(response.data.get("id", False))

    def test_get_list(self):
        response = UsersTests.auth_user_client.get(NAMES_PATHS["user-list"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        except_json = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "first_name": "vasya",
                    "last_name": "pupkin",
                    "username": "Test_urser",
                    "email": "test_user@email.ru",
                    "is_subscribed": False,
                    "id": 1,
                },
                {
                    "email": "admin@adminemail.com",
                    "first_name": "Администратор",
                    "id": 2,
                    "last_name": "Администраторов",
                    "is_subscribed": False,
                    "username": "Admin",
                },
            ],
        }
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            except_json,
            "неверный JSON ответ",
        )

    def generate_users(self, number):
        users = []
        for i in range(number):
            users.append(
                CustomUser(
                    username=f"Тестюзер{i}",
                    first_name=f"Имя{i}",
                    last_name=f"Фамилия{i}",
                    email=f"testuser{i}@email.com",
                )
            )
        CustomUser.objects.bulk_create(users)

    def test_pagination(self):
        num_users = 50
        num_page = 50 // Pagination.default_limit
        self.generate_users(num_users)

        response = UsersTests.auth_user_client.get(NAMES_PATHS["user-list"])
        for i in range(1, num_page):
            next_page_url = response.data["next"]
            self.assertIsNotNone(next_page_url, f"Пустая {i} страница")
            response = UsersTests.auth_user_client.get(next_page_url)

    def test_regestration_user(self):
        user_data = {
            "username": "testuser",
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "iivanov@email.com",
            "password": "qwerty123da",
        }
        anonymous_client = APIClient()
        response = anonymous_client.post(
            NAMES_PATHS["user-list"],
            user_data,
            format="json",
        )
        self.assertEqual(response.data["username"], user_data["username"])
        self.assertEqual(response.data["email"], user_data["email"])
        self.assertEqual(response.data["first_name"], user_data["first_name"])
        self.assertEqual(response.data["last_name"], user_data["last_name"])
        self.assertTrue(response.data.get("id", False))

    def test_get_token(self):
        client = APIClient()
        response = client.post(
            NAMES_PATHS["login"],
            {"email": USER["email"], "password": USER["password"]},
            format="json",
        )
        self.assertIsNotNone(response.data.get("auth_token", None))
        token = response.data["auth_token"]
        response = client.get(
            NAMES_PATHS["user-list"], HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_token(self):
        client = APIClient()
        response = client.post(
            NAMES_PATHS["login"],
            {"email": USER["email"], "password": USER["password"]},
            format="json",
        )
        token = response.data["auth_token"]
        self.assertTrue(Token.objects.filter(key=token).exists())
        client.post(NAMES_PATHS["logout"], HTTP_AUTHORIZATION=f"Token {token}")
        self.assertFalse(Token.objects.filter(key=token).exists())

    def test_reset_password(self):
        response = UsersTests.auth_user_client.post(
            NAMES_PATHS["reset_password"],
            {
                "new_password": "new_password",
                "current_password": USER["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_my_subscriptions(self):
        response = UsersTests.auth_user_client.get(
            NAMES_PATHS["my-subscriptions"],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
