from waitress import serve
# from application import app
from explicolivais import app
import sys
import os
sys.path.insert(0,os.getcwd()+"/DBhelpers")

import DBcreateTables
import DBloadQuiz

import os
import logging

# Configurar logging
logging.getLogger('waitress.queue').setLevel(logging.ERROR)


if __name__ == '__main__':
    # check_and_create_tables()
    createHandlerPath=os.getcwd()+'/SQLiteQueries/createHandler/'
    DBcreateTables.handle_tables(createHandlerPath + 'create_users.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_connections.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_classes.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_documents.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_personal.sql')
    DBcreateTables.handle_tables(createHandlerPath + 'create_iplist.sql')

    DBloadQuiz.loadQanswers();
    DBloadQuiz.loadQlinks();
    DBloadQuiz.loadQtemas();
    DBloadQuiz.loadQaulas();
    
    # For production use waitress to serve the app

    # Localhost access only
    # serve(app, host="localhost", port=8080, threads=8, channel_timeout=120,connection_limit=100,backlog=2048 )
    serve(app, host='0.0.0.0', port=8080, threads=8, channel_timeout=120,connection_limit=100,backlog=2048 )
