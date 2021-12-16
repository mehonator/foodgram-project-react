from collections import namedtuple
from typing import List

from rest_framework import status
from rest_framework.response import Response

ValidationResult = namedtuple(
    "ValidationResult", ["is_valid", "query_param", "error_msg"]
)


def validate_query_params(validators: List):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            params_errors = {}
            for validate in validators:
                validation = validate(self)
                if not validation.is_valid:
                    params_errors[
                        validation.query_param
                    ] = validation.error_msg

            if params_errors:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=params_errors,
                )

            return method(self, *args, **kwargs)

        return wrapper

    return decorator
