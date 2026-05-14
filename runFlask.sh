#!/bin/bash

# Move to the script's directory to ensure relative paths work
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "   🚀 Creating tables if they don't exit"

# Get absolute path to the virtual environment
VENV_PATH=$(realpath ../app-env)

# export APP_ENV=local

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
# export FLASK_APP=application.py
export FLASK_APP=explicolivais.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export APP_ENV=dev # Changed from local to dev to trigger SSM loading

# Remote Database Assurance (EC2-1 -> EC2-2)
if [[ "${APP_ENV}" == "dev" ]]; then
    REMOTE_DB_IP="10.0.14.15"
    SSH_KEY="/home/ec2-user/.ssh/ec2_internal"
    
    echo -e "${YELLOW}📡 Ensuring remote database on ${REMOTE_DB_IP} is running...${NC}"
    
    # Try to start the DB service on the remote machine
    # We use -o ConnectTimeout to fail fast if the machine is down
    ssh -i "${SSH_KEY}" -o ConnectTimeout=5 "ec2-user@${REMOTE_DB_IP}" "sudo systemctl start mcwebapp-db"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✓ Remote database service signaled successfully.${NC}"
    else
        echo -e "${RED}   ✗ Failed to reach remote database machine or start service.${NC}"
        echo -e "${RED}     Please check the SSH connection or the remote mcwebapp-db service.${NC}"
        # We don't exit 1 here to allow local dev fallback if desired, 
        # but the app might fail later if it can't connect to RDS/Docker.
    fi
fi

# Fetch DB credentials from SSM if on AWS
if [[ "${APP_ENV}" == "dev" ]]; then
    echo -e "${YELLOW}🔐 Fetching DB credentials from AWS SSM...${NC}"
    AWS_REGION="eu-south-2"
    
    # Exporting these so they are available to the process and any subprocesses
    export ROOT_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/ROOT_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    export MC_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/MC_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    export EXPL_MYSQL_PASSWORD=$(aws ssm get-parameter --name "/dev/EXPL_MYSQL_PASSWORD" --with-decryption --query "Parameter.Value" --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -z "$ROOT_MYSQL_PASSWORD" ]; then
        echo -e "${RED}   ✗ Failed to fetch credentials from SSM. Falling back to .env defaults.${NC}"
    else
        echo -e "${GREEN}   ✓ Credentials fetched and exported.${NC}"
        
        # Ensure Docker is up with these credentials
        echo -e "${YELLOW}🐳 Ensuring Docker containers are up...${NC}"
        # Move up to the root directory where docker-compose.yml is located
        (cd .. && docker compose up -d)
    fi
fi

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
