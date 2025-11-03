#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "   🚀 Creating tables if they don't exit"

python -c "import os;\
import sys;\
sys.path.insert(0, os.getcwd() + '/DBhelpers');\
import DBcreateTables;\
import DBloadQuiz;\
createHandlerPath=os.getcwd()+'/SQLiteQueries/createHandler/';\
DBcreateTables.handle_tables(createHandlerPath + 'create_users.sql');\
DBcreateTables.handle_tables(createHandlerPath + 'create_connections.sql');\
DBcreateTables.handle_tables(createHandlerPath + 'create_classes.sql');\
DBcreateTables.handle_tables(createHandlerPath + 'create_documents.sql');\
DBcreateTables.handle_tables(createHandlerPath + 'create_personal.sql');\
DBcreateTables.handle_tables(createHandlerPath + 'create_iplist.sql');\
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

# Get public IP for easy access
# PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")

echo -e "${YELLOW}📍 Access URLs:${NC}"
echo -e "   Direct: http://$PUBLIC_IP:8080"
echo -e "   Domain: https://www.explicolivais.com"
echo -e "   Local:  http://localhost:8080"
echo ""
echo -e "${YELLOW}💡 Features enabled:${NC}"
echo -e "   ✅ Auto-reload on file changes"
echo -e "   ✅ Interactive debugger"
echo -e "   ✅ Detailed error pages"
echo ""
echo -e "${RED}Press Ctrl+C to stop${NC}"
echo ""

# Start Flask
# flask run --host=0.0.0.0 --port=8080
flask run --host=localhost --port=8080
