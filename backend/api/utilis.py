from typing import List

from django.db import models
from django.utils.text import slugify as dj_slugify
from transliterate import detect_language
from transliterate import slugify as trans_slugify

from api.exceptions import NotFoundLangException


def transliterate_slugify(text: str):
    if text.isascii():
        return dj_slugify(text)

    if detect_language(text) is not None:
        return trans_slugify(text)

    raise NotFoundLangException("Invalid language")


def is_distinct(items):
    distinct = list(set(items))
    try:
        distinct.sort()
    except TypeError:
        distinct.sort(key=lambda item: item.pk)

    try:
        items.sort()
    except TypeError:
        items.sort(key=lambda item: item.pk)
    return items == distinct


def get_nonexistent_ids(model: models.Model, ids_objects) -> List[int]:
    not_exists = []
    for id_object in ids_objects:
        if not model.objects.filter(pk=id_object).exists():
            not_exists.append(id_object)
    return not_exists
