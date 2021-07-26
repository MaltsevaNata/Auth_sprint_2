from flasgger import SwaggerView

from .schemas import *


class SignUpView(SwaggerView):
    tags = ["Authorization"]
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
        },
        400: {
            "description": "Bad request",
            "schema": BadRequestSchema
        }
    }


class SignInView(SwaggerView):
    tags = ["Authorization"]
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
        }
    ]
    responses = {
        200: {
            "description": "Sign in with credentials",
            "schema": RefreshSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class SignOutView(SwaggerView):
    tags = ["Authorization"]
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
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class SignOutAllView(SwaggerView):
    tags = ["Authorization"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Sign out from all devices",
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class RefreshView(SwaggerView):
    tags = ["Authorization"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Refresh user's tokens",
            "schema": RefreshSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class HistoryView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "History of user logins",
            "schema": HistorySchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class UpdateView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "username",
            "in": "body",
            "type": "string",
            "required": False,
        },
        {
            "name": "email",
            "in": "body",
            "type": "string",
            "required": False,
        },
        {
            "name": "first_name",
            "in": "body",
            "type": "string",
            "required": False,
        },
        {
            "name": "last_name",
            "in": "body",
            "type": "string",
            "required": False,
        },
        {
            "name": "active_2FA",
            "in": "body",
            "type": "string",
            "required": False,
        }
    ]
    responses = {
        200: {
            "description": "Partly update user info",
            "schema": UpdateUserSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        },
        400: {
            "description": "Bad request",
            "schema": BadRequestSchema
        }
    }


class ChangePasswordView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "password",
            "in": "body",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Change User Password",
            "schema": ChangedPasswordSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        },
        400: {
            "description": "Bad request",
            "schema": BadRequestSchema
        }
    }


class MeView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
    ]
    responses = {
        200: {
            "description": "Current user info",
            "schema": UserSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class UserRoleView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
    ]
    responses = {
        200: {
            "description": "Current user roles",
            "schema": UserRoleSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class AddRoleView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "username",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "rolename",
            "in": "body",
            "type": "string",
            "required": True,
        },
    ]
    responses = {
        200: {
            "description": "Add user role",
            "schema": ResponseSchema
        },
        403: {
            "description": "Forbidden",
            "schema": ForbiddenSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class RemoveRoleView(SwaggerView):
    tags = ["User"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "username",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "rolename",
            "in": "body",
            "type": "string",
            "required": True,
        },
    ]
    responses = {
        200: {
            "description": "Remove user role",
            "schema": ResponseSchema
        },
        403: {
            "description": "Forbidden",
            "schema": ForbiddenSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class RoleView(SwaggerView):
    tags = ["Roles"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
    ]
    responses = {
        200: {
            "description": "All roles",
            "schema": RoleSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        }
    }


class CreateRoleView(SwaggerView):
    tags = ["Roles"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "name",
            "in": "body",
            "type": "string",
            "required": True,
        },
        {
            "name": "permissions",
            "in": "body",
            "type": "integer",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Role created",
            "schema": RoleSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        },
        403: {
            "description": "Forbidden",
            "schema": ForbiddenSchema
        }
    }


class UpdateRoleView(SwaggerView):
    tags = ["Roles"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "name": "name",
            "in": "body",
            "type": "string",
            "required": False,
        },
        {
            "name": "permissions",
            "in": "body",
            "type": "integer",
            "required": False,
        },
        {
            "name": "default",
            "in": "body",
            "type": "boolean",
            "required": False,
        }
    ]
    responses = {
        200: {
            "description": "Role updated successfully",
            "schema": RoleSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        },
        403: {
            "description": "Forbidden",
            "schema": ForbiddenSchema
        }
    }


class DeleteRoleView(SwaggerView):
    tags = ["Roles"]
    parameters = [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        }
    ]
    responses = {
        200: {
            "description": "Role deleted successfully",
            "schema": ResponseSchema
        },
        401: {
            "description": "User isn't authorized",
            "schema": UnauthorizedSchema
        },
        403: {
            "description": "Forbidden",
            "schema": ForbiddenSchema
        }
    }