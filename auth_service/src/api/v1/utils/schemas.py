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


class SignInSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class UpdateUserSchema(ma.Schema):
    username = fields.String(required=False)
    email = fields.String(required=False)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    active_2FA = fields.Boolean(required=False)


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
