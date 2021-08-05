from google_auth_oauthlib import flow as gauth_flow
from googleapiclient.discovery import build
from flask import current_app, url_for

from core import Config
from models import Role
from .auth_user import auth_user


def firstcall_function():
    flow = gauth_flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=Config.GOOGLE_CLIENT_SCOPES)

    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    return authorization_url


def callback_function(state, url):
    flow = gauth_flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=Config.GOOGLE_CLIENT_SCOPES,
        state=state)
    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_response = url

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    service = build('people', 'v1', credentials=credentials)
    return service.people().get(
        resourceName='people/me',
        personFields='names,emailAddresses'
    ).execute()


def auth_google_user(email, first_name, last_name):
    google_user = current_app.google_user_manager.get_by_email(email)
    if not google_user:
        # ищем только того пользователя, у кого указан текущий гугловский email, username роли не играет
        user = current_app.user_manager.get_by_email(email)
        if not user:
            user = current_app.user_manager.create_user(
                username=current_app.user_manager.generate_username(size=Config.MOCK_USERNAME_LENGTH),
                password=current_app.user_manager.generate_password(size=Config.MOCK_PASSWORD_LENGTH),
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            default_role = Role.query.filter_by(default=True).first()
            if default_role:
                current_app.user_manager.add_role(user, default_role.name)

        google_user = current_app.google_user_manager.create_google_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_id=user.id
        )

    user = current_app.user_manager.get_by_id(google_user.user_id)

    return auth_user(user)
