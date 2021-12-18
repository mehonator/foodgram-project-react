import json

from api.models import Ingredient, MeasurementUnit


def fill_db_ingredient_measurement_unit(path_file: str):
    with open(path_file) as json_file:
        data = json.load(json_file)
        for ingredient in data:
            measurement_unit, _ = MeasurementUnit.objects.get_or_create(
                name=ingredient["measurement_unit"]
            )
            Ingredient.objects.get_or_create(
                name=ingredient["name"], measurement_unit=measurement_unit
            )


fill_db_ingredient_measurement_unit("/code/utils/ingredients.json")
