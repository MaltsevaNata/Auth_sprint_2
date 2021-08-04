import pyotp
from flask import jsonify, current_app

from .api_bp import bp
from .utils import schemas
from .utils.auth_user import auth_user
from .utils.decorators import validate_request


@bp.route("/initial_sync/<string:user_id>")
def initial_sync(user_id: str):
    """
    Generates key and associates it with the user
    """
    secret = pyotp.random_base32()
    user = current_app.user_manager.get_by_id(user_id)
    user.totp_secret = secret
    user.save()
    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(name=user.username, issuer_name='Auth app')
    return jsonify(url=provisioning_url, id=user_id)  # use this data to make QR


@bp.route("/sync/<string:user_id>", methods=["POST"])
@validate_request(schema=schemas.SyncUser)
def sync(data, user_id: str):
    """
    Requests totp code and verifies the user
    """
    user = current_app.user_manager.get_by_id(user_id)
    secret = user.totp_secret
    totp = pyotp.TOTP(secret)
    # Verify received code
    code = data.pop("code")
    if not totp.verify(code):
        return jsonify(msg="Wrong code"), 401
    user.is_verified = True
    user.save()
    return auth_user(user)
