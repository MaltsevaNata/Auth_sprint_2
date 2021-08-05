from flask import redirect, request

from .api_bp import bp
from .utils.auth_google_user import auth_google_user, callback_function, firstcall_function


@bp.route("/authorize/with_google")
def authorize_with_google():
    authorization_url = firstcall_function()

    return redirect(authorization_url)


@bp.route("/authorize/with_google/callback")
def google_oauth2callback():
    result = callback_function(
        state=request.args.get('state'),
        url=request.url
    )

    return auth_google_user(
        email=result['emailAddresses'][0]['value'],
        first_name=result['names'][0]['givenName'],
        last_name=result['names'][0]['familyName']
    )
