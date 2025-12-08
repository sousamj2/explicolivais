from flask import current_app
from config import DevelopmentConfig
import pymysql

def get_mysql_connection(use_dict_cursor: bool = False):
    """
    Establishes and returns a connection to the MySQL database.

    This function retrieves database connection parameters (host, database name, user,
    password, port) from the current Flask application's configuration. It then
    uses these parameters to create and return a `pymysql` connection object.

    Args:
        use_dict_cursor (bool, optional): If True, the connection's cursor will
            return rows as dictionaries instead of the default tuples.
            Defaults to False.

    Returns:
        pymysql.Connection | None: A `pymysql` connection object on success, or
        `None` if the connection fails.
    """
    # Load from env vars or AWS Secrets/Parameter Store
    MYSQL_HOST = current_app.config['MYSQL_HOST']
    MYSQL_NAME = current_app.config['MYSQL_DBNAME']
    MYSQL_USER = current_app.config['MYSQL_USER']
    MYSQL_PASS = current_app.config['MYSQL_PASSWORD']
    MYSQL_PORT = int(current_app.config['MYSQL_PORT'])

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
    Initializes the application's database schema.

    This setup utility connects to the MySQL server and performs the initial
    database and table creation. It is intended to be run once to bootstrap the
    database environment or for resetting it during development.

    The function performs the following actions:
    1.  Connects to the MySQL server using credentials from the development config.
    2.  Executes a `CREATE DATABASE IF NOT EXISTS` statement to ensure the main
        application database exists.
    3.  Switches to the newly created or existing database.
    4.  Calls a series of helper functions (`newTableUsers`, `newTableConnectionData`,
        etc.) to create each of the application's tables.
    5.  Prints progress and error messages to the console.
    """
    # # Load from env vars or AWS Secrets/Parameter Store
    # MYSQL_HOST = current_app.config['MYSQL_HOST']
    # MYSQL_NAME = current_app.config['MYSQL_DBNAME']
    # MYSQL_USER = current_app.config['MYSQL_USER']
    # MYSQL_PASS = current_app.config['MYSQL_PASSWORD']
    # MYSQL_PORT = int(current_app.config['MYSQL_PORT'])


    MYSQL_HOST = DevelopmentConfig.MYSQL_HOST
    MYSQL_NAME = DevelopmentConfig.MYSQL_DBNAME
    MYSQL_USER = DevelopmentConfig.MYSQL_USER
    MYSQL_PASS = DevelopmentConfig.MYSQL_PASSWORD
    MYSQL_PORT = DevelopmentConfig.MYSQL_PORT
    
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
