from flask import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from core import db
from models import Role, User
from .api_bp import bp
from .utils import schemas
from .utils.decorators import superuser_required, validate_request


@bp.route("/roles")
@jwt_required()
def get_roles():
    roles = Role.query.all()
    role_data = [role.as_dict() for role in roles]

    return jsonify(role_data)


@bp.route("/roles", methods=["POST"])
@jwt_required()
@superuser_required
@validate_request(schema=schemas.CreateRoleSchema)
def create_role(data):
    role = Role.query.filter_by(name=data.get("name")).first()
    if role:
        raise ValidationError("name already exists.")

    role = Role(name=data.get("name"), permissions=data.get("permissions"))
    db.session.add(role)
    db.session.commit()

    return jsonify(role.as_dict())


@bp.route("/roles/<id>", methods=["PATCH"])
@jwt_required()
@superuser_required
@validate_request(schema=schemas.UpdateRoleSchema)
def update_role(data, id):
    role = Role.query.get_or_404(id)

    default = data.get("default")

    if default and not role.default:
        previous_default_role = Role.query.filter_by(default=True).first()
        setattr(previous_default_role, 'default', False)
        db.session.add(previous_default_role)
    else:
        del data["default"]

    for key, value in data.items():
        setattr(role, key, value)

    db.session.add(role)
    db.session.commit()

    return jsonify(role.as_dict())


@bp.route("/roles/<id>", methods=["DELETE"])
@jwt_required()
@superuser_required
def delete_role(id):
    Role.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify(msg='ok')

