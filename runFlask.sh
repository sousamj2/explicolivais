#!/bin/bash

# Move to the script's directory to ensure relative paths work
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REMOTE_DB_IP="10.0.10.243" # Reverted to your manual setting
SSH_KEY="/home/ec2-user/.ssh/ec2_internal"
AWS_REGION="eu-south-2"

# Set environment
export APP_ENV=dev # Enable SSM loading

# Remote Database and Credential Assurance
if [[ "${APP_ENV}" == "dev" ]]; then
    echo -e "${YELLOW}📡 Signaling remote database on ${REMOTE_DB_IP}...${NC}"
    # We MUST succeed in signaling the remote machine before we wait for the port
    if ! ssh -i "${SSH_KEY}" -o ConnectTimeout=5 "ec2-user@${REMOTE_DB_IP}" "sudo systemctl start mcwebapp-db.service"; then
        echo -e "${RED}   ✗ CRITICAL: Could not reach remote machine or start DB service.${NC}"
        echo -e "${RED}     Please verify IP ${REMOTE_DB_IP} and SSH keys.${NC}"
        exit 1
    fi
    echo -e "${GREEN}   ✓ Remote signal sent successfully.${NC}"
    
    echo -e "${YELLOW}🔐 Fetching credentials from AWS SSM...${NC}"
    # Exporting these so they are available to the process and any subprocesses
    export ROOT_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/ROOT_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    export MC_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/MC_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    export EXPL_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/EXPL_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    # Also fetch SECRET_KEY if it's missing in .env
    if [ -z "$SECRET_KEY" ] && [ -z "$FLASK_SECRET_KEY" ]; then
         export SECRET_KEY=$(aws ssm get-parameter --name "/dev/SECRET_KEY" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    fi

    if [ -z "$ROOT_MYSQL_PASSWORD" ]; then
        echo -e "${RED}   ✗ Failed to fetch credentials from SSM. Falling back to .env defaults.${NC}"
    else
        echo -e "${GREEN}   ✓ Credentials fetched and remote DB signaled.${NC}"
        
        # Wait for the REMOTE MariaDB to be ready
        echo -e "${YELLOW}⏳ Waiting for remote MariaDB on ${REMOTE_DB_IP} to be ready...${NC}"
        for i in {1..30}; do
            # Use the remote DB port (usually 3306 or 3307 depending on your setup)
            # Based on your .env, the remote MariaDB on the other machine is at port 3307
            if nc -z -w 1 "${REMOTE_DB_IP}" 3307; then
                 break
            fi
            echo -n "."
            sleep 1
        done
        echo ""
    fi
fi

echo -e "   🚀 Creating tables if they don't exit"

# Get absolute path to the virtual environment
VENV_PATH=$(realpath ../app-env)

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
