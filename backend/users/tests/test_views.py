import json
import pdb
from django.contrib import auth

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from users.views import Pagination
from users.models import Role
from rest_framework import status

from django.contrib.auth.models import Group

CustomUser = get_user_model()

USERNAME = "Test_urser"
FIRST_NAME = "vasya"
LAST_NAME = "pupkin"
USER_EMAIL = "test_user@email.ru"

ADMIN_USERNAME = "Admin"
ADMIN_EMAIL = "admin@adminemail.com"
ADMIN_FIRST_NAME = "Администратор"
ADMIN_LAST_NAME = "Администраторов"

NAMES_PATHS = {
    "user-list": "/api/users/",
}


class UsersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cls.urls = {
        #     "user-me": reverse(NAMES_PATHS["user-list"]) + "me/",
        #     "user-list": reverse(NAMES_PATHS["user-list"]),
        # }

        cls.user = CustomUser.objects.create_user(
            username=USERNAME,
            email=USER_EMAIL,
            first_name=FIRST_NAME,
            last_name=LAST_NAME,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.admin = CustomUser.objects.create_user(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            first_name=ADMIN_FIRST_NAME,
            last_name=ADMIN_LAST_NAME,
            role=Role.ADMIN,
        )
        cls.admin_client = Client()
        cls.admin_client.force_login(cls.admin)

    def test_me(self):
        """Проверка записи о себе"""
        response = UsersTests.authorized_client.get("/api/users/me/")
        self.assertEqual(
            response.data["username"],
            USERNAME,
            f"Неккоретный username {response.data['username']} {USERNAME}",
        )
        self.assertEqual(response.data["email"], USER_EMAIL)
        self.assertEqual(response.data["first_name"], FIRST_NAME)
        self.assertEqual(response.data["last_name"], LAST_NAME)
        self.assertTrue(response.data.get("id", False))

    def test_get_list(self):
        response = UsersTests.authorized_client.get(NAMES_PATHS["user-list"])
        self.assertEqual(response.status_code, 200)
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
                    'is_subscribed': False,
                    "id": 1,
                },
                {
                    "email": "admin@adminemail.com",
                    "first_name": "Администратор",
                    "id": 2,
                    "last_name": "Администраторов",
                    'is_subscribed': False,
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

        response = UsersTests.authorized_client.get(NAMES_PATHS["user-list"])
        for i in range(1, num_page):
            next_page_url = response.data["next"]
            self.assertIsNotNone(next_page_url, f"Пустая {i} страница")
            response = UsersTests.authorized_client.get(next_page_url)

    def test_regestration_user(self):
        user_data = {
            "username": "testuser",
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "iivanov@email.com",
            "password": "qwerty123da",
        }
        user_json = json.dumps(user_data)
        response = self.client.post(
            NAMES_PATHS["user-list"],
            user_json,
            content_type="application/json",
        )
        self.assertEqual(response.data["username"], user_data["username"])
        self.assertEqual(response.data["email"], user_data["email"])
        self.assertEqual(response.data["first_name"], user_data["first_name"])
        self.assertEqual(response.data["last_name"], user_data["last_name"])
        self.assertTrue(response.data.get("id", False))
