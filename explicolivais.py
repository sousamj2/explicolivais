import os
from flask import Flask
from pprint import pprint

from dotenv import load_dotenv
load_dotenv()

# from DBhelpers import *
from blueprints import *
# check_user_bp,logout_bp,oauth2callback_bp,pages_bp, profile_bp, signin_redirect_bp,signin_bp,signup_bp,updateDB_bp


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Determine which config to use
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    app.register_blueprint(check_user_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(oauth2callback_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(signin_redirect_bp)
    app.register_blueprint(signin_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(updateDB_bp)

    
    # Main route
    @app.route('/')
    def index():
        return "Home Page"
    
    return app


# Create the app
app = create_app()

if __name__ == '__main__':
    app.run()

# with app.app_context():
#     # from connectDB import check_and_create_users_table
#     # check_and_create_users_table()
#     pass