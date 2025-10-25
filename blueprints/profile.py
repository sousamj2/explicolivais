from flask import Blueprint, render_template, session, redirect, url_for,current_app
from pprint import pprint

from DBhelpers import get_user_profile
from Funhelpers import get_lisbon_greeting,render_profile_template

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
def profile():
    if not session:
        return redirect(url_for('signin.signin'))
    # print("session data:", session)
    user = session.get('user') or session.get('userinfo')
    # pprint(f'User session data: {user}')
    # pprint(session.get('userinfo'))
    if user:
        pprint('Rendering profile page...')
        # print(user)
        # if not session.get("metadata"):
        #     session["metadata"] = {}
        email = user['email']
        session["metadata"] = get_user_profile(email)
        session["metadata"]["greeting"] = get_lisbon_greeting()

        g_address = session["metadata"]["address"]
        if session["metadata"]["number"] != "NA": 
            g_address = session["metadata"]["address"] + ", " + str(session["metadata"]["number"])
        full_address = g_address
        if session["metadata"]["floor"] != "NA":
            full_address = full_address + " " + str(session["metadata"]["floor"])
        if session["metadata"]["door"]  != "NA":
            full_address = full_address + " " + str(session["metadata"]["door"])
        session["metadata"]["full_address"] = full_address
        session["metadata"]["g_address"] = g_address

        print(session)
        with open('templates/content/profile.html', 'r', encoding='utf-8') as file:
            
            main_content_html = render_profile_template(file.read())

        return render_template('index.html',
                                admin_email=current_app.config['ADMIN_EMAIL'],
                                #    user=user,
                                user = session.get("userinfo"),
                                metadata=session.get("metadata"),
                                page_title="Explicações em Lisboa",
                                title="Explicações em Lisboa",
                                main_content=main_content_html)
    else:
        return redirect(url_for('index'))