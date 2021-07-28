import google_auth_oauthlib.flow
from flask import redirect, session, url_for, request, jsonify
from googleapiclient.discovery import build

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

    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)


@bp.route("/sign_in/google_oauth2callback")
def google_oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILEPATH,
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ],
        state=state)

    flow.redirect_uri = url_for('api_v1.google_oauth2callback', _external=True)

    authorization_response = request.url.replace('http://', 'https://')     # FIXME dev костыль
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = {'token': credentials.token,
                              'refresh_token': credentials.refresh_token,
                              'token_uri': credentials.token_uri,
                              'client_id': credentials.client_id,
                              'client_secret': credentials.client_secret,
                              'scopes': credentials.scopes}

    service = build('people', 'v1', credentials=credentials)
    result = service.people().get(
        resourceName='people/me',
        personFields='names,emailAddresses'
    ).execute()

    return jsonify({})
