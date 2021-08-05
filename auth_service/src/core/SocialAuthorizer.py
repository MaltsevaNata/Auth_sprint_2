import abc
from google_auth_oauthlib import flow as gauth_flow
from googleapiclient.discovery import build
from flask import current_app, url_for

from api.v1.utils.auth_user import auth_user
from core import Config
from models import Role


class SocialAuthorizer(abc.ABC):
    @abc.abstractmethod
    def get_redirect_url(self):
        pass

    @abc.abstractmethod
    def callback_func(self):
        pass

    @abc.abstractmethod
    def authorize(self):
        pass


class GoogleAuthorizer(SocialAuthorizer):
    def get_redirect_url(self):
        flow = gauth_flow.Flow.from_client_secrets_file(
            Config.GOOGLE_CLIENT_SECRET_FILEPATH,
            scopes=Config.GOOGLE_CLIENT_SCOPES)

        flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')

        return authorization_url

    def callback_func(self, **kwargs):
        flow = gauth_flow.Flow.from_client_secrets_file(
            Config.GOOGLE_CLIENT_SECRET_FILEPATH,
            scopes=Config.GOOGLE_CLIENT_SCOPES,
            state=kwargs.get('state'))
        flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

        authorization_response = kwargs.get('url')

        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        service = build('people', 'v1', credentials=credentials)
        data = service.people().get(
            resourceName='people/me',
            personFields='names,emailAddresses'
        ).execute()

        return self.authorize(
            email=data['emailAddresses'][0]['value'],
            first_name=data['names'][0]['givenName'],
            last_name=data['names'][0]['familyName']
        )

    def authorize(self, **kwargs):
        google_user = current_app.google_user_manager.get_by_email(kwargs.get('email'))
        if not google_user:
            # ищем только того пользователя, у кого указан текущий гугловский email, username роли не играет
            user = current_app.user_manager.get_by_email(kwargs.get('email'))
            if not user:
                user = current_app.user_manager.create_user(
                    username=current_app.user_manager.generate_username(size=Config.MOCK_USERNAME_LENGTH),
                    password=current_app.user_manager.generate_password(size=Config.MOCK_PASSWORD_LENGTH),
                    email=kwargs.get('email'),
                    first_name=kwargs.get('first_name'),
                    last_name=kwargs.get('last_name')
                )
                default_role = Role.query.filter_by(default=True).first()
                if default_role:
                    current_app.user_manager.add_role(user, default_role.name)

            google_user = current_app.google_user_manager.create_google_user(
                email=kwargs.get('email'),
                first_name=kwargs.get('first_name'),
                last_name=kwargs.get('last_name'),
                user_id=user.id
            )

        user = current_app.user_manager.get_by_id(google_user.user_id)

        return auth_user(user)
