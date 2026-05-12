from waitress import serve
from explicolivais import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mysql')))
from DBhelpers import DBbaseline
import DBloadQuiz

import os
import logging

# Configurar logging
logging.getLogger('waitress.queue').setLevel(logging.ERROR)


if __name__ == '__main__':
    DBbaseline.setup_mysql_database(app_name="explicolivais");
    DBloadQuiz.loadQanswers();
    DBloadQuiz.loadQlinks();
    DBloadQuiz.loadQtemas();
    DBloadQuiz.loadQaulas();
    
    # For production use waitress to serve the app
    print("🚀 Starting Explicolivais Waitress Server on port 8080...", flush=True)
    serve(
        app, 
        host='*', 
        port=8080, 
        threads=8, 
        channel_timeout=120, 
        connection_limit=100, 
        backlog=2048,
        trusted_proxy='*', # Trust headers from all proxies
        trusted_proxy_headers=['x-forwarded-for', 'x-forwarded-proto', 'x-forwarded-host', 'x-forwarded-port']
    )
