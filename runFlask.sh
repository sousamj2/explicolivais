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

export APP_ENV=local

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
export APP_ENV=local

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
