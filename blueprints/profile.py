from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from markupsafe import Markup
from pprint import pprint

from DBhelpers import get_user_profile
from Funhelpers import get_lisbon_greeting, format_data

bp_profile = Blueprint('profile', __name__, url_prefix='/profile')


@bp_profile.route('/')
def profile():
    # This 
    source_method = request.args.get('source_method', 'GET')

    email = None
    mypict =''
    # print(session.get("userinfo"))
    # print()
    # print(session.get("user"))
    # print()
    # print(session.get("metadata"))
    # print()
    # print(source_method)

    if session and session.get("metadata"):
        email  = session.get("metadata").get("email")
    else:
        return redirect(url_for('signin.signin'))

    if session and session.get("userinfo"):
        mypict = session.get("userinfo").get('picture','')

    # pprint(f'User session data: {user}')
    # pprint(session.get('userinfo'))
    # pprint(session)
    if email:
        pprint('Rendering profile page...')
        # print("email:",email,session["metadata"])
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

        zip_full = str(session["metadata"].get("zip_code1", "")) + "-" + str(session["metadata"].get("zip_code2", "")) 

        session["metadata"]["full_name"] = session["metadata"]["first_name"] + " " + session["metadata"]["last_name"]

        # print(session["metadata"]["first_name"])
        # print(session["metadata"]["last_name"])
        # print(session["metadata"]["full_name"])
        # print(session["metadata"].get("full_name", ""))

        # First render the content template with profile variables
        main_content_html = render_template(
            'content/profile.html',
            greeting=session["metadata"]["greeting"],
            full_name=session["metadata"].get("full_name", ""),
            email=session["metadata"].get("email", ""),
            lastlogin=format_data(session["metadata"].get("lastlogints", "")), # session["metadata"].get("lastlogin", ""),
            user_picture=mypict,
            vpn_check_color="green",  # These could come from session or be calculated
            primeiro_contacto_color="yellow",
            primeira_aula_color="red",
            morada=session["metadata"].get("full_address", ""),
            codigopostal=zip_full,
            nif=session["metadata"].get("nfiscal", ""),
            telemovel=session["metadata"].get("cell_phone", "")
        )

        # Then render the main template with the rendered content
        return render_template('index.html',
                            admin_email=current_app.config['ADMIN_EMAIL'],
                            user=session.get("userinfo"),
                            metadata=session.get("metadata"),
                            page_title="Explicações em Lisboa",
                            title="Explicações em Lisboa",
                            main_content=Markup(main_content_html))
    else:
        return redirect(url_for('index'))