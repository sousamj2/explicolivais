from flask import Blueprint, request, session, redirect, url_for,current_app, render_template
from pprint import pprint
import bleach
from Funhelpers import check_ip_in_portugal, valid_cellphone,valid_NIF, mask_email
from DBhelpers import *
from typing import Any, Mapping, cast
from werkzeug.security import generate_password_hash
import re
from markupsafe import Markup

bp_updateDB = Blueprint('updateDB', __name__)
bp_updateDB314 = Blueprint('updateDB314', __name__)

@bp_updateDB.route('/updateDB', methods = ["GET","POST"])
def updateDB():
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


@bp_updateDB314.route('/updateDB314', methods=["GET", "POST"])
def updateDB314():
    """TIER 1: Initial registration - only basic user data"""
    
    pprint('Creating Tier 1 user...')
    userinfo = session.get('userinfo', {})
    
    def get_clean(field: str, default: str = "") -> str:
        return bleach.clean(request.form.get(field) or default)
    
    first_name = userinfo.get('given_name') or get_clean('given_name')
    last_name = userinfo.get('family_name') or get_clean('family_name')
    email = (userinfo.get('email') or get_clean('email')).lower()
    errorMessage = ""
    
    username = None
    if userinfo.get('email'):
        username = email
    else:
        username = get_clean('username').lower()
        if username != email and not re.match(r'^[A-Za-z0-9._-]+$', username):
            errorMessage += "O username pode conter letras, números ou os símbolos '.' , '-' ou '_'\n"
            errorMessage += "Em alternativa pode utilizar o email como username."
    
    h_password = None
    password = get_clean('password') or None
    if password:
        h_password = generate_password_hash(password)
    
    register_ip = request.headers.get('X-Real-IP')
    if not register_ip : register_ip = request.remote_addr
    
    # Validation
    sameEmail = getDataFromEmail(email)
    if sameEmail:
        sameEmail_map = cast(Mapping[str, Any], sameEmail)
        errorMessage += f"Este email ({sameEmail_map.get('email','')}) já tem uma conta aqui criada em {sameEmail_map.get('createdatts','')}.\n"
    
    if not check_ip_in_portugal(register_ip):
        errorMessage += f"Este endereço de IP {register_ip} está localizado fora de Lisboa. Tente de novo quando voltar.\n"
    
    if len(errorMessage) > 0:
        session['metadata']['error_message'] = errorMessage
        print(errorMessage)
        return redirect(url_for('signup314.signup314', email=email))
    
    # TIER 1: Only these three functions
    successUser = insertNewUser(first_name, last_name, email, h_password, username)
    successIP = insertNewIP(email, register_ip)
    successConn = insertNewConnectionData(email, register_ip)
    
    if successUser and successIP and successConn:
        # Store in session and redirect to profile
        session['metadata'] = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'tier': 1  # New user starts at tier 1
        }
        session.modified = True
        return redirect(url_for('profile.profile'))
    else:
        return "Error registering user", 500
