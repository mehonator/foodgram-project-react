import pdb

from api.models import Ingredient, MeasurementUnit, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

USER = {
    "username": "Test_urser",
    "email": "test_user@email.ru",
    "first_name": "vasya",
    "last_name": "pupkin",
    "password": "password_user",
}
NAMES_PATHS = {
    "ingredients": "/api/ingredients/",
    "tags": "/api/tags/",
}

MEASUREMENT_UNITS = ["КГ", "Л", "г"]
INGREDIENTS = [
    {"name": "мука", "measurement_unit": "КГ"},
    {"name": "молоко", "measurement_unit": "Л"},
    {"name": "сахар", "measurement_unit": "г"},
]
TAGS = [
    {"name": "Новый год", "color": "#1f00eb"},
    {"name": "Майские", "color": "#ff0505"},
    {"name": "День рождения", "color": "#fff705"},
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
    for tag in TAGS:
        Tag.objects.create(**tag)


def get_auth_clien() -> APIClient:
    user = CustomUser.objects.create_user(
        username=USER["username"],
        email=USER["email"],
        first_name=USER["first_name"],
        last_name=USER["last_name"],
        password=USER["password"],
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class IngredientsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = get_auth_clien()
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
        expected_ingredient = [
            {
                "id": 1,
                "name": "мука",
                "measurement_unit": "КГ",
            }
        ]
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_ingredient,
        )


class TagsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = get_auth_clien()
        fill_db()

    def test_tags_list(self):
        response = IngredientsTests.client.get(NAMES_PATHS["tags"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_list_ingredients = [
            {
                "id": 1,
                "color": "#1f00eb",
                "name": "Новый год",
                "slug": "novyj-god",
            },
            {
                "id": 2,
                "color": "#ff0505",
                "name": "Майские",
                "slug": "majskie",
            },
            {
                "id": 3,
                "color": "#fff705",
                "name": "День рождения",
                "slug": "den-rozhdenija",
            },
        ]
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_list_ingredients,
        )

    def test_tag_retrieve(self):
        response = IngredientsTests.client.get(NAMES_PATHS["tags"] + "1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_list_ingredients = {
            "id": 1,
            "color": "#1f00eb",
            "name": "Новый год",
            "slug": "novyj-god",
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_list_ingredients,
        )
