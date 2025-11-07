import sqlite3
insertFolder = "SQLiteQueries/insertHandler/"

def handle_tables(sql_file_path,dbname='explicolivais.db'):
    """
    Executes a CREATE TABLE SQL command from a file.
    """
    conn = sqlite3.connect(dbname)  # Adjust your DB path
    try:
        # Read SQL code from file
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()

        # Connect to database
        cursor = conn.cursor()

        # Execute the SQL command
        cursor.executescript(sql_code)  # Using executescript to handle multiple statements if exist
        conn.commit()

        status = "Table created successfully"
    except Exception as e:
        status = f"Error creating table: {e} from {sql_file_path}"
        print(status)
    finally:
        conn.close()

    return status

def newTableClass():
    handle_tables(insertFolder + "create_classes.sql")

def newTableIPs():
    handle_tables(insertFolder + "create_iplist.sql")

def newTableDocuments():
    handle_tables(insertFolder + "create_documents.sql")

def newTableConnectionData():
    handle_tables(insertFolder + "create_connections.sql")

def newTablePersonalData():
    handle_tables(insertFolder + "create_personal.sql")

def newTableUsers():
    handle_tables(insertFolder + "create_users.sql")

def createAllTables():
    handle_tables(insertFolder + "create_all_tables.sql")

def deleteAllTable():
    handle_tables(insertFolder + "delete_all_tables.sql")
