import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask config
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError("FLASK_SECRET_KEY environment variable must be set")
    
    # Admin config
    ADMIN_EMAIL = os.getenv('ADMINDB_EMAIL')
    if ADMIN_EMAIL is None:
        raise ValueError("ADMINDB_EMAIL environment variable must be set")
    ADMIN_EMAIL = ADMIN_EMAIL.lower()
    
    # Database config (example)
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///default.db')
    
    # Load client secrets from environment variables or a safe storage
    CLIENT_ID = os.getenv('SECRET_CLIENT_KEY')
    CLIENT_SECRET = os.getenv('SECRET_CLIENT_SECRET')
    REDIRECT_URI = 'http://localhost:8080/oauth2callback'  # Your redirect URI

    # OAuth 2.0 endpoints
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    SCOPE = 'openid email profile'  # Scopes for user info

    SERVICE_ACCOUNT_FILE = './primeiro-contact-account.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CALENDAR_ID = '982d2d8cb74e54a702ffaaedd1aa7fdc7fa2645931fbd4abb6b80c3da8dd2541@group.calendar.google.com'

    # Scheduling configuration
    MAX_SLOTS_PER_TIME = 4  # Maximum 4 people per time slot
    APPOINTMENT_DURATION = 10  # 10 minutes per appointment

    # Weekly schedule definition
    WEEKLY_SCHEDULE = {
        0: [('15:00', '17:00')],  # Sunday
        1: [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '16:00'), ('16:00', '18:00'), ('18:00', '20:00')],  # Monday
        2: [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '16:00'), ('16:00', '18:00'), ('18:00', '20:00')],  # Tuesday
        3: [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '16:00'), ('16:00', '18:00'), ('18:00', '20:00')],  # Wednesday
        4: [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '16:00'), ('16:00', '18:00'), ('18:00', '20:00')],  # Thursday
        5: [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '16:00'), ('16:00', '18:00'), ('18:00', '20:00')],  # Friday
        6: [('08:00', '10:00'), ('10:00', '12:00'), ('13:00', '15:00')],  # Saturday
    }

    # Other settings
    DEBUG = False
    TESTING = False
    

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
