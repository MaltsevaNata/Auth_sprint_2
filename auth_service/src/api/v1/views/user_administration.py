import pyotp
from flask import jsonify, request, current_app, redirect, render_template, url_for
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from flask_jwt_extended.utils import get_jwt

from app import redis
from core import db, Config, jwt
from models import RefreshToken, User, LoginHistory

from .api_bp import bp
from .errors import bad_request, unauthorized
from .utils.decorators import validate_request
from .utils.schemas import SignUpSchema, UpdateUserSchema, ChangePasswordSchema, SignInSchema, SignOutSchema
from .utils.auth_user import auth_user


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
@validate_request(schema=SignUpSchema)
def sign_up(data):
    """
    Creates user instance in database
    """
    user = current_app.user_manager.create_user(**data)
    return jsonify(user.as_dict()), 201


@bp.route("/initial_sync/<string:user_id>")
def initial_sync(user_id: str):
    """
    Generate key and associate it with the user
    """
    secret = pyotp.random_base32()
    user = current_app.user_manager.get_by_id(user_id)
    user.totp_secret = secret
    user.save()
    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(name=user_id + '@praktikum.ru', issuer_name='Awesome Auth app')
    return render_template("sync_template.html", url=provisioning_url, id=user_id)


@bp.route("/sync/<string:user_id>", methods=["POST"])
def sync(user_id: str):
    user = current_app.user_manager.get_by_id(user_id)
    secret = user.totp_secret
    print(f"""Got secret: {secret}""")
    totp = pyotp.TOTP(secret)
    print(f"""Expected code: {totp.now()}""")
    # Верифицируем полученный от пользователя код
    code = request.form['code']
    print(f"""Got code: {code}""")
    if not totp.verify(code):
        return 'Неверный код'
    user.is_verified = True
    user.save()
    return auth_user(user)


@bp.route("/check/<string:user_id>", methods=["POST"])
def check(user_id: str):
    user = current_app.user_manager.get_by_id(user_id)
    if not user.is_verified:
        return redirect(url_for('.sign_in'))

    code = request.form['code']
    secret = user.totp_secret
    totp = pyotp.TOTP(secret)
    print(f"""Expected code: {totp.now()}""")
    # Верифицируем полученный от пользователя код
    print(f"""Got code: {code}""")

    if not totp.verify(code):
        return jsonify(msg="Неверный код")

    return auth_user(user)


@bp.route("/", methods=["GET"])
def base():
    return render_template("base_page.html")


@bp.route("/sign_in", methods=["POST"])
@validate_request(schema=SignInSchema)
def sign_in(data):
    """
    Checks credentials, performs 2FA and generates tokens
    """
    user = current_app.user_manager.get_by_username(data["username"])
    if not user or not user.check_password(data["password"]):
        return unauthorized("Unauthorized")

    if user.active_2FA:
        if not user.is_verified:
            return redirect(url_for('.initial_sync', user_id=user.id))
        return render_template("check_totp.html", message="", id=user.id)

    return auth_user(user)


@bp.route("/sign_out", methods=["POST"])
@jwt_required()
@validate_request(schema=SignOutSchema)
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
@validate_request(schema=UpdateUserSchema)
def update_user(data):
    """
    Updates user information: email, username, first name, last name optionally
    """
    identity = get_jwt_identity()
    print(identity)
    user = User.query.get_or_404(identity)
    print(user)

    updated_user = current_app.user_manager.update_user(user, data)

    return jsonify(data=updated_user.as_dict(), msg="Updated user info")


@bp.route("/user/change_password", methods=["POST"])
@jwt_required()
@validate_request(schema=ChangePasswordSchema)
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
