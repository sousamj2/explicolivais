import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mysql')))

from flask import Flask, redirect, render_template, request
from Funhelpers import mail
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
load_dotenv()
# from DBhelpers import *
from blueprints import *
from mailinteraction import bp_mail_relay
# check_user_bp,logout_bp,oauth2callback_bp,pages_bp, profile_bp, signin_redirect_bp,signin_bp,signup_bp,updateDB_bp

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static'
                )

    # Determine which config to use
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    app.config["PREFERRED_URL_SCHEME"] = "https"
    
    # Initialize Rate Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri="memory://",
        default_limits=["20 per minute"],
        default_limits_exempt_when=lambda: request.path.startswith('/static/') or request.method != 'GET'
    )
    
    # Initialize Flask-Mail via the extension pattern to avoid assigning new attributes on Flask
    mail.init_app(app)
    # print("Mail state after init_app:", mail.state)
    
    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('images/favicon.png')
    
    app.register_blueprint(bp_check_user)
    # app.register_blueprint(bp_check_user314)
    app.register_blueprint(bp_logout)
    app.register_blueprint(bp_oauth2callback)
    app.register_blueprint(bp_home)
    app.register_blueprint(bp_maps)
    app.register_blueprint(bp_prices)
    app.register_blueprint(bp_calendar)
    app.register_blueprint(bp_terms)
    app.register_blueprint(bp_adminDB)
    app.register_blueprint(bp_profile)
    app.register_blueprint(bp_signin_redirect)
    # app.register_blueprint(bp_signin_redirect314)
    app.register_blueprint(bp_signin)
    # app.register_blueprint(bp_signin314)
    app.register_blueprint(bp_signup)
    # app.register_blueprint(bp_signup314)
    app.register_blueprint(bp_updateDB)
    # app.register_blueprint(bp_updateDB314)
    app.register_blueprint(bp_register)
    app.register_blueprint(bp_mail_relay)
    # app.register_blueprint(bp_register314)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(quiz_assets_bp)
    app.register_blueprint(bp_elevate_tier)
    app.register_blueprint(bp_elevate_tier314)
    
    @app.context_processor
    def inject_copyright():
        from flask import request
        host = request.host
        
        # Determine display name based on domain
        if "mjcrafts.pt" in host:
            display_name = "MJCRAFTS.PT"
            year = 2026
        else:
            display_name = "EXPLICACOESLISBOA.PT"
            year = "2025-2026"
            
        return {
            'current_year': year,
            'copyright_name': display_name
        }
    
    
    # Main route: redirect to /pages/ (home)
    @app.route('/')
    def index():
        return redirect('/')
    
    return app


# Create the app
app = create_app()

@app.cli.command("send-email")
def send_email_command():
    """CLI command to send email from stdin JSON."""
    import sys
    import json
    from mailinteraction import send_email
    try:
        data = json.load(sys.stdin)
        send_email(
            data['subject'], 
            data['email_to'], 
            data['html_message'], 
            sender=data.get('sender')
        )
        print("Email sent successfully via CLI", flush=True)
    except Exception as e:
        print(f"Error sending email via CLI: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # Number of values to trust in X-Forwarded-For
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)


if __name__ == '__main__':
    app.run()

# with app.app_context():
#     # from connectDB import check_and_create_users_table
#     # check_and_create_users_table()
#     pass