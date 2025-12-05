from flask import current_app
from config import DevelopmentConfig
import pymysql

def get_mysql_connection(use_dict_cursor: bool = False):
    """
    This function creates the connection to MySQL in AWS.
    """
    # Load from env vars or AWS Secrets/Parameter Store
    MYSQL_HOST = current_app.config['MYSQL_HOST']
    # MYSQL_HOST = "localhost"
    MYSQL_NAME = current_app.config['MYSQL_DBNAME']
    MYSQL_USER = current_app.config['MYSQL_USER']
    MYSQL_PASS = current_app.config['MYSQL_PASSWORD']
    MYSQL_PORT = int(current_app.config['MYSQL_PORT'])
    # MYSQL_PORT = 3307

    cursor_cls = pymysql.cursors.DictCursor if use_dict_cursor else pymysql.cursors.Cursor

    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            db=MYSQL_NAME,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            charset="utf8mb4",
            cursorclass=cursor_cls,
            use_unicode=True,
            )
        return conn
    except Exception as e:
        print(f"Error connecting: {e}")
        return None


def setup_mysql_database():
    """
    This function is used to setup the database at the beginning creating the database and the tables if they don't exist.
    """
    # # Load from env vars or AWS Secrets/Parameter Store
    # MYSQL_HOST = current_app.config['MYSQL_HOST']
    # MYSQL_NAME = current_app.config['MYSQL_DBNAME']
    # MYSQL_USER = current_app.config['MYSQL_USER']
    # MYSQL_PASS = current_app.config['MYSQL_PASSWORD']
    # MYSQL_PORT = int(current_app.config['MYSQL_PORT'])


    MYSQL_HOST = DevelopmentConfig.MYSQL_HOST
    # MYSQL_HOST = "localhost"
    MYSQL_NAME = DevelopmentConfig.MYSQL_DBNAME
    MYSQL_USER = DevelopmentConfig.MYSQL_USER
    MYSQL_PASS = DevelopmentConfig.MYSQL_PASSWORD
    MYSQL_PORT = DevelopmentConfig.MYSQL_PORT
    # MYSQL_PORT = 3307
    
    # print()
    # print(MYSQL_HOST)
    # print(MYSQL_NAME)
    # print(MYSQL_USER)
    # print(MYSQL_PASS)
    # print(MYSQL_PORT)
    # print()


    # Connect to MySQL server (without specifying database)
    conn = pymysql.connect (
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        port=MYSQL_PORT,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
        autocommit=True,
        use_unicode=True,
    )
    cursor = conn.cursor()
        
    from DBhelpers import (
        newTableResults,
        newTableClass,
        newTableConnectionData,
        newTableDocuments,
        newTableIPs,
        newTablePersonalData,
        newTableUsers
    )

    try:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_NAME}")
        print(f"Database '{MYSQL_NAME}' created or already exists")
        
        # Switch to the database
        cursor.execute(f"USE {MYSQL_NAME}")
        print(f"Using database '{MYSQL_NAME}'")
        
        newTableUsers(cursor)
        print("Table users created correctly")
        newTableConnectionData(cursor)
        print("Table connections created correctly")
        newTablePersonalData(cursor)
        print("Table personal created correctly")
        newTableIPs(cursor)
        print("Table ips created correctly")
        newTableResults(cursor)
        print("Table results created correctly")

        newTableClass(cursor)
        print("Table class created correctly")
        newTableDocuments(cursor)
        print("Table documents created correctly")
        
        # Commit the changes
        print("Database setup completed successfully!")
                
    except Exception as err:
        print(f"Error: {err}")
    
    finally:
        cursor.close()
        conn.close()
