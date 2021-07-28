import google_auth_oauthlib.flow
from flask import redirect, url_for, request, jsonify
from googleapiclient.discovery import build

from core import Config
from .api_bp import bp


@bp.route("/authorize/with_google")
def authorize_with_google():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
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
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
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
    first_name = result['names'][0]['givenName']
    last_name = result['names'][0]['familyName']

    return jsonify({})
