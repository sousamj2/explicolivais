from waitress import serve
from application import app
from connectDB import check_and_create_tables

if __name__ == '__main__':
    check_and_create_tables()
    # For production use waitress to serve the app

    # Localhost access only
    serve(app, host='localhost', port=8080)
    # serve(app, host='0.0.0.0', port=8080)
