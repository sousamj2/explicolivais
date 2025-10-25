from flask import Blueprint, redirect,current_app

signin_redirect_bp = Blueprint('signin_redirect', __name__)

@signin_redirect_bp.route('/signin_redirect')
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