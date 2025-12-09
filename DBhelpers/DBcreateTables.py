createFolder = "SQLiteQueries/createHandlerMySQL/"

def create_tables(sql_file_path,cursor):
    """
    Executes a CREATE TABLE SQL script from a file.

    This function reads an SQL file containing a `CREATE TABLE` statement and
    executes it using the provided database cursor. It is a generic utility
    used by other functions to create specific tables.

    Args:
        sql_file_path (str): The path to the .sql file containing the CREATE TABLE command.
        cursor (pymysql.cursors.Cursor): The database cursor to use for executing the command.

    Returns:
        str: A status message indicating whether the table was created successfully
             or if an error occurred.
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
    """
    Creates the 'classes' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `classes` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_classes.sql",cursor=cursor)

def newTableIPs(cursor):
    """
    Creates the 'iplist' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `iplist` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_iplist.sql",cursor=cursor)

def newTableResults(cursor):
    """
    Creates the 'qresults' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `qresults` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_qresults.sql",cursor=cursor)

def newTableDocuments(cursor):
    """
    Creates the 'documents' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `documents` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_documents.sql",cursor=cursor)

def newTableConnectionData(cursor):
    """
    Creates the 'connections' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `connections` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_connections.sql",cursor=cursor)

def newTablePersonalData(cursor):
    """
    Creates the 'personal' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `personal` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_personal.sql",cursor=cursor)

def newTableUsers(cursor):
    """
    Creates the 'users' table in the database.

    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `users` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_users.sql",cursor=cursor)

def newTableBlacklistedEmails(cursor):
    """
    Creates the 'blacklisted_emails' table in the database.
    
    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `blacklisted_emails` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_blacklisted_emails.sql",cursor=cursor)

def newTableBlacklistedIPs(cursor):
    """
    Creates the 'blacklisted_ips' table in the database.
    
    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `blacklisted_ips` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_blacklisted_ips.sql",cursor=cursor)

def newTableRegistrationTokens(cursor):
    """
    Creates the 'registration_tokens' table in the database.
    
    This function calls the generic `create_tables` utility to execute the
    SQL script for creating the `registration_tokens` table.

    Args:
        cursor (pymysql.cursors.Cursor): The database cursor to use.
    """
    create_tables(sql_file_path=createFolder + "create_registration_tokens.sql",cursor=cursor)
