from waitress import serve
from application import app

# serve(app, host='0.0.0.0', port=8080)
serve(app, host='localhost', port=8080)
