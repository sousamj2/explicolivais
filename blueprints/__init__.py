# blueprints/__init__.py

# Optional: You can leave this empty or use it to export blueprints
from .check_user import check_user_bp
from .logout import logout_bp
from .oauth2callback import oauth2callback_bp
from .profile import profile_bp
from .signin_redirect import signin_redirect_bp
from .signin import signin_bp
from .signup import signup_bp
from .updateDB import updateDB_bp
from .pages import pages_bp


__all__ = ['check_user_bp',
           'logout_bp',
           'oauth2callback_bp',
           'profile_bp',
           'signin_redirect_bp',
           'signin_bp',
           'signup_bp',
           'updateDB_bp',
           'pages_bp'
    ]