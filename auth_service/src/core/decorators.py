import functools

from flask import abort
from marshmallow import ValidationError


def catch_validation_errors(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return abort(400, e)

    return wrapper
