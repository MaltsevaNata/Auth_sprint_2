from google_auth_oauthlib import flow as gauth_flow
from flask import redirect, url_for, request, current_app
from googleapiclient.discovery import build

from core import Config
from models import Role, GoogleUser
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

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    service = build('people', 'v1', credentials=credentials)
    result = service.people().get(
        resourceName='people/me',
        personFields='names,emailAddresses'
    ).execute()
    email = result['emailAddresses'][0]['value']

    google_user = current_app.google_user_manager.get_by_email(email)
    if not google_user:
        # ищем только того пользователя, у кого указан текущий гугловский email, username роли не играет
        user = current_app.user_manager.get_by_email(email)
        if not user:
            user = current_app.user_manager.create_user(
                username=current_app.user_manager.generate_username(size=Config.MOCK_USERNAME_LENGTH),
                password=current_app.user_manager.generate_password(size=Config.MOCK_PASSWORD_LENGTH),
                email=email,
                first_name=result['names'][0]['givenName'],
                last_name=result['names'][0]['familyName']
            )
            default_role = Role.query.filter_by(default=True).first()
            if default_role:
                current_app.user_manager.add_role(user, default_role.name)

        google_user = current_app.google_user_manager.create_google_user(
            email=email,
            first_name=result['names'][0]['givenName'],
            last_name=result['names'][0]['familyName'],
            user_id=user.id
        )

    user = current_app.user_manager.get_by_id(google_user.user_id)

    return auth_user(user)
