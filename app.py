import os
import requests
from flask import Flask, redirect, request, session, render_template, url_for
from markupsafe import Markup
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Load client secrets from environment variables or a safe storage
CLIENT_ID = os.getenv('SECRET_CLIENT_KEY')
CLIENT_SECRET = os.getenv('SECRET_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/oauth2callback'  # Your redirect URI

# OAuth 2.0 endpoints
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
SCOPE = 'openid email profile'  # Scopes for user info

@app.route('/')
def index():
    with open('templates/content/home.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
    return render_template(
        'index.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)

@app.route('/maps')
def maps():
    with open('templates/content/maps.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
    return render_template(
        'index.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)

@app.route('/prices')
def prices():
    with open('templates/content/prices.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
    return render_template(
        'index.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)

@app.route('/terms')
def terms():
    with open('templates/content/terms.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
    return render_template(
        'index.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)

@app.route('/signin')
def signin():
    logo_url = url_for('static', filename='images/google_logo.svg')
    with open('templates/content/signin.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
        main_content_html = main_content_html.replace('STATIC_GOOGLE_LOGO', logo_url)
    return render_template(
        'index.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa",
        main_content=main_content_html)
    # return render_template('signin.html')

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
    userinfo = userinfo_response.json()
    pprint(userinfo)  # For debugging purposes

    # pprint(tokens)  # For debugging purposes

    return 'Authentication successful, tokens acquired!'

if __name__ == '__main__':
    app.run(debug=True)
