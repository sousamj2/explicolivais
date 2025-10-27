from flask import Blueprint, request, session, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash  # pip install werkzeug for password hash comparison

from pprint import pprint
from DBhelpers import get_user_profile, refresh_last_login_and_ip,getHashFromEmail,getEmailFromUsername

bp_check_user = Blueprint('check_user', __name__, url_prefix='/check_user')


@bp_check_user.route('/', methods=['GET', 'POST'])
def check_user():
    pprint('Checking user in the database...')

    if request.method == 'POST':
        email = request.form.get('username','').lower()  # use 'username' if that's your form field name
        password = request.form.get('password','')

        if not email or not password:
            flash('Missing email or password.')
            return redirect(url_for('signin.signin'))

        if '@' not in email: # case for user name
            email = getEmailFromUsername(email)

        # Fetch the stored hash for this email
        hashval = getHashFromEmail(email)
        if hashval is None:
            flash('User not found.')
            return redirect(url_for('signin.signin'))
        
        # Verify password against hash
        if check_password_hash(hashval, password):
            user = get_user_profile(email)
            if user:
                refresh_last_login_and_ip(email, request.remote_addr)
                session["metadata"] = user
                # return redirect(url_for('profile.profile', source_method ='POST'))
                return redirect(url_for('profile.profile'))
            else:
                flash('Profile not found, please register.')
                return redirect(url_for('signup.signup'))
        else:
            flash('Incorrect password.')
            return redirect(url_for('signin.signin'))
        
    else:
        userinfo = session.get('userinfo')
        # pprint(userinfo)
        # pprint(session)["metadata"])
        if not userinfo or 'email' not in userinfo:
            return redirect(url_for('signup.signup'))

        email = userinfo['email']
        
        user = get_user_profile(email)

        if user:
            pprint('User found in the database.')
            refresh_last_login_and_ip(email, request.remote_addr)
            session["metadata"] = get_user_profile(email)
            # pprint(session['metadata'])
            # return redirect(url_for('profile.profile', source_method ='GET'))
            return redirect(url_for('profile.profile'))
        else:
            flash('Profile not found, please register.')
            # pprint('User not found, redirecting to signup.')
            return redirect(url_for('signup.signup'))