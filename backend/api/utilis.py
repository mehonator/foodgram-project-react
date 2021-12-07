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
