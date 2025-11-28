import os
from flask import Flask, redirect, render_template
from pprint import pprint
from Funhelpers import mail

from dotenv import load_dotenv
load_dotenv()

# from DBhelpers import *
from blueprints import *
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
    
    # Initialize Flask-Mail via the extension pattern to avoid assigning new attributes on Flask
    mail.init_app(app)
    print("Mail state after init_app:", mail.state)
    
    app.register_blueprint(bp_check_user)
    app.register_blueprint(bp_check_user314)
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
    app.register_blueprint(bp_signin_redirect314)
    app.register_blueprint(bp_signin)
    app.register_blueprint(bp_signin314)
    app.register_blueprint(bp_signup)
    app.register_blueprint(bp_signup314)
    app.register_blueprint(bp_updateDB)
    app.register_blueprint(bp_updateDB314)
    app.register_blueprint(bp_register)
    app.register_blueprint(bp_register314)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(quiz_assets_bp)
    
    # Main route: redirect to /pages/ (home)
    @app.route('/')
    def index():
        return redirect('/')
    
    return app


# Create the app
app = create_app()

if __name__ == '__main__':
    app.run()

# with app.app_context():
#     # from connectDB import check_and_create_users_table
#     # check_and_create_users_table()
#     pass