from flask import Blueprint, render_template, session, url_for,current_app
from markupsafe import Markup

signin_bp = Blueprint('signin', __name__)


@signin_bp.route('/signin')
def signin():
    logo_url = url_for('static', filename='images/google_logo.svg')
    with open('templates/content/signin.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
        main_content_html = main_content_html.replace('STATIC_GOOGLE_LOGO', logo_url)
    user = session.get('user') or session.get('userinfo')
    return render_template(
        'index.html',
        admin_email=current_app.config['ADMIN_EMAIL'],
        user=user,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)