import factory

from api.models import (
    AmountIngredient,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
    transliterate_slugify,
)
from users.models import CustomUser
from users.tests.factories import CustomUserFactory

TAGS_COLORS = [
    "#ff0000",
    "#eaff00",
    "#00ff11",
    "#0040ff",
    "#0800ff",
    "#ee00ff",
]


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Тег_{n}")
    color = factory.Iterator(TAGS_COLORS)
    slug = factory.LazyAttribute(lambda obj: transliterate_slugify(obj.name))

    class Meta:
        model = Tag

    @staticmethod
    def to_dict(tag: Tag) -> dict:
        return {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "slug": tag.slug,
        }


class MeasurementUnitFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"единица_измерения_{n}")

    class Meta:
        model = MeasurementUnit


class IngredientFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"ингредиент_{n}")
    measurement_unit = factory.SubFactory(MeasurementUnitFactory)

    class Meta:
        model = Ingredient


class AmountIngredientFactory(factory.django.DjangoModelFactory):
    amount = factory.Sequence(lambda n: n)
    ingredient = factory.Iterator(Ingredient.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())

    class Meta:
        model = AmountIngredient

    @staticmethod
    def to_dict(amount_ingretient: AmountIngredient) -> dict:
        return {
            "id": amount_ingretient.id,
            "name": amount_ingretient.ingredient.name,
            "measurement_unit": (
                amount_ingretient.ingredient.measurement_unit.name
            ),
            "amount": amount_ingretient.amount,
        }


class RecipeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"рецепт_{n}")
    author = factory.SubFactory(CustomUserFactory)
    text = factory.Faker("text")
    image = factory.django.ImageField(filename="api/tests/test-pic.png")
    cooking_time = 1

    class Meta:
        model = Recipe

    @staticmethod
    def create_update_to_dict(recipe: Recipe) -> dict:
        ingredients = [
            AmountIngredientFactory.to_dict(amount)
            for amount in recipe.amounts_ingredients.all()
        ]
        recipe_dict = {
            "id": recipe.id,
            "name": recipe.name,
            "tags": [TagFactory.to_dict(tag) for tag in recipe.tags.all()],
            "ingredients": ingredients,
            "image": recipe.image.url if recipe.image else None,
            "text": recipe.text,
            "cooking_time": recipe.cooking_time,
        }
        return recipe_dict

    @staticmethod
    def detail_to_dict(recipe: Recipe, request_user: CustomUser) -> dict:
        is_favorited = recipe.users_chose_as_favorite.filter(
            id=request_user.id
        ).exists()

        is_in_shopping_cart = recipe.users_put_in_cart.filter(
            id=request_user.id
        ).exists()

        recipe_dict = RecipeFactory.create_update_to_dict(recipe)
        recipe_dict.update(
            {
                "author": CustomUserFactory.user_to_dict(
                    recipe.author, request_user
                ),
                "is_favorited": is_favorited,
                "is_in_shopping_cart": is_in_shopping_cart,
            }
        )

        return recipe_dict

    @factory.post_generation
    def users_chose_as_favorite(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users_chose_as_favorite.add(user)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
