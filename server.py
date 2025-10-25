from waitress import serve
# from application import app
from explicolivais import app
from DBhelpers import DBcreateTables
import os

if __name__ == '__main__':
    # check_and_create_tables()
    createHandlerPath=os.getcwd()+'/SQLiteQueries/createHandler/'
    DBcreateTables.handle_tables(createHandlerPath + 'create_users.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_connections.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_classes.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_documents.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_personal.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_iplist.sql')
    
    # For production use waitress to serve the app

    # Localhost access only
    serve(app, host="localhost", port=8080)
    # serve(app, host='0.0.0.0', port=8080)
