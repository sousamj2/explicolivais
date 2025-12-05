createFolder = "SQLiteQueries/createHandlerMySQL/"

def create_tables(sql_file_path,cursor):
    """
    Executes a CREATE TABLE SQL command from a file.
    """

    try:
        # Read SQL code from file
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()

        # Execute the SQL command
        cursor.execute(sql_code)  # Using executescript to handle multiple statements if exist
        # conn.commit()

        status = "Table created successfully"
    except Exception as e:
        status = f"Error creating table: {e} from {sql_file_path}"
        print(status)

    return status

def newTableClass(cursor):
    create_tables(sql_file_path=createFolder + "create_classes.sql",cursor=cursor)

def newTableIPs(cursor):
    create_tables(sql_file_path=createFolder + "create_iplist.sql",cursor=cursor)

def newTableResults(cursor):
    create_tables(sql_file_path=createFolder + "create_qresults.sql",cursor=cursor)

def newTableDocuments(cursor):
    create_tables(sql_file_path=createFolder + "create_documents.sql",cursor=cursor)

def newTableConnectionData(cursor):
    create_tables(sql_file_path=createFolder + "create_connections.sql",cursor=cursor)

def newTablePersonalData(cursor):
    create_tables(sql_file_path=createFolder + "create_personal.sql",cursor=cursor)

def newTableUsers(cursor):
    create_tables(sql_file_path=createFolder + "create_users.sql",cursor=cursor)
