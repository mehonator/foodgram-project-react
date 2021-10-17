import base64
import pdb
from typing import List
import json
from api.models import (
    AmountIngredient,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
)
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CustomUser = get_user_model()


USER = {
    "username": "Test_urser",
    "email": "test_user@email.ru",
    "first_name": "vasya",
    "last_name": "pupkin",
    "password": "password_user",
}

AUTHOR = {
    "username": "Author",
    "email": "author@email.ru",
    "first_name": "author-first-name",
    "last_name": "author-last-name",
    "password": "password_author",
}

NAMES_URLS = {
    "ingredients": "/api/ingredients/",
    "tags": "/api/tags/",
    "recipes-list": "api:recipes-list",
    "recipes-detail": "api:recipes-detail",
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

IMAGE_BASE64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAAC"
    "Qd1PeAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVIqRewgopCh"
    "umhBVMRRq1CECqFWaNXB5NIPoUlD0uLiKLgWHPxYrDq4OOvq4CoIgh8gbm5Oi"
    "i5S4v+SQosYD4778e7e4+4dINRLTLM6xgBNr5ipRFzMZFfEwCuCCKMHIxiUmW"
    "XMSlISnuPrHj6+3sV4lve5P0e3mrMY4BOJZ5hhVojXiac2KwbnfeIIK8oq8Tn"
    "xqEkXJH7kuuLyG+eCwwLPjJjp1BxxhFgstLHSxqxoasSTxFFV0ylfyLisct7i"
    "rJWqrHlP/sJQTl9e4jrNASSwgEVIEKGgig2UUEGMVp0UCynaj3v4+x2/RC6FX"
    "Btg5JhHGRpkxw/+B7+7tfIT425SKA50vtj2xxAQ2AUaNdv+Prbtxgngfwau9J"
    "a/XAemP0mvtbToERDeBi6uW5qyB1zuAH1PhmzKjuSnKeTzwPsZfVMW6L0Fgqt"
    "ub819nD4AaeoqeQMcHALDBcpe83h3V3tv/55p9vcDiZRysDBSUUwAAAAJcEhZ"
    "cwAALiMAAC4jAXilP3YAAAAHdElNRQflCg8RLAMlUts1AAAAGXRFWHRDb21tZ"
    "W50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAAAxJREFUCNdj+P//PwAF/gL+3M"
    "xZ5wAAAABJRU5ErkJggg=="
)


def create_get_ingredients() -> List[Ingredient]:
    for measurement_unit in MEASUREMENT_UNITS:
        MeasurementUnit.objects.create(name=measurement_unit)
    ingredients = []
    for ingredient in INGREDIENTS:
        unit = MeasurementUnit.objects.get(name=ingredient["measurement_unit"])
        ingredients.append(
            Ingredient.objects.create(
                name=ingredient["name"], measurement_unit=unit
            )
        )
    return ingredients


def create_get_tags() -> List[Tag]:
    tags = []
    for tag in TAGS:
        tags.append(Tag.objects.create(**tag))
    return tags


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
        create_get_ingredients()

    def test_get_ingredients(self):
        response = IngredientsTests.client.get(NAMES_URLS["ingredients"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_list_ingredients = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {"id": 1, "name": "мука", "measurement_unit": "КГ"},
                {"id": 2, "name": "молоко", "measurement_unit": "Л"},
                {"id": 3, "name": "сахар", "measurement_unit": "г"},
            ],
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_list_ingredients,
        )

        response = IngredientsTests.client.get(
            NAMES_URLS["ingredients"] + "1/"
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
            NAMES_URLS["ingredients"], {"search": "му"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_ingredient = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "мука",
                    "measurement_unit": "КГ",
                }
            ],
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_ingredient,
        )


class TagsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = get_auth_clien()
        create_get_tags()

    def test_tags_list(self):
        response = IngredientsTests.client.get(NAMES_URLS["tags"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_list_ingredients = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
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
            ],
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_list_ingredients,
        )

    def test_tag_retrieve(self):
        response = IngredientsTests.client.get(NAMES_URLS["tags"] + "1/")
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


class RecipesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = get_auth_clien()
        ingredients = create_get_ingredients()

        tags = create_get_tags()
        author = CustomUser.objects.create_user(
            username=AUTHOR["username"],
            email=AUTHOR["email"],
            first_name=AUTHOR["first_name"],
            last_name=AUTHOR["last_name"],
            password=AUTHOR["password"],
        )

        cls.author_client = APIClient()
        cls.author_client.force_authenticate(user=author)

        image_format, image_str = IMAGE_BASE64.split(";base64,")
        image_bytes = base64.b64decode(image_str)
        image_content_file = ImageFile(base64.b64decode(image_bytes))
        recipe = Recipe.objects.create(
            name="рецепт",
            author=author,
            image=image_content_file,
            text="хоп-хоп и готово!",
            cooking_time=1,
        )
        recipe.tags.set(tags)
        recipe.save()

        for ingredient in ingredients:
            AmountIngredient.objects.create(
                amount=1, recipe=recipe, ingredient=ingredient
            )

    def test_list(self):
        response = RecipesTests.client.get(reverse(NAMES_URLS["recipes-list"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_recipes = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "рецепт",
                    "tags": [
                        {
                            "id": 1,
                            "name": "Новый год",
                            "color": "#1f00eb",
                            "slug": "novyj-god",
                        },
                        {
                            "id": 2,
                            "name": "Майские",
                            "color": "#ff0505",
                            "slug": "majskie",
                        },
                        {
                            "id": 3,
                            "name": "День рождения",
                            "color": "#fff705",
                            "slug": "den-rozhdenija",
                        },
                    ],
                    "author": {
                        "email": "author@email.ru",
                        "id": 2,
                        "username": "Author",
                        "first_name": "author-first-name",
                        "last_name": "author-last-name",
                        "is_subscribed": False,
                    },
                    "is_favorited": False,
                    "is_in_shopping_cart": False,
                    "ingredients": [
                        {
                            "id": 1,
                            "name": "мука",
                            "measurement_unit": "КГ",
                            "amount": 1.0,
                        },
                        {
                            "id": 2,
                            "name": "молоко",
                            "measurement_unit": "Л",
                            "amount": 1.0,
                        },
                        {
                            "id": 3,
                            "name": "сахар",
                            "measurement_unit": "г",
                            "amount": 1.0,
                        },
                    ],
                    "image": None,
                    "text": "хоп-хоп и готово!",
                    "cooking_time": 1,
                }
            ],
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_recipes,
        )

    def test_detail(self):
        response = RecipesTests.client.get(
            reverse(NAMES_URLS["recipes-detail"], args=[1])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_recipes = {
            "id": 1,
            "name": "рецепт",
            "tags": [
                {
                    "id": 1,
                    "name": "Новый год",
                    "color": "#1f00eb",
                    "slug": "novyj-god",
                },
                {
                    "id": 2,
                    "name": "Майские",
                    "color": "#ff0505",
                    "slug": "majskie",
                },
                {
                    "id": 3,
                    "name": "День рождения",
                    "color": "#fff705",
                    "slug": "den-rozhdenija",
                },
            ],
            "author": {
                "email": "author@email.ru",
                "id": 2,
                "username": "Author",
                "first_name": "author-first-name",
                "last_name": "author-last-name",
                "is_subscribed": False,
            },
            "is_favorited": False,
            "is_in_shopping_cart": False,
            "ingredients": [
                {
                    "id": 1,
                    "name": "мука",
                    "measurement_unit": "КГ",
                    "amount": 1.0,
                },
                {
                    "id": 2,
                    "name": "молоко",
                    "measurement_unit": "Л",
                    "amount": 1.0,
                },
                {
                    "id": 3,
                    "name": "сахар",
                    "measurement_unit": "г",
                    "amount": 1.0,
                },
            ],
            "image": None,
            "text": "хоп-хоп и готово!",
            "cooking_time": 1,
        }

        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_recipes,
        )

    def test_create(self):
        create_data = {
            "name": "Нечто восхитительное",
            "tags": [
                {"id": 1},
            ],
            "ingredients": [
                {"id": 1, "amount": 10},
            ],
            "image": IMAGE_BASE64,
            "text": (
                "Чтобы приготовить Нечто восхитительное,"
                " необходимо всего лишь...."
            ),
            "cooking_time": 42,
        }
        expected_data = {
            "id": 2,
            "name": "Нечто восхитительное",
            "tags": [
                {
                    "id": 1,
                    "name": "Новый год",
                    "color": "#1f00eb",
                    "slug": "novyj-god",
                }
            ],
            "author": {
                "email": "author@email.ru",
                "id": 2,
                "username": "Author",
                "first_name": "author-first-name",
                "last_name": "author-last-name",
                "is_subscribed": False,
            },
            "is_favorited": False,
            "is_in_shopping_cart": False,
            "ingredients": [
                {
                    "id": 1,
                    "name": "мука",
                    "measurement_unit": "КГ",
                    "amount": 10.0,
                }
            ],
            "image": "random-url",
            "text": (
                "Чтобы приготовить Нечто восхитительное,"
                " необходимо всего лишь...."
            ),
            "cooking_time": 42,
        }
        response = RecipesTests.author_client.post(
            path=reverse(NAMES_URLS["recipes-list"]),
            data=json.dumps(create_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        response_data_without_image = response.data.copy()
        response_data_without_image.pop("image")
        expected_data_without_image = expected_data.copy()
        expected_data_without_image.pop("image")
        self.assertJSONEqual(
            json.dumps(response_data_without_image),
            expected_data_without_image,
        )

    def test_update(self):
        update_data = {
            "name": "Теперь тут плов",
            "tags": [
                {"id": 1},
            ],
            "ingredients": [
                {"id": 1, "amount": 2},
            ],
            "image": IMAGE_BASE64,
            "text": "Охапка дров и плов готов!",
            "cooking_time": 10,
        }
        expected_data = {
            "id": 1,
            "name": "Теперь тут плов",
            "tags": [
                {
                    "id": 1,
                    "name": "Новый год",
                    "color": "#1f00eb",
                    "slug": "novyj-god",
                }
            ],
            "author": {
                "email": "author@email.ru",
                "id": 2,
                "username": "Author",
                "first_name": "author-first-name",
                "last_name": "author-last-name",
                "is_subscribed": False,
            },
            "is_favorited": False,
            "is_in_shopping_cart": False,
            "ingredients": [
                {
                    "id": 1,
                    "name": "мука",
                    "measurement_unit": "КГ",
                    "amount": 2.0,
                }
            ],
            "image": "random-url",
            "text": "Охапка дров и плов готов!",
            "cooking_time": 10,
        }
        response = RecipesTests.client.put(
            reverse(NAMES_URLS["recipes-detail"], args=[1]),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        response = RecipesTests.author_client.put(
            path=reverse(NAMES_URLS["recipes-detail"], args=[1]),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        response_data_without_image = response.data.copy()
        response_data_without_image.pop("image")
        expected_data_without_image = expected_data.copy()
        expected_data_without_image.pop("image")
        self.assertJSONEqual(
            json.dumps(response_data_without_image),
            expected_data_without_image,
        )

    def test_delete(self):
        response = RecipesTests.client.delete(
            path=reverse(NAMES_URLS["recipes-detail"], args=[1]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        response = RecipesTests.author_client.delete(
            path=reverse(NAMES_URLS["recipes-detail"], args=[1]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
