import google_auth_oauthlib.flow
from flask import redirect

from core import Config
from .api_bp import bp


@bp.route("/sign_in/with_google")
def sign_in_with_google():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ])

    flow.redirect_uri = 'http://127.0.0.1:5000'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    return redirect(authorization_url)
