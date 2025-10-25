from flask import Blueprint, render_template, session,current_app
from markupsafe import Markup
from pprint import pprint
from Funhelpers import get_lisbon_greeting, render_profile_template


signup_bp = Blueprint('signup', __name__)


@signup_bp.route('/signup')
def signup():
    pprint('Rendering signup page...')
    user = session.get('user') or session.get('userinfo')
    if not session.get('metadata') :
        session['metadata'] = {}
    session["metadata"]["greeting"] = get_lisbon_greeting()

    with open('templates/content/signup.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(render_profile_template(file.read()))

    return render_template(
        'index.html',
        user=user,
        metadata=session.get("metadata"),
        admin_email=current_app.config['ADMIN_EMAIL'],
        main_content=main_content_html,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa")