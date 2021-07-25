from marshmallow import fields, validate

from core import ma


class SignUpSchema(ma.Schema):
    username = fields.String(required=True)
    email = fields.Str(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6, max=300)
    )


class SignOutSchema(ma.Schema):
    refresh_token = fields.String(required=True)


class RefreshSchema(ma.Schema):
    refresh_token = fields.String()
    access_token = fields.String()


class SignInSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class UpdateUserSchema(ma.Schema):
    username = fields.String(required=False)
    email = fields.String(required=False)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    active_2FA = fields.Boolean(required=False)


class UserSchema(ma.Schema):
    username = fields.String()
    email = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    active_2FA = fields.Boolean()
    id = fields.UUID()
    updated = fields.DateTime()
    created = fields.DateTime()


class UserRoleSchema(ma.Schema):
    roles = fields.List(fields.String())


class ChangePasswordSchema(ma.Schema):
    new_password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6, max=300)
    )


class CreateRoleSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    permissions = fields.Integer(required=True)


class UpdateRoleSchema(ma.Schema):
    name = fields.String(validate=validate.Length(min=1))
    permissions = fields.Integer()
    default = fields.Boolean()


class AddRoleSchema(ma.Schema):
    username = fields.String(required=True)
    rolename = fields.String(required=True)


class RoleSchema(ma.Schema):
    id = fields.UUID()
    name = fields.String()
    default = fields.Boolean()
    permissions = fields.Integer()
    updated = fields.DateTime()
    created = fields.DateTime()


class HistorySchema(ma.Schema):
    ip_addr = fields.String()
    timestamp = fields.DateTime()
    user_agent = fields.String()


class ChangedPasswordSchema(ma.Schema):
    msg = fields.String()


class ForbiddenSchema(ma.Schema):
    error = fields.String()
    message = fields.String()


class UnauthorizedSchema(ma.Schema):
    msg = fields.String()


class BadRequestSchema(ma.Schema):
    error = fields.String()
    message = fields.String()


class ResponseSchema(ma.Schema):
    msg = fields.String()
