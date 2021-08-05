from flask import redirect, request, current_app

from .api_bp import bp


@bp.route("/authorize/with_google")
def authorize_with_google():
    return redirect(
        current_app.google_authorizer.get_redirect_url()
    )


@bp.route("/authorize/with_google/callback")
def google_oauth2callback():
    return current_app.google_authorizer.callback_func(
        state=request.args.get('state'),
        url=request.url
    )
