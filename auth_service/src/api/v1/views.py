from flask import jsonify, request, current_app
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from flask_jwt_extended.utils import get_jwt
from marshmallow import ValidationError

from app import redis
from core import db, Config, jwt
from models import RefreshToken, User, LoginHistory, Role

from .api_bp import bp
from .errors import unauthorized
from .utils import schemas
from .utils.decorators import validate_request, superuser_required


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    Callback function to check if a JWT exists in the redis blocklist
    """
    user_id = jwt_payload["sub"]
    jti = jwt_payload["jti"]

    soa_flag = redis.get(f"{user_id}-soa")
    if soa_flag:
        redis.set(jti, ttl=Config.REDIS_TTL, value="")
        return True

    token_in_redis = redis.get(jti)
    return token_in_redis is not None


@bp.route("/sign_up", methods=["POST"])
@validate_request(schema=schemas.SignUpSchema)
def sing_up(data):
    """
    Creates user instance in database
    """

    user = current_app.user_manager.create_user(**data)
    default_role = Role.query.filter_by(default=True).first()
    if default_role:
        current_app.user_manager.add_role(user, default_role.name)
    return jsonify(user.as_dict()), 201


# sing in
@bp.route("/sign_in", methods=["POST"])
@validate_request(schema=schemas.SignInSchema)
def sign_in(data):
    """
    Checks credentials and generates tokens if they're valid
    """
    user = current_app.user_manager.get_by_username(data["username"])

    if not user or not user.check_password(data["password"]):
        return unauthorized("Unauthorized")

    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'roles': user.get_roles()
        }
    )
    refresh_token = create_refresh_token(identity=user.id)

    db.session.add(RefreshToken(user_id=user.id, token=refresh_token))
    # log to login history
    db.session.add(
        LoginHistory(
            user_id=user.id,
            user_agent=request.user_agent.string,
            ip_addr=request.remote_addr)
    )
    db.session.commit()

    redis.delete(f"{user.id}-soa")

    return jsonify(access_token=access_token,
                   refresh_token=refresh_token,
                   msg="Signed in")


@bp.route("/sign_out", methods=["POST"])
@jwt_required()
@validate_request(schema=schemas.SignOutSchema)
def sign_out(data):
    """
    Removes current refresh token for user
    """
    jti = get_jwt()["jti"]
    redis.set(jti, ttl=Config.REDIS_TTL, value="")

    refresh_token = data.pop("refresh_token")
    saved_token = RefreshToken.query.filter_by(token=refresh_token)
    saved_token.delete()
    db.session.commit()

    return jsonify(msg="Signed out")


@bp.route("/sign_out_all", methods=["POST"])
@jwt_required()
def sign_out_all():
    """
    Removes all user's refresh tokens and sets SOA flag
    """
    user_id = get_jwt_identity()
    redis.set(f"{user_id}-soa", ttl=Config.REDIS_EXTENDED_TTL, value="")

    db.session.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.session.commit()

    return jsonify(msg="Signed out")


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Generates a new pair of tokens for user
    """
    identity = get_jwt_identity()
    user = User.query.get_or_404(identity)
    # find old token instance and delete it
    old_refresh_token = request.headers.get("Authorization").lstrip("Bearer ")
    saved_token = RefreshToken.query.filter_by(user_id=user.id, token=old_refresh_token)
    saved_token.delete()
    db.session.commit()
    # generate new token and create instance
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.session.add(new_token)
    db.session.commit()

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@bp.route("/history", methods=["GET"])
@jwt_required()
def get_login_history():
    """
    Returns current user's history of history logs
    """
    user_id = get_jwt_identity()
    query = db.session.query(LoginHistory).filter(LoginHistory.user_id == user_id)
    history_logs = query.all()

    return jsonify([log.serialize for log in history_logs])


@bp.route("/get_role")
@jwt_required()
def get_role():
    """Get current user's role
    """
    identity = get_jwt_identity()
    user = User.query.get_or_404(identity)
    roles = user.get_roles()
    return jsonify(roles=roles)


# partial user update
@bp.route("/user/update", methods=["PATCH"])
@jwt_required()
@validate_request(schema=schemas.UpdateUserSchema)
def update_user(data):
    """
    Updates user information: email, username, first name, last name optionally
    """
    identity = get_jwt_identity()
    user = User.query.get_or_404(identity)

    updated_user = current_app.user_manager.update_user(user, data)

    return jsonify(data=updated_user.as_dict(), msg="Updated user info")


@bp.route("/user/change_password", methods=["POST"])
@jwt_required()
@validate_request(schema=schemas.ChangePasswordSchema)
def change_password(data):
    """
    Saves the new password hash. We expect that after changing password, the "Sign out all" request will be sent
    """
    identity = get_jwt_identity()
    # set new password hash
    user = User.query.filter_by(id=identity).first()
    user.set_password(data["new_password"])
    db.session.commit()
    return jsonify(msg="Changed password, please, sign out")


@bp.route("/me")
@jwt_required()
def get_me():
    """
    Returns current user's information
    """
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first()
    user_data = user.as_dict()
    return jsonify(user_data)


@bp.route("/users")
@jwt_required()
def get_users():
    """
    Returns information about all users
    """
    users = User.query.all()
    user_data = [user.as_dict() for user in users]
    
    return jsonify(user_data)


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


@bp.route("/roles/<id>", methods=["POST"])
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


@bp.route("/user/add_role", methods=["POST"])
@jwt_required()
@superuser_required
@validate_request(schema=schemas.AddRoleSchema)
def add_role(data):
    user = User.query.filter_by(username=data.get("username")).first_or_404()
    current_app.user_manager.add_role(user, data.get('rolename'))
    return jsonify(msg='ok')


@bp.route("/user/remove_role", methods=["POST"])
@jwt_required()
@superuser_required
@validate_request(schema=schemas.AddRoleSchema)
def remove_role(data):
    user = User.query.filter_by(username=data.get("username")).first_or_404()
    current_app.user_manager.remove_role(user, data.get('rolename'))
    return jsonify(msg='ok')


@bp.route("/authorize")
@jwt_required()
def authorize():
    return jsonify(roles=get_jwt().get("roles"))
