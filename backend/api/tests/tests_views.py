from django.contrib.auth import get_user_model
from django.test import TestCase
from users.views import Pagination
from users.models import Role
from api.models import MeasurementUnit, Ingredient
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import pdb

USER = {
    "username": "Test_urser",
    "email": "test_user@email.ru",
    "first_name": "vasya",
    "last_name": "pupkin",
    "password": "password_user",
}
NAMES_PATHS = {
    "ingredients": "/api/ingredients/",
}

MEASUREMENT_UNITS = ["КГ", "Л", "г"]
INGREDIENTS = [
    {"name": "мука", "measurement_unit": "КГ"},
    {"name": "молоко", "measurement_unit": "Л"},
    {"name": "сахар", "measurement_unit": "г"},
]

CustomUser = get_user_model()


def fill_db():
    for measurement_unit in MEASUREMENT_UNITS:
        MeasurementUnit.objects.create(name=measurement_unit)
    for ingredient in INGREDIENTS:
        unit = MeasurementUnit.objects.get(name=ingredient["measurement_unit"])
        Ingredient.objects.create(
            name=ingredient["name"], measurement_unit=unit
        )


class IngredientsTests(TestCase):
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
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.user)
        fill_db()

    def test_get_ingredients(self):
        response = IngredientsTests.client.get(NAMES_PATHS["ingredients"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_list_ingredients = [
            {"id": 1, "name": "мука", "measurement_unit": "КГ"},
            {"id": 2, "name": "молоко", "measurement_unit": "Л"},
            {"id": 3, "name": "сахар", "measurement_unit": "г"},
        ]
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_list_ingredients,
        )

        response = IngredientsTests.client.get(
            NAMES_PATHS["ingredients"] + "1/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_ingredient = {
            "id": 1,
            "name": "мука",
            "measurement_unit": "КГ",
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_ingredient,
        )

    def test_search_ingredients(self):
        response = IngredientsTests.client.get(
            NAMES_PATHS["ingredients"], {"search": "му"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_ingredient = [{
            "id": 1,
            "name": "мука",
            "measurement_unit": "КГ",
        }]
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_ingredient,
        )
    