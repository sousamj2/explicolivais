from flask import Blueprint, render_template, session, url_for,current_app
from markupsafe import Markup

bp_signin = Blueprint('signin', __name__, url_prefix='/signin')
bp_signin314 = Blueprint('signin314', __name__, url_prefix='/signin314')


@bp_signin314.route('/')
def signin314():
    user = session.get('user') or session.get('userinfo')
    # Render the content template first
    main_content_html = render_template(
        'content/signin.html',
        logo_url=url_for('static', filename='images/google_logo.svg')
    )
    user = None

    # Then render the main template with the content
    return render_template(
        'index.html',
        admin_email=current_app.config['ADMIN_EMAIL'],
        user=user,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=Markup(main_content_html))

@bp_signin.route('/')
def signin():
    user = session.get('user') or session.get('userinfo')
    # Render the content template first
    main_content_html = render_template(
        'content/wip.html',
    )
    user = None

    # Then render the main template with the content
    return render_template(
        'index.html',
        admin_email=current_app.config['ADMIN_EMAIL'],
        user=user,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=Markup(main_content_html))