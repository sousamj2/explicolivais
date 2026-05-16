import os
import platform
from typing import Dict, Optional

# Optional: keep dotenv for local usage only
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


APP_NAME = os.getenv("APP_NAME", "explicolivais")
APP_ENV = os.getenv("APP_ENV","dev")  # "production" or "development" or "testing"

# Heuristic to decide environment if APP_ENV not set
def _is_aws_host() -> bool:
    if APP_ENV:
        return APP_ENV.lower() == "dev"
    sysname = platform.system()
    nodename = platform.node()  # e.g., ip-xx-xx-xx-xx for EC2
    return sysname == "Linux" and nodename.startswith("ip-") and ".compute.internal" in nodename

def _load_from_env() -> Dict[str, str]:
    # Local/dev: load .env if library available
    if load_dotenv:
        # Search for .env in current directory and parent directory
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(dotenv_path):
            dotenv_path = os.path.join(os.getcwd(), '..', '.env')

        if os.path.exists(dotenv_path):
            print(f"[CONFIG] Loading .env from {os.path.abspath(dotenv_path)}", flush=True)
            load_dotenv(dotenv_path, override=True)
        else:
            print("[CONFIG] .env file not found in current or parent directory", flush=True)
            load_dotenv()  # Fallback to default search
    return dict(os.environ)

def _settings() -> Dict[str, str]:
    # Always load .env as baseline
    print("[CONFIG] Loading baseline config from local .env", flush=True)
    settings = _load_from_env()
    
    # OS environment now contains both .env values and any GCP secrets
    # exported by the shell script (runFlask.sh or start-services.sh).
    return dict(os.environ)

# Centralized lookup dictionary
SETTINGS = _settings()

def _get(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    val = SETTINGS.get(key, default)
    if required and (val is None or val == ""):
        raise ValueError(f"{key} environment variable must be set")
    return val

class Config:
    # Flask
    SECRET_KEY = _get("SECRET_KEY") or _get("FLASK_SECRET_KEY", required=True)

    # Admin config
    ADMIN_EMAIL = _get("ADMINDB_EMAIL", required=True)
    if ADMIN_EMAIL:
        ADMIN_EMAIL = ADMIN_EMAIL.lower()

    # Database
    DATABASE_URI = _get("DATABASE_URI", "sqlite:///default.db")

    # OAuth2 (Google)
    CLIENT_ID = _get("EXPL_SECRET_CLIENT_KEY") or _get("SECRET_CLIENT_KEY")
    CLIENT_SECRET = _get("EXPL_SECRET_CLIENT_SECRET") or _get("SECRET_CLIENT_SECRET")

    # print(CLIENT_ID)
    # print(CLIENT_SECRET)

    # Use separate redirect for production if provided, else default local
    REDIRECT_URI = _get("EXPL_OAUTH_REDIRECT_URI") or _get("OAUTH_REDIRECT_URI", "http://localhost:8080/oauth2callback")

    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = "openid email profile"

    # Mail (no-reply) — primary config used for mjcrafts.pt (default domain)
    MAIL_SERVER = _get("MC_MAIL_SERVER")
    MAIL_PORT = int(_get("MAIL_PORT", "465"))
    MAIL_USE_SSL = (_get("MAIL_USE_SSL", "True") == "True")
    MAIL_USERNAME = _get("MC_MAIL_DEFAULT_SENDER")
    MAIL_PASSWORD = _get("MC_MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = _get("MC_MAIL_DEFAULT_SENDER")

    # Google Cloud Mail Relay
    GOOGLE_MAIL_RELAY_URL = _get("GOOGLE_MAIL_RELAY_URL", "https://mail-relay-783543567741.europe-southwest1.run.app")

    # Optional secondary secret items
    SECURITY_PASSWORD_SALT = _get("SECURITY_PASSWORD_SALT")

    # Google Calendar service account
    SERVICE_ACCOUNT_FILE = _get("SERVICE_ACCOUNT_FILE", "./primeiro-contact-account.json")
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_ID = _get("CALENDAR_ID", "CHANGE_ME")

    # Scheduling
    MAX_SLOTS_PER_TIME = int(_get("MAX_SLOTS_PER_TIME", "4"))
    APPOINTMENT_DURATION = int(_get("APPOINTMENT_DURATION", "10"))
    WEEKLY_SCHEDULE = {
        0: [("15:00", "17:00")],
        1: [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")],
        2: [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")],
        3: [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")],
        4: [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")],
        5: [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")],
        6: [("08:00", "10:00"), ("10:00", "12:00"), ("13:00", "15:00")],
    }

    # RDS Connection to MySQL
    MYSQL_PASSWORD = _get("EXPL_MYSQL_PASSWORD") or _get("MYSQL_PASSWORD")
    MYSQL_HOST     = _get("EXPL_MYSQL_HOST") or _get("MYSQL_HOST")
    MYSQL_USER     = _get("EXPL_MYSQL_USER") or _get("MYSQL_USER") or "admin"
    MYSQL_DBNAME   = _get("EXPL_MYSQL_DBNAME") or "explicolivais"
    MYSQL_PORT     = int(_get("EXPL_MYSQL_PORT") or _get("MYSQL_PORT") or "3306")
    
    # Alt domain mail config — used when visiting explicacoeslisboa.pt
    ALT_DOMAIN = _get("EXPL_ALT_DOMAIN")
    ALT_MAIL_SERVER = _get("EXPL_MAIL_SERVER")
    ALT_MAIL_SENDER = _get("EXPL_MAIL_DEFAULT_SENDER")
    ALT_MAIL_PASSWORD = _get("EXPL_MAIL_PASSWORD")
    ALT_MAIL_PORT = int(_get("EXPL_MAIL_PORT") or "465")
    
    if not MYSQL_PASSWORD or not MYSQL_USER:
        print("[CONFIG] CRITICAL ERROR: explicolivais Database credentials (MYSQL_USER or MYSQL_PASSWORD) are missing. Please check AWS SSM or local .env.", flush=True)
        import sys
        sys.exit(1)


    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
