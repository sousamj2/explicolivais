from flask import Blueprint, redirect,current_app

bp_signin_redirect = Blueprint('signin_redirect', __name__, url_prefix='/signin_redirect')

@bp_signin_redirect.route('/')
def signin_redirect():
    # Create the Google OAuth authorization URL
    auth_url = (
        f'{current_app.config["AUTHORIZATION_URL"]}?response_type=code'
        f'&client_id={current_app.config["CLIENT_ID"]}'
        f'&redirect_uri={current_app.config["REDIRECT_URI"]}'
        f'&scope={current_app.config["SCOPE"]}'
        f'&access_type=offline'
        f'&prompt=consent'
        f'&state=secure_random_state'
    )
    return redirect(auth_url)