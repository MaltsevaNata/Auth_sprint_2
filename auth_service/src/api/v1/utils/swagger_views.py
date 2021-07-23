from flasgger import Swagger, SwaggerView, Schema, fields

from .schemas import *


class SignUpView(SwaggerView):
    parameters = [
        {
            "name": "username",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "password",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "email",
            "in": "body",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        201: {
            "description": "Create new user instance",
            "schema": SignUpSchema
        }
    }


class SignOutView(SwaggerView):
    parameters = [
        {
            "name": "refreshtoken",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Sign out",
            "schema": SignOutSchema
        }
    }