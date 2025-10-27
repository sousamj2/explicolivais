from flask import Blueprint, session, redirect, url_for,current_app
import requests

bp_logout = Blueprint('logout', __name__, url_prefix='/logout')


@bp_logout.route('/')
def logout():
    # Revoke token if exists
    access_token = session.get('access_token')
    if access_token:
        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': access_token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})
        if revoke.status_code == 200:
            print("Google token revoked successfully")
        else:
            print("Failed to revoke token")

    # Clear Flask session
    session.clear()

    # Redirect to sign-in or homepage
    return redirect(url_for('signin.signin'))  # or your login route