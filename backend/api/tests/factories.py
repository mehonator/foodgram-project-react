import factory
from api.models import (
    Tag,
    Ingredient,
    MeasurementUnit,
    Recipe,
    transliterate_slugify,
)
from users.models import CustomUser
from users.tests.factories import CustomUserFactory

TAGS_ATTRIBUTE = {
    "names": [
        "Завтрак,",
        "Обед",
        "Ужин",
        "Подник",
        "Второй завтрак",
        "Новый год",
        "День Рождения",
        "Майские праздники",
        "Салаты",
        "Супы",
    ],
    "colors": [
        "#ff0000",
        "#eaff00",
        "#00ff11",
        "#0040ff",
        "#0800ff",
        "#ee00ff",
    ],
}
NUMBER_TAGS = len(TAGS_ATTRIBUTE["names"])

MEASUREMENT_UNITS_NAMES = [
    "КГ",
    "Г",
    "мл",
    "Л",
    "шт.",
]
NUMBER_MEASUREMENT_UNITS = len(MEASUREMENT_UNITS_NAMES)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Iterator(TAGS_ATTRIBUTE["names"])
    color = factory.Iterator(TAGS_ATTRIBUTE["colors"])
    slug = factory.LazyAttribute(lambda obj: transliterate_slugify(obj.name))


class MeasurementUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeasurementUnit

    name = factory.Iterator(MEASUREMENT_UNITS_NAMES)


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = factory.Sequence(lambda n: f"ингредиент_{n}")
    measurement_unit = factory.Iterator(MeasurementUnit.objects.all())


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    name = factory.Sequence(lambda n: f"рецепт_{n}")
    tags = factory.SubFactory(TagFactory)
    author = factory.SubFactory(CustomUserFactory)

    user_chose_as_favorite1 = factory.RelatedFactory(
        CustomUserFactory,
        factory_related_name="favorite_recipes",
    )
    user_chose_as_favorite2 = factory.RelatedFactory(
        CustomUserFactory,
        factory_related_name="favorite_recipes",
    )
    text = factory.Faker("text")
    cooking_time = 1
