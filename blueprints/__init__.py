
# Import and export all blueprints
from .check_user import bp_check_user
from .logout import bp_logout
from .oauth2callback import bp_oauth2callback
from .profile import bp_profile
from .signin_redirect import bp_signin_redirect
from .signin import bp_signin,bp_signin314
from .signup import bp_signup,bp_signup314
from .updateDB import bp_updateDB,bp_updateDB314
from .pages import bp_home, bp_maps, bp_prices, bp_calendar, bp_terms, bp_adminDB
from .register import bp_register,bp_register314
from .request_new_user import bp_request_new_user
from .quiz import quiz_bp
from .quiz_assets import quiz_assets_bp


__all__ = [
    'bp_check_user',
    'bp_logout',
    'bp_oauth2callback',
    'bp_profile',
    'bp_signin_redirect',
    'bp_signin',
    'bp_signup',
    'bp_updateDB',
    'bp_home',
    'bp_maps',
    'bp_prices',
    'bp_calendar',
    'bp_terms',
    'bp_adminDB',
    'bp_register',
    'bp_request_new_user',
    'quiz_bp',
    'quiz_assets_bp',
    'bp_signin314',
    'bp_updateDB314',
    'bp_register314',
    'bp_signup314',
    ]