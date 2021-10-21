import base64
from typing import List
import json
from api.models import (
    AmountIngredient,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
)
from api.tests.factories import (
    MeasurementUnitFactory,
    TagFactory,
    IngredientFactory,
    NUMBER_MEASUREMENT_UNITS,
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


URLS = {
    "ingredients": "/api/ingredients/",
    "ingredients-list": "api:ingredients-list",
    "ingredients-detail": "api:ingredients-detail",
    "tags": "/api/tags/",
    "tags-list": "api:tags-list",
    "tags-detail": "api:tags-detail",
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


def generate_users(number) -> List[CustomUser]:
    users = []
    for i in range(len(number)):
        users.append(
            CustomUser.objects.create_user(
                username=f"Test_user{i}",
                email=f"test_user{i}@email.com",
                first_name=f"first_name{i}",
                last_name=f"last_name{i}",
                password=f"password{i}",
            )
        )
    return users


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
        cls.NUMBER_INGREDIENTS = 10

        MeasurementUnitFactory.create_batch(NUMBER_MEASUREMENT_UNITS)
        cls.ingredients = IngredientFactory.create_batch(
            cls.NUMBER_INGREDIENTS
        )

    def test_get_list(self):
        response = IngredientsTests.client.get(
            reverse(URLS["ingredients-list"])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_result = []
        for ingredient in IngredientsTests.ingredients:
            expected_result.append(
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "measurement_unit": ingredient.measurement_unit.name,
                }
            )
        expected_response_data = {
            "count": IngredientsTests.NUMBER_INGREDIENTS,
            "next": None,
            "previous": None,
            "results": expected_result,
        }

        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_response_data,
        )

    def test_get_detail(self):
        ingredient = IngredientsTests.ingredients[0]
        response = IngredientsTests.client.get(
            reverse(URLS["ingredients-detail"], kwargs={"pk": ingredient.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_ingredient = {
            "id": ingredient.id,
            "name": ingredient.name,
            "measurement_unit": ingredient.measurement_unit.name,
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_ingredient,
        )

    def test_search_ingredients(self):
        ingredient = IngredientsTests.ingredients[0]
        response = IngredientsTests.client.get(
            reverse(URLS["ingredients-list"]), {"search": ingredient.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_ingredient = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "measurement_unit": ingredient.measurement_unit.name,
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
        cls.number_tags = 5
        cls.tags = TagFactory.create_batch(cls.number_tags)

    def test_tags_list(self):
        response = IngredientsTests.client.get(URLS["tags"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_result = []
        for tag in TagsTests.tags:
            expected_result.append(
                {
                    "id": tag.id,
                    "color": tag.color,
                    "name": tag.name,
                    "slug": tag.slug,
                }
            )
        expected_response_data = {
            "count": TagsTests.number_tags,
            "next": None,
            "previous": None,
            "results": expected_result,
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_response_data,
        )

    def test_tag_retrieve(self):
        tag = TagsTests.tags[0]
        response = IngredientsTests.client.get(
            reverse(URLS["tags-detail"], kwargs={"pk": tag.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_tag = {
            "id": tag.id,
            "color": tag.color,
            "name": tag.name,
            "slug": tag.slug,
        }
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_tag,
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
        response = RecipesTests.client.get(reverse(URLS["recipes-list"]))
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

    def test_filters(self):
        response = RecipesTests.client.get(
            reverse(URLS["recipes-list"]), tags="zavtrak"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_recipes = {}

        response = RecipesTests.client.get(
            reverse(URLS["recipes-list"]), tags="non-existent-slug"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail(self):
        response = RecipesTests.client.get(
            reverse(URLS["recipes-detail"], args=[1])
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
            path=reverse(URLS["recipes-list"]),
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
            reverse(URLS["recipes-detail"], args=[1]),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        response = RecipesTests.author_client.put(
            path=reverse(URLS["recipes-detail"], args=[1]),
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
            path=reverse(URLS["recipes-detail"], args=[1]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        response = RecipesTests.author_client.delete(
            path=reverse(URLS["recipes-detail"], args=[1]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )


class SubscriptionTest(TestCase):
    pass
