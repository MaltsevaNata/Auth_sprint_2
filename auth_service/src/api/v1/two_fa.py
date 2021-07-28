import pyotp
from flask import jsonify, render_template, request, url_for, current_app, redirect

from .api_bp import bp
from .utils.auth_user import auth_user


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
    provisioning_url = totp.provisioning_uri(name=user_id + '@praktikum.ru', issuer_name='Awesome Auth app')
    return render_template("sync_template.html", url=provisioning_url, id=user_id)


@bp.route("/sync/<string:user_id>", methods=["POST"])
def sync(user_id: str):
    """
    Requests totp code and verifies the user
    """
    user = current_app.user_manager.get_by_id(user_id)
    secret = user.totp_secret
    totp = pyotp.TOTP(secret)
    # Verify received code
    code = request.form['code']
    if not totp.verify(code):
        return 'Неверный код'
    user.is_verified = True
    user.save()
    return auth_user(user)
