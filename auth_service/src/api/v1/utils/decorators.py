import functools

from flask_jwt_extended import get_jwt_identity

from api.v1.errors import bad_request, forbidden
from flask import request
from marshmallow import ValidationError, EXCLUDE

from models import User


def validate_request(schema):
    """Параметризированный декоратор для валидации POST запроса
    используя marshmallow схему.

    Args:
        schema (marshmallow.Schema): marshmallow Schema class object
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if request.json:
                    data = schema().load(request.json, unknown=EXCLUDE)
                elif request.form:
                    data = schema().load(request.form, unknown=EXCLUDE)
                else:
                    return bad_request("Data not found")
            except ValidationError as err:
                return bad_request(err.messages)
            return f(data, *args, **kwargs)

        return decorated_function

    return decorator


def superuser_required(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        user_id = get_jwt_identity()
        current_user = User.query.get_or_404(user_id)
        if 'superuser' not in current_user.get_roles():
            return forbidden('Forbidden')
        return fn(*args, **kwargs)

    return decorator
