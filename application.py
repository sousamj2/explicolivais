import locale
import os
import requests
from flask import Flask, redirect, request, session, render_template, url_for, jsonify
from markupsafe import Markup
from pprint import pprint
import psycopg2
from psycopg2.extras import RealDictCursor
# from connectDB import insert_user, submit_query, results_to_html_table, get_db_connection, check_ip_in_portugal, get_user_profile, refresh_last_login_and_ip, get_lisbon_greeting
from connectDB import check_ip_in_portugal, get_lisbon_greeting, mask_email,valid_cellphone,valid_NIF
from datetime import datetime, timedelta
from typing import Any, Mapping, cast
import locale
import pytz
import bleach
from urllib.parse import quote_plus

from dotenv import load_dotenv
load_dotenv()

from DBinsertTables import *
from DBselectTables import * 
from DBupdateTables import *

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Validate required environment variables at startup
admin_email = os.getenv('ADMINDB_EMAIL')
if admin_email is None:
    raise ValueError("ADMINDB_EMAIL environment variable must be set")
app.config['ADMIN_EMAIL'] = admin_email.lower()

with app.app_context():
    # from connectDB import check_and_create_users_table
    # check_and_create_users_table()
    pass

# Load client secrets from environment variables or a safe storage
CLIENT_ID = os.getenv('SECRET_CLIENT_KEY')
CLIENT_SECRET = os.getenv('SECRET_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/oauth2callback'  # Your redirect URI

# OAuth 2.0 endpoints
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
SCOPE = 'openid email profile'  # Scopes for user info

def render_page(route="/", template_name="home", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata=None):
    def view_func():
        with open(f'templates/content/{template_name}.html', 'r', encoding='utf-8') as file:
            if route == "/maps":
                print(session.get("metadata"))
                main_content_html = render_profile_template(Markup(file.read()))
            else :
                main_content_html = Markup(file.read())
        user = session.get('user') or session.get('userinfo')
        # pprint(user)
        if not user and template_name == "profile":
            return redirect(url_for('signin'))
        elif (not user or user['email'].lower() != app.config['ADMIN_EMAIL']) and template_name == "adminDB":
            return redirect(url_for('signin'))

        if route == "/profile":
            pprint("metadata is:", metadata)

        # if template_name == "adminDB":

        return render_template(
            'index.html',
            admin_email=app.config['ADMIN_EMAIL'],
            user=user,
            metadata=metadata,
            page_title=page_title,
            title=title,
            main_content=main_content_html
            )
    view_func.__name__ = f'view_func_{template_name.replace("-", "_").replace("/", "_")}'
    app.route(route, methods=['GET'])(view_func)
    return view_func

render_page(route="/"        , template_name="home"     , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(route="/maps"    , template_name="maps"     , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(route="/prices"  , template_name="prices"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(route="/calendar", template_name="calendar" , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(route="/terms"   , template_name="terms"    , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(route="/adminDB" , template_name="adminDB"  , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/profile" , template_name="profile"  , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={session["metadata"]})
# render_page(route="/signin"  , template_name="signin"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/signup"  , template_name="signup"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/logout"  , template_name="logout"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# The above function creates routes dynamically, so the below individual route definitions are commented out.
# They can be removed if the dynamic function works as intended.

# @app.route('/adminDB', methods=['POST'])
# def admin_db():
#     data = request.json
#     query = data.get('query')
#     if not query:
#         return jsonify({'error': 'No SQL query provided'}), 400

#     result = submit_query(query)
#     if isinstance(result, str):  # Indicates an error message
#         return jsonify({'error': result}), 400
    
#     if isinstance(result, list):
#         if len(result) > 0 and isinstance(result[0],str):
#             result = " ("+",".join(result[1:]) + ") "
#             return jsonify(result)
        
#         html_table = results_to_html_table(result)
#         # pprint(html_table)
        
#         result = {'html_table': html_table}

#     return jsonify(result)

@app.route('/signin')
def signin():
    logo_url = url_for('static', filename='images/google_logo.svg')
    with open('templates/content/signin.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
        main_content_html = main_content_html.replace('STATIC_GOOGLE_LOGO', logo_url)
    user = session.get('user') or session.get('userinfo')
    return render_template(
        'index.html',
        admin_email=app.config['ADMIN_EMAIL'],
        user=user,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)

@app.route('/signin_redirect')
def signin_redirect():
    # Create the Google OAuth authorization URL
    auth_url = (
        f'{AUTHORIZATION_URL}?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope={SCOPE}'
        f'&access_type=offline'
        f'&prompt=consent'
        f'&state=secure_random_state'
    )
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    # Exchange code for tokens
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    tokens = response.json()

    # Save tokens in session or your database
    session['access_token'] = tokens.get('access_token')
    session['id_token'] = tokens.get('id_token')
    
    userinfo_response = requests.post(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {session["access_token"]}'}
    )
    session['userinfo'] = userinfo_response.json()
    userinfo = userinfo_response.json()
    # pprint(userinfo)  # For debugging purposes
    # print()
    # pprint(tokens)  # For debugging purposes
    pprint( 'Authentication successful, tokens acquired!')
    return redirect(url_for('check_user'))

@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    pprint('Checking user in the database...')
    userinfo = session.get('userinfo')
    # pprint(userinfo)
    if not userinfo or 'email' not in userinfo:
        return redirect(url_for('signin'))
    email = userinfo['email']
    
    user = get_user_profile(email)

    if user:
        pprint('User found in the database.')
        refresh_last_login_and_ip(email, request.remote_addr)
        session["metadata"] = get_user_profile(email)
        # pprint(session['metadata'])
        return redirect(url_for('profile'))
    else:
        pprint('User not found, redirecting to signup.')
        return redirect(url_for('signup'))
        
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session:
        return redirect(url_for('signin'))
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
                                admin_email=app.config['ADMIN_EMAIL'],
                                #    user=user,
                                user = session.get("userinfo"),
                                metadata=session.get("metadata"),
                                page_title="Explicações em Lisboa",
                                title="Explicações em Lisboa",
                                main_content=main_content_html)
    else:
        return redirect(url_for('/'))        
        
@app.route('/signup', methods=['GET', 'POST'])
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
        admin_email=app.config['ADMIN_EMAIL'],
        main_content=main_content_html,
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa")



@app.route('/updateDB', methods=['GET', 'POST'])
def updateDB():
    pprint('Updating user in the database...')
    userinfo = session.get('userinfo', {})
    # pprint(userinfo)
    first_name = userinfo.get('given_name')
    last_name = userinfo.get('family_name')
    email = userinfo.get('email')

    notes = "NA"

    # Helper: request.form.get can return None; coerce to empty string before cleaning
    def get_clean(field: str, default: str = "") -> str:
        return bleach.clean(request.form.get(field) or default)

    address = get_clean('address')
    number = get_clean('number') or "NA"
    floor = get_clean('floor') or "NA"
    door = get_clean('door') or "NA"
    zip_code1 = get_clean('zip_code1')
    zip_code2 = get_clean('zip_code2')
    cell_phone = get_clean('cell_phone')
    nif = get_clean('nfiscal')
    g_address = address
    if number != "NA":
        g_address = address + ", " + str(number)
    full_address = g_address
    if floor != "NA":
        full_address += ", " + str(floor)
    if door != "NA":
        full_address += " " + str(door)
    session['metadata'] = {
        'name': (first_name or "") + " " + (last_name or ""),
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'full_address': full_address,
        'g_address': g_address,
        'address': address,
        'number': number,
        'floor': floor,
        'door': door,
        'notes': notes,
        'zip_code1': str(zip_code1),
        'zip_code2': str(zip_code2),
        'zip_code': str(zip_code1) + "-" + str(zip_code2),
        'cell_phone': cell_phone,
        'nfiscal': nif
    }
    session['error_message'] = ""
    print("------------------------------------------------")
    errorMessage = ""
    sameEmail = getDataFromEmail(email)
    print("sameEmail", sameEmail)
    if sameEmail:
        sameEmail_map = cast(Mapping[str, Any], sameEmail)
        errorMessage += f"Este email ({sameEmail_map.get('email','')}) já tem uma conta aqui criada em {sameEmail_map.get('createdatts','')}. <br>\n"
    register_ip = request.remote_addr
    # sameIP = getDataFromIPcreated(register_ip)
    # print("sameIP",sameIP)
    # if sameIP:
    #     errorMessage += f"Este IP ({register_ip}) já registou o email {mask_email(sameIP["email"])} em {sameIP["createdatts"]}.<br>\n"
    sameNIF = getDataFromNIF(nif)
    print("sameNIF",sameNIF)
    if sameNIF:
        sameNIF_map = cast(Mapping[str, Any], sameNIF)
        errorMessage += f"Este NIF ({nif}) já pertence a uma conta com o email {mask_email(sameNIF_map.get('email',''))} em {sameNIF_map.get('createdatts','')}.<br>\n"
    sameCell = getDataFromCellNumber(cell_phone)
    print("sameCell",sameCell)
    if sameCell:
        sameCell_map = cast(Mapping[str, Any], sameCell)
        errorMessage += f"Este Telemóvel ({cell_phone}) já pertence a uma conta com o email {mask_email(sameCell_map.get('email',''))} em {sameCell_map.get('createdatts','')}.<br>\n"
    if not check_ip_in_portugal(register_ip):
        pprint(f"IP {register_ip} is not from Lisboa/Portugal.")
        errorMessage += f"Este endereço de IP {register_ip} está localizado fora de Lisboa. Tente de novo quando voltar. <br> Nota: só é necessário para o registro não para o acesso.<br>\n"
    if not valid_NIF (nif):
        errorMessage += f"Este NIF ({nif}) não é válido. <br> \n"
    if not valid_cellphone (cell_phone):
        errorMessage += f"Este telemóvel ({cell_phone}) não é válido. <br> \n"
    print("------------------------------------------------")

    if len(errorMessage) > 0:
        session['metadata']['error_message'] = errorMessage
        print(errorMessage)
        return redirect(url_for('signup'))

    successUser = insertNewUser(first_name,last_name,email)
    successPers = insertNewPersonalData(email, address, number, floor, door, notes, zip_code1,zip_code2,cell_phone,nif)
    successIP   = insertNewIP(email,register_ip)
    successConn = insertNewConnectionData(email,register_ip)
    if successPers and successUser and successIP and successConn:

        return redirect(url_for('profile'))
    else:
        return "Error registering user", 500

@app.route('/logout')
def logout():
    # Revoke token if exists
    access_token = session.get('access_token')
    if access_token:
        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                               params={'token': access_token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})
        if revoke.status_code == 200:
            print("Google token revoked successfully")
        else:
            print("Failed to revoke token")

    # Clear Flask session
    session.clear()

    # Redirect to sign-in or homepage
    return redirect(url_for('signin'))  # or your login route


def format_data(timestampUTC):
    print("-----------------------",timestampUTC)
    try:
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
        
        dt = datetime.fromisoformat(timestampUTC)
        dt = dt - timedelta(hours=1)
        lisbon_tz = pytz.timezone('Europe/Lisbon')
        
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        # print(f"Original datetime: {dt} with tz: {dt.tzinfo}")
        
        # dt_local = lisbon_tz
        dt_local = dt.astimezone(lisbon_tz)
        # print(f"Converted to Lisbon timezone: {dt_local} with tz: {dt_local.tzinfo}")
        
        now_local = datetime.now(lisbon_tz).date()
        dt_date = dt_local.date()
        yesterday = now_local - timedelta(days=1)
        
        if dt_date == now_local:
            date_str = "hoje"
        elif dt_date == yesterday:
            date_str = "ontem"
        else:
            date_str = dt_local.strftime('em %-d de %B de %Y')
        
        time_str = dt_local.strftime('às %H:%M')
        return f"{date_str} {time_str}"
        
    except Exception as e:
        print(f"Error formatting date: {e}")
        return timestampUTC


def render_profile_template(template_text):
    userinfo = session.get("userinfo", {})
    metadata = session.get("metadata", {})
    template_text = str(template_text)
    # Example replacements; add more as needed
    rendered = template_text.replace("{{user_picture}}", userinfo.get("picture", ""))
    rendered = rendered.replace("{{greeting}}", metadata.get("greeting", ""))
    rendered = rendered.replace("{{nome}}", " ".join([metadata.get("first_name", ""), metadata.get("last_name", "")]))
    rendered = rendered.replace("{{email}}", metadata.get("email", ""))
    rendered = rendered.replace("{{lastlogin}}", format_data(metadata.get("lastlogints", "")))
    rendered = rendered.replace("{{morada}}", metadata.get("full_address", ""))
    rendered = rendered.replace("{{codigopostal}}", str(metadata.get("zip_code1", ""))+'-'+str(metadata.get("zip_code2", ""))) 
    rendered = rendered.replace("{{nif}}", str(metadata.get("nfiscal", "")))
    rendered = rendered.replace("{{telemovel}}", str(metadata.get("cell_phone", "")))

    rendered = rendered.replace("{{cell_phone}}", str(metadata.get("cell_phone", "")))
    rendered = rendered.replace("{{zip_code1}}", str(metadata.get("zip_code1", "")))
    rendered = rendered.replace("{{zip_code2}}", str(metadata.get("zip_code2", "")))
    rendered = rendered.replace("{{address}}", str(metadata.get("address", "")))
    rendered = rendered.replace("{{number}}", str(metadata.get("number", "")))
    rendered = rendered.replace("{{floor}}", str(metadata.get("floor", "")))
    rendered = rendered.replace("{{door}}", str(metadata.get("door", "")))
    rendered = rendered.replace("{{nfiscal}}", str(metadata.get("nfiscal", "")))
    rendered = rendered.replace("{{error_message}}", str(metadata.get("error_message", "")))
    rendered = rendered.replace("{{gg_address}}", str(format_address_for_url(metadata.get("g_address",""))))
    # Replace boolean fields for LEDs (example: 'green' if True else 'orange')
    vpn_check = metadata.get("vpn_check", False)
    primeiro_contacto = metadata.get("first_contact_complete", False)
    primeira_aula = metadata.get("first_session_complete", False)
    rendered = rendered.replace("{{vpn_check_color}}", "green" if vpn_check else "orange")
    rendered = rendered.replace("{{primeiro_contacto_color}}", "green" if primeiro_contacto else "orange")
    rendered = rendered.replace("{{primeira_aula_color}}", "green" if primeira_aula else "orange")

    return Markup(rendered)

def format_address_for_url(address):
    """
    Takes an address string and returns it formatted for use in a URL.
    
    Args:
        address (str): The address to format (e.g., "Rua Cidade de Nampula, 1, 1800 Lisboa")
    
    Returns:
        str: URL-encoded address
    """
    return quote_plus(address)

