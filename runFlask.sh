#!/bin/bash

# Move to the script's directory to ensure relative paths work
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
# DEPLOY_TOPOLOGY: "single" (default, everything on one host) or "multi" (separate DB machine)
DEPLOY_TOPOLOGY="${DEPLOY_TOPOLOGY:-single}"
PROJECT_ID="${GCP_PROJECT_ID:-minecraft-server-july-12}"

# If multi-machine topology is explicitly chosen, configure remote DB details:
REMOTE_DB_IP="${REMOTE_DB_IP:-10.0.10.243}"
SSH_KEY="${REMOTE_DB_SSH_KEY:-$HOME/.ssh/id_rsa}"
REMOTE_DB_USER="${REMOTE_DB_USER:-$USER}"

# Set environment
export APP_ENV=dev
export DEPLOY_TOPOLOGY="${DEPLOY_TOPOLOGY}"
VENV_PATH=$(realpath ../app-env)

# Remote Database and Credential Assurance
if [[ "${APP_ENV}" == "dev" ]]; then
    if [[ "${DEPLOY_TOPOLOGY}" == "multi" ]]; then
        echo -e "${YELLOW}📡 Signaling remote database on ${REMOTE_DB_IP}...${NC}"
        if ! ssh -i "${SSH_KEY}" -o ConnectTimeout=5 "${REMOTE_DB_USER}@${REMOTE_DB_IP}" "sudo systemctl restart mcwebapp-db.service"; then
            echo -e "${RED}   ✗ CRITICAL: Could not reach remote machine or start DB service.${NC}"
            echo -e "${RED}     Please verify IP ${REMOTE_DB_IP} and SSH keys.${NC}"
            exit 1
        fi
        echo -e "${GREEN}   ✓ Remote signal sent successfully.${NC}"
    else
        echo -e "${GREEN}📦 Topology set to 'single' (local database / Cloud SQL). Skipping remote SSH signal.${NC}"
    fi
    
    echo -e "${YELLOW}🔐 Fetching configuration from GCP Secret Manager (PASS_CONFIG)...${NC}"
    SECRET_JSON=$(gcloud secrets versions access latest --secret="PASS_CONFIG" --project="${PROJECT_ID}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$SECRET_JSON" ]; then
        # Export all keys from the JSON as environment variables
        while IFS='=' read -r key value; do
            export "$key"="$value"
        done < <(python3 -c "import json, sys; data = json.loads(sys.stdin.read()); [print(f'{k}={v}') for k, v in data.items()]" <<< "$SECRET_JSON")
        echo -e "${GREEN}   ✓ Credentials fetched from GCP and exported.${NC}"
        
        # Determine target DB host for readiness check
        if [[ "${DEPLOY_TOPOLOGY}" == "multi" ]]; then
            TARGET_DB_HOST="${REMOTE_DB_IP}"
        else
            TARGET_DB_HOST="${MYSQL_HOST:-127.0.0.1}"
        fi
        TARGET_DB_PORT="${MYSQL_PORT:-3307}"

        # Wait for MariaDB to be ready
        echo -e "${YELLOW}⏳ Waiting for MariaDB on ${TARGET_DB_HOST}:${TARGET_DB_PORT} to be ready...${NC}"
        for i in {1..30}; do
            if $VENV_PATH/bin/python -c "
import pymysql, sys, os
try:
    pymysql.connect(
        host='${TARGET_DB_HOST}',
        port=int('${TARGET_DB_PORT}'),
        user=os.getenv('MYSQL_USER', 'dummy'),
        password=os.getenv('MYSQL_PASSWORD', 'dummy')
    )
except pymysql.err.OperationalError as e:
    if e.args[0] == 1045: sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
                 break
            fi
            echo -n "."
            sleep 1
        done
        echo ""
    else
        echo -e "${RED}   ✗ Failed to fetch credentials from GCP. Falling back to .env defaults.${NC}"
    fi
fi

echo -e "   🚀 Creating tables if they don't exit"

# Get absolute path to the virtual environment

$VENV_PATH/bin/python -c "import os;\
import sys;\
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')));\
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../mysql')));\
from DBhelpers import DBbaseline;\
import DBloadQuiz;\
DBbaseline.setup_mysql_database(app_name=\"explicolivais\");\
DBloadQuiz.loadQanswers();\
DBloadQuiz.loadQlinks();\
DBloadQuiz.loadQtemas();\
DBloadQuiz.loadQaulas();\
"

echo -e "   ✅ Tables are now up and running"
echo ""
echo ""
echo -e "${GREEN}🚀 Starting Flask Development Server${NC}"

# Set Flask environment
export FLASK_APP=explicolivais.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Get public IP for easy access
# PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")

echo -e "${YELLOW}📍 Access URLs:${NC}"
echo -e "   Direct: http://[$PUBLIC_IP]:8080"
echo -e "   Domain: https://www.explicolivais.com"
echo -e "   Local:  http://[::1]:8080"
echo ""
echo -e "${YELLOW}💡 Features enabled:${NC}"
echo -e "   ✅ Auto-reload on file changes"
echo -e "   ✅ Interactive debugger"
echo -e "   ✅ Detailed error pages"
echo ""
echo -e "${RED}Press Ctrl+C to stop${NC}"
echo ""

# Start Flask
$VENV_PATH/bin/flask run --host=:: --port=8080
