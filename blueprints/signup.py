from flask import Blueprint, render_template, session,current_app, request, redirect,url_for
from markupsafe import Markup
from pprint import pprint
from Funhelpers import get_lisbon_greeting, render_profile_template


bp_signup314 = Blueprint('signup314', __name__)
bp_signup = Blueprint('signup', __name__)


@bp_signup.route('/signup314', methods=['GET', 'POST'])
def signup314():
    pprint('Rendering signup page...')
    if not session.get('metadata') :
        session['metadata'] = {}
    session["metadata"]["greeting"] = get_lisbon_greeting()

    email = ''
    given_name = ''
    family_name = ''
    is_google = False

    if request.method == "POST": 
        email = request.form.get('email', '')
    elif request.method == "GET":
        user = session.get('user') or session.get('userinfo')
        email = user['email']
        given_name = user['given_name']
        family_name = user['family_name']
        is_google = True

    if len(email) == 0:
        return redirect(url_for('signin.signin'))

    # print(email)
    # error_message = session.get("metadata").get("error_message",'')
    # print(session.get("metadata"))

    # First render the content template with profile variables
    main_content_html = render_template(
        'content/signup.html',
        email_input=email,
        # error_message=error_message,
        is_google=is_google,
        given_name=given_name,
        family_name=family_name,
        **session.get("metadata", {} )
    )

    # Then render the main template with the rendered content
    return render_template(
        'index.html',
        user=None,
        # metadata=session.get("metadata"),
        admin_email=current_app.config['ADMIN_EMAIL'],
        main_content=Markup(main_content_html),
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa")


@bp_signup.route('/')
def signup():
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