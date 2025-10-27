from flask import Blueprint, render_template, session,current_app, request, redirect,url_for
from markupsafe import Markup
from pprint import pprint
from Funhelpers import get_lisbon_greeting, render_profile_template


bp_signup = Blueprint('signup', __name__)


@bp_signup.route('/signup')
def signup():
    pprint('Rendering signup page...')
    user = session.get('user') or session.get('userinfo')
    if not session.get('metadata') :
        session['metadata'] = {}
    session["metadata"]["greeting"] = get_lisbon_greeting()

    email = ''
    given_name = ''
    family_name = ''
    is_google = False
    if user: # signup from email
        email = user['email']
        given_name = user['given_name']
        family_name = user['family_name']
        is_google = True
    else:
        # Get email from the query string
        email = request.args.get('email', '')

    if len(email) == 0:
        return redirect(url_for('signin.signin'))

    print(email)
    error_message = session.get("metadata").get("error_message",'')
    print(session.get("metadata"))

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