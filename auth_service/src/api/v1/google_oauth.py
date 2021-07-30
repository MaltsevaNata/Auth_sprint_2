from google_auth_oauthlib import flow as gauth_flow
from flask import redirect, url_for, request, current_app
from googleapiclient.discovery import build

from core import Config
from models import Role
from models.google_user import GoogleUser
from .api_bp import bp
from .utils.auth_user import auth_user


@bp.route("/authorize/with_google")
def authorize_with_google():
    flow = gauth_flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=Config.GOOGLE_CLIENT_SCOPES)

    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    return redirect(authorization_url)


@bp.route("/authorize/with_google/callback")
def google_oauth2callback():
    state = request.args.get('state')
    flow = gauth_flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=Config.GOOGLE_CLIENT_SCOPES,
        state=state)
    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_response = request.url

    # FIXME dev костыль, без него google ругается
    authorization_response = authorization_response.replace('http://', 'https://')

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    service = build('people', 'v1', credentials=credentials)
    result = service.people().get(
        resourceName='people/me',
        personFields='names,emailAddresses'
    ).execute()
    email = result['emailAddresses'][0]['value']

    google_user = GoogleUser.query.filter_by(email=email).first()
    if not google_user:
        user = current_app.user_manager.create_user(
            username=email,
            password=current_app.user_manager.generate_password(size=Config.MOCK_PASSWORD_LENGTH),
            email=email
        )
        user.first_name = result['names'][0]['givenName']
        user.last_name = result['names'][0]['familyName']
        default_role = Role.query.filter_by(default=True).first()
        if default_role:
            current_app.user_manager.add_role(user, default_role.name)

        google_user = GoogleUser(email=user.email,
                                 first_name=user.first_name,
                                 last_name=user.last_name,
                                 user_id=user.id)
        google_user.save()

    user = current_app.user_manager.get_by_id(google_user.user_id)

    return auth_user(user)
