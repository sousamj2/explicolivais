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
    
    # Debug middleware to see what Apache is sending
    @app.before_request
    def log_request_info():
        from flask import request
        # Only log for authentication routes to keep logs clean
        if 'signin' in request.path or 'oauth2' in request.path:
            print(f"\n[DEBUG] --- EXPLICOLIVAIS Request: {request.path} ---", flush=True)
            print(f"[DEBUG] Host Header: {request.headers.get('Host')}", flush=True)
            print(f"[DEBUG] X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto')}", flush=True)
            print(f"[DEBUG] X-Forwarded-Host: {request.headers.get('X-Forwarded-Host')}", flush=True)
            print(f"[DEBUG] Flask thinks URL is: {request.url}", flush=True)

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
