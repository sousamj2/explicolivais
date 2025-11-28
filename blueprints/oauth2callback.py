from flask import Blueprint, request, session, redirect, url_for,current_app
import requests

bp_oauth2callback = Blueprint('oauth2callback', __name__, url_prefix='/oauth2callback')


@bp_oauth2callback.route('/')
def oauth2callback():
    code = request.args.get('code')
    # Exchange code for tokens
    data = {
        'code': code,
        'client_id': current_app.config["CLIENT_ID"],
        'client_secret': current_app.config["CLIENT_SECRET"],
        'redirect_uri': current_app.config["REDIRECT_URI"],
        'grant_type': 'authorization_code'
    }
    response = requests.post(current_app.config["TOKEN_URL"], data=data)
    tokens = response.json()

    # Save tokens in session or your database
    session['access_token'] = tokens.get('access_token')
    session['id_token'] = tokens.get('id_token')
    
    userinfo_response = requests.post(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {session["access_token"]}'}
    )
    session['userinfo'] = userinfo_response.json()
    userinfo = userinfo_response.json()
    # pprint(userinfo)  # For debugging purposes
    # print()
    # pprint(tokens)  # For debugging purposes
    print( 'Authentication successful, tokens acquired!')
    return redirect(url_for('check_user314.check_user314'))