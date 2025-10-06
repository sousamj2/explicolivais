import os
import requests
from flask import Flask, redirect, request, session, render_template, url_for, jsonify
from markupsafe import Markup
from dotenv import load_dotenv
from pprint import pprint
import psycopg2
from psycopg2.extras import RealDictCursor
from connectDB import insert_user, submit_query, results_to_html_table

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

def render_page(route="/", template_name="home", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata=None):
    def view_func():
        with open(f'templates/content/{template_name}.html', 'r', encoding='utf-8') as file:
            main_content_html = Markup(file.read())
        user = session.get('user') or session.get('userinfo')
        pprint(user)
        if not user and template_name == "profile":
            return redirect(url_for('signin'))
        elif (not user or user['email'].lower() != os.getenv('ADMINDB_EMAIL').lower()) and template_name == "adminDB":
            return redirect(url_for('signin'))

        # if template_name == "adminDB":


        return render_template(
            'index.html',
            admin_email=os.getenv('ADMINDB_EMAIL').lower(),
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
render_page(route="/profile" , template_name="profile"  , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/signin"  , template_name="signin"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/signup"  , template_name="signup"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(route="/logout"  , template_name="logout"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# The above function creates routes dynamically, so the below individual route definitions are commented out.
# They can be removed if the dynamic function works as intended.

@app.route('/adminDB', methods=['POST'])
def admin_db():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No SQL query provided'}), 400

    result = submit_query(query)
    if isinstance(result, str):  # Indicates an error message
        return jsonify({'error': result}), 400
    
    if isinstance(result, list):
        if len(result) > 0 and isinstance(result[0],str):
            result = " ("+",".join(result[1:]) + ") "
            return jsonify(result)
        
        html_table = results_to_html_table(result)
        # pprint(html_table)
        
        result = {'html_table': html_table}

    return jsonify(result)

@app.route('/signin')
def signin():
    logo_url = url_for('static', filename='images/google_logo.svg')
    with open('templates/content/signin.html', 'r', encoding='utf-8') as file:
        main_content_html = Markup(file.read())
        main_content_html = main_content_html.replace('STATIC_GOOGLE_LOGO', logo_url)
    user = session.get('user') or session.get('userinfo')
    return render_template(
        'index.html',
        admin_email=os.getenv('ADMINDB_EMAIL').lower(),
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
    # print("session data:", session)
    user = session.get('user') or session.get('userinfo')
    # pprint(f'User session data: {user}')
    if user:
        pprint('Rendering profile page...')
        with open('templates/content/profile.html', 'r', encoding='utf-8') as file:
            main_content_html = Markup(file.read())

        return render_template('index.html',
                               admin_email=os.getenv('ADMINDB_EMAIL').lower(),
                               user=user,
                               page_title="Explicações em Lisboa",
                               title="Explicações em Lisboa",
                               main_content=main_content_html)
    else:
        return redirect(url_for('/'))        
        
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    pprint('Rendering signup page...')
    user = session.get('user') or session.get('userinfo')
    return render_template(
        'signup.html',
        user=user,
        admin_email=os.getenv('ADMINDB_EMAIL').lower(),
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
    
            
# if __name__ == '__main__':
#     # app.run(debug=True)
#     pass