import os
import requests
from flask import Flask, redirect, request, session, render_template, url_for
from markupsafe import Markup
from dotenv import load_dotenv
from pprint import pprint
import psycopg2
from psycopg2.extras import RealDictCursor
from connectDB import insert_user, fetch_user_by_email


load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

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

@app.route('/calendar')
def calendar():
    with open('templates/content/calendar.html', 'r', encoding='utf-8') as file:
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
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection error", 500
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

        if user:
            pprint('User found in the database.')
            
            return redirect(url_for('profile'))
        else:
            pprint('User not found, redirecting to signup.')
            return redirect(url_for('signup'))
    except Exception as e:
        print(f"Error fetching user: {e}")
        return "Error processing your request", 500
    finally:
        conn.close()
        
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session:
        return redirect(url_for('signin'))
    print("session data:", session)
    user = session.get('user') or session.get('userinfo')
    pprint(f'User session data: {user}')
    if user:
        pprint('Rendering profile page...')
        with open('templates/content/profile.html', 'r', encoding='utf-8') as file:
            main_content_html = Markup(file.read())
        return render_template('profile.html',
                               user=user,
                               page_title="Explicações em Lisboa",
                               title="Explicações em Lisboa",
                               main_content=main_content_html)
    else:
        return redirect(url_for('/'))        
        
@app.route('/signup')
def signup():
    pprint('Rendering signup page...')
    return render_template(
        'signup.html',
        page_title="Explicações em Lisboa",
        title="Explicações em Lisboa")

@app.route('/updateDB', methods=['GET', 'POST'])
def updateDB():
    pprint('Updating user in the database...')
    userinfo = session.get('userinfo')
    name = userinfo.get('name')
    email = userinfo.get('email')
    address = request.form.get('address')
    zip_code = request.form.get('zip_code')
    cell_phone = request.form.get('cell_phone')
    register_ip = request.remote_addr

    # if not all([name, email]):
    #     return "Name and Email are required!", 400

    success = insert_user(name, email, address, zip_code, cell_phone, register_ip)
    if success:
        session['user'] = {
            'name': name,
            'email': email,
            'address': address,
            'zip_code': zip_code,
            'cell_phone': cell_phone
        }
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
    
            
if __name__ == '__main__':
    app.run(debug=True)
