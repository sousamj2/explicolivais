from flask import Blueprint, request, session, redirect, url_for, current_app
from pprint import pprint
from DBhelpers import get_user_profile, refresh_last_login_and_ip

check_user_bp = Blueprint('check_user', __name__)


@check_user_bp.route('/check_user')
def check_user():
    pprint('Checking user in the database...')
    userinfo = session.get('userinfo')
    # pprint(userinfo)
    if not userinfo or 'email' not in userinfo:
        return redirect(url_for('signin.signin'))
    email = userinfo['email']
    
    user = get_user_profile(email)

    if user:
        pprint('User found in the database.')
        refresh_last_login_and_ip(email, request.remote_addr)
        session["metadata"] = get_user_profile(email)
        # pprint(session['metadata'])
        return redirect(url_for('profile.profile'))
    else:
        pprint('User not found, redirecting to signup.')
        return redirect(url_for('signup.signup'))