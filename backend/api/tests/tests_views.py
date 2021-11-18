import base64
from collections import namedtuple
import json
import shutil
from os.path import basename
from typing import Dict, List

from api.models import Recipe, Tag, Subscription
from api.serializers import RecipeMinifiedSerializer, UserWithRecipesSerializer
from api.tests.factories import (
    NUMBER_MEASUREMENT_UNITS,
    AmountIngredientFactory,
    IngredientFactory,
    MeasurementUnitFactory,
    RecipeFactory,
    TagFactory,
)

from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.tests.factories import CustomUserFactory

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
    "ingredients-list": "api:ingredients-list",
    "ingredients-detail": "api:ingredients-detail",
    "tags-list": "api:tags-list",
    "tags-detail": "api:tags-detail",
    "recipes-list": "api:recipes-list",
    "recipes-detail": "api:recipes-detail",
    "recipes-favorite": "api:recipes-favorite",
    "recipes-shopping_cart": "api:recipes-shopping_cart",
    "subscriptions-list": "api:subscriptions-list",
    "subscriptions-detail": "api:subscriptions-detail",
}

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

MEDIA_PATH = "./test_media/"

TestRequest = namedtuple("TestRequest", ("user",))


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


def get_recipe_img_basename(recipe: dict) -> dict:
    recipe_img_basename = recipe.copy()
    image_path = recipe["image"]
    # при отстутсвии файла response возвращает None, модель ""
    # всё приводим к None
    if image_path in ("", None):
        recipe_img_basename["image"] = None
    else:
        recipe_img_basename["image"] = basename(image_path)
    return recipe_img_basename


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

        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_result,
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
        response = IngredientsTests.client.get(reverse(URLS["tags-list"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tags_dicts = [TagFactory.to_dict(tag) for tag in TagsTests.tags]
        expected_response_data = {
            "count": TagsTests.number_tags,
            "next": None,
            "previous": None,
            "results": tags_dicts,
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

        expected_data = TagFactory.to_dict(tag)
        self.assertJSONEqual(
            str(response.content, "utf8"),
            expected_data,
        )


@override_settings(MEDIA_ROOT=MEDIA_PATH)
class RecipesTests(TestCase):
    NUMBER_RECIPES = 2
    NUMBER_TAGS_IN_SET = 2
    NUMBER_FAVORITE_USERS = 2
    NUMBER_AMOUNTS = 2
    NUMBER_INGREDIENTS = 2
    NUMBER_MEASUREMENT_UNIT = 2

    @classmethod
    def create_recipes(cls):
        MeasurementUnitFactory.create_batch(cls.NUMBER_MEASUREMENT_UNIT)
        IngredientFactory.create_batch(cls.NUMBER_INGREDIENTS)
        same_set_tags = TagFactory.create_batch(cls.NUMBER_TAGS_IN_SET)
        same_set_favorite_users = CustomUserFactory.create_batch(
            cls.NUMBER_FAVORITE_USERS
        )
        image_format, image_str = IMAGE_BASE64.split(";base64,")
        image_bytes = base64.b64decode(image_str)
        image_content_file = ImageFile(base64.b64decode(image_bytes))

        for _ in range(cls.NUMBER_RECIPES):
            different_set_tags = TagFactory.create_batch(
                cls.NUMBER_TAGS_IN_SET
            )
            different_set_users = CustomUserFactory.create_batch(
                cls.NUMBER_FAVORITE_USERS
            )
            tags = same_set_tags + different_set_tags
            users_chose_as_favorite = (
                same_set_favorite_users + different_set_users
            )

            recipe = RecipeFactory.create(
                tags=tags,
                users_chose_as_favorite=users_chose_as_favorite,
                image=image_content_file,
            )

            for _ in range(cls.NUMBER_AMOUNTS):
                AmountIngredientFactory.create(recipe=recipe)

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
        cls.user_client = APIClient()
        cls.user_client.force_authenticate(user=cls.user)

        cls.author = CustomUser.objects.create_user(
            username=AUTHOR["username"],
            email=AUTHOR["email"],
            first_name=AUTHOR["first_name"],
            last_name=AUTHOR["last_name"],
            password=AUTHOR["password"],
        )

        cls.author_client = APIClient()
        cls.author_client.force_authenticate(user=cls.author)
        cls.recipe = RecipeFactory.create(author=cls.author)

        RecipesTests.create_recipes()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_PATH)

    def get_prepared_recipes(
        self, recipes: List[dict], request_user: CustomUser
    ) -> List[dict]:
        recipes_img_basename = []
        for recipe in recipes:
            recipe_dict = RecipeFactory.detail_to_dict(recipe, request_user)
            # Меняем полное название файла, на название без пути
            # т.к. путь из модели и reponse отличаються
            recipe_img_basename = get_recipe_img_basename(recipe_dict)
            recipes_img_basename.append(recipe_img_basename)
        return recipes_img_basename

    def get_prepared_response_data(self, response):
        results_image_basename = response.data["results"].copy()
        for i, recipe_dict in enumerate(results_image_basename):
            # Меняем полное название файла, на название без пути
            # т.к. путь из модели и reponse отличаються
            results_image_basename[i] = get_recipe_img_basename(recipe_dict)
        response_data_image_basename = response.data.copy()
        response_data_image_basename["results"] = results_image_basename
        return json.dumps(response_data_image_basename)

    def test_list(self):
        response = RecipesTests.user_client.get(reverse(URLS["recipes-list"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_recipes = Recipe.objects.all().order_by("-pub_date")
        results = self.get_prepared_recipes(
            expected_recipes, RecipesTests.user
        )

        expected_recipes = {
            "count": Recipe.objects.all().count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(
            prepared_response_data,
            expected_recipes,
        )

    def test_detail(self):
        recipe = Recipe.objects.latest("pub_date")
        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-detail"], args=[recipe.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_recipes = RecipeFactory.detail_to_dict(
            recipe, RecipesTests.user
        )

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

        response = RecipesTests.author_client.post(
            path=reverse(URLS["recipes-list"]),
            data=json.dumps(create_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        recipe = Recipe.objects.latest("pub_date")
        expected_data = RecipeFactory.detail_to_dict(recipe, RecipesTests.user)

        # image have random name
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

        response = RecipesTests.user_client.put(
            reverse(URLS["recipes-detail"], args=[RecipesTests.recipe.id]),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        recipe_dict = RecipeFactory.detail_to_dict(
            RecipesTests.recipe, RecipesTests.user
        )
        recipe_dict_image_basename = get_recipe_img_basename(recipe_dict)

        response = RecipesTests.author_client.put(
            path=reverse(
                URLS["recipes-detail"], args=[RecipesTests.recipe.id]
            ),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_data_image_basename = get_recipe_img_basename(recipe_dict)
        self.assertJSONEqual(
            json.dumps(response_data_image_basename),
            recipe_dict_image_basename,
        )

    def test_delete(self):
        recipe = RecipeFactory.create(author=RecipesTests.author)
        response = RecipesTests.user_client.delete(
            path=reverse(URLS["recipes-detail"], args=[recipe.id]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Не автор не должен иметь доступ к редактированию",
        )

        response = RecipesTests.author_client.delete(
            path=reverse(URLS["recipes-detail"], args=[recipe.id]),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_author_filter(self):
        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-list"]),
            data={"author": RecipesTests.author.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_recipes = Recipe.objects.filter(author=RecipesTests.author)
        results = self.get_prepared_recipes(
            expected_recipes, RecipesTests.user
        )
        expected_response = {
            "count": expected_recipes.count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(prepared_response_data, expected_response)

    def test_tag_filter(self):
        search_tag = Tag.objects.first()

        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-list"]), data={"tags": search_tag.slug}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_recipes = Recipe.objects.filter(tags=search_tag)
        results = self.get_prepared_recipes(
            expected_recipes, RecipesTests.user
        )
        expected_response = {
            "count": expected_recipes.count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(prepared_response_data, expected_response)

    def test_favourite_filter(self):
        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-list"]),
            data={"is_favorited": "true"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_recipes = Recipe.objects.filter(
            users_chose_as_favorite=RecipesTests.user
        )
        results = self.get_prepared_recipes(
            expected_recipes, RecipesTests.user
        )

        expected_response_data = {
            "count": expected_recipes.count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(
            prepared_response_data,
            expected_response_data,
        )

    def test_shoping_cart_filter(self):
        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-list"]),
            data={"is_in_shopping_cart": "true"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_empty_recipes = Recipe.objects.filter(
            users_put_in_cart=RecipesTests.user
        )

        results = self.get_prepared_recipes(
            expected_empty_recipes, RecipesTests.user
        )

        expected_response_data = {
            "count": expected_empty_recipes.count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(
            prepared_response_data,
            expected_response_data,
        )

        response = RecipesTests.user_client.get(
            reverse(URLS["recipes-list"]),
            data={"is_in_shopping_cart": "false"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_recipes = Recipe.objects.exclude(
            users_put_in_cart=RecipesTests.user
        )

        results = self.get_prepared_recipes(
            expected_recipes, RecipesTests.user
        )

        expected_response_data = {
            "count": expected_recipes.count(),
            "next": None,
            "previous": None,
            "results": results,
        }

        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(
            prepared_response_data,
            expected_response_data,
        )

    def test_favorited_add(self):
        recipe = RecipesTests.recipe
        is_favorited = recipe.users_chose_as_favorite.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertFalse(is_favorited)

        response = RecipesTests.user_client.get(
            path=reverse(URLS["recipes-favorite"], args=[recipe.id]),
        )
        is_favorited = recipe.users_chose_as_favorite.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertTrue(is_favorited)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(
            response.content, RecipeMinifiedSerializer(instance=recipe).data
        )

    def test_favorited_delete(self):
        recipe = RecipesTests.recipe
        recipe.users_chose_as_favorite.add(RecipesTests.user)

        response = RecipesTests.user_client.delete(
            path=reverse(URLS["recipes-favorite"], args=[recipe.id]),
        )
        is_favorited = recipe.users_chose_as_favorite.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertFalse(is_favorited)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_shopping_cart_add(self):
        recipe = RecipesTests.recipe
        is_in_shopping_cart = recipe.users_put_in_cart.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertFalse(is_in_shopping_cart)

        response = RecipesTests.user_client.get(
            path=reverse(URLS["recipes-shopping_cart"], args=[recipe.id]),
        )
        is_in_shopping_cart = recipe.users_put_in_cart.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertTrue(is_in_shopping_cart)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(
            response.content, RecipeMinifiedSerializer(instance=recipe).data
        )

    def test_shopping_cart_delete(self):
        recipe = RecipesTests.recipe
        recipe.users_put_in_cart.add(RecipesTests.user)

        response = RecipesTests.user_client.delete(
            path=reverse(URLS["recipes-shopping_cart"], args=[recipe.id]),
        )
        is_in_shopping_cart = recipe.users_put_in_cart.filter(
            pk=RecipesTests.user.pk
        ).exists()
        self.assertFalse(is_in_shopping_cart)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


@override_settings(MEDIA_ROOT=MEDIA_PATH)
class SubscriptionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = CustomUserFactory.create(
            username=USER["username"],
            email=USER["email"],
            first_name=USER["first_name"],
            last_name=USER["last_name"],
            password=USER["password"],
        )
        cls.user_client = APIClient()
        cls.user_client.force_authenticate(user=cls.user)

        cls.recipes = []
        cls.authors = []
        number_recipes = 5
        for i in range(number_recipes):
            author = CustomUserFactory.create(
                username=f"author{i}",
                email=f"author{i}@email.com",
            )
            cls.authors.append(author)
            Subscription.objects.create(leader=author, follower=cls.user)
            cls.recipes.append(RecipeFactory.create(author=author))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_PATH)

    def get_users_with_recipes_img_basename(
        self, users_with_recipes: List[Dict]
    ):
        result = users_with_recipes.copy()
        for user in result:
            for i in range(len(user["recipes"])):
                user["recipes"][i] = get_recipe_img_basename(
                    user["recipes"][i]
                )
        return result

    def get_prepared_response_data(self, response):
        results = response.data["results"].copy()
        for user in results:
            for i, recipe_dict in enumerate(user["recipes"]):
                # Меняем полное название файла, на название без пути
                # т.к. путь из модели и reponse отличаються
                user["recipes"][i] = get_recipe_img_basename(recipe_dict)
        response_data_image_basename = response.data.copy()
        response_data_image_basename["results"] = results
        return json.dumps(response_data_image_basename)

    def test_list(self):
        response = SubscriptionTest.user_client.get(
            path=reverse(URLS["subscriptions-list"])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_authors = CustomUser.objects.filter(
            leader_subscriptions__follower=RecipesTests.user
        )
        expected_results = []
        for author in expected_authors:
            expected_results.append(
                UserWithRecipesSerializer(
                    instance=author,
                    context={"test_request_user": RecipesTests.user},
                ).data
            )
        expected_results = self.get_users_with_recipes_img_basename(
            expected_results
        )
        expected_response = {
            "count": expected_authors.count(),
            "next": None,
            "previous": None,
            "results": expected_results,
        }
        prepared_response_data = self.get_prepared_response_data(response)
        self.assertJSONEqual(prepared_response_data, expected_response)

    def test_create(self):
        leader = CustomUserFactory.create()
        response = SubscriptionTest.user_client.get(
            path=reverse(URLS["subscriptions-detail"], args=[leader.id])
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        excepted = UserWithRecipesSerializer(
            instance=leader,
            context={"test_request_user": SubscriptionTest.user},
        ).data
        self.assertJSONEqual(
            json.dumps(response.data),
            excepted,
        )

    def test_delete(self):
        leader = CustomUserFactory.create()
        Subscription.objects.create(
            leader=leader, follower=SubscriptionTest.user
        )

        response = SubscriptionTest.user_client.delete(
            path=reverse(URLS["subscriptions-detail"], args=[leader.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
