from .DBbaseline import get_mysql_connection

deleteFolder = "SQLiteQueries/deleteHandler/"


def execute_delete_from_file(sql_file_path, params=None):
    """
    Executes a parameterized DELETE query from an SQL file.
    """
    try:
        with open(sql_file_path, "r") as file:
            sql_code = file.read()

        conn = get_mysql_connection()
        if not conn:
            raise ConnectionError("Could not connect to MySQL database")

        cursor = conn.cursor()
        cursor.execute(sql_code, params)
        conn.commit()

        status = "Delete successful"
    except Exception as e:
        status = f"Error deleting data: {e}"
    finally:
        if "conn" in locals() and conn:
            conn.close()

    return status


def deleteRegistrationToken(token):
    """
    Deletes a registration token from the 'registration_tokens' table.
    """
    deleteFile = "delete_registration_token.sql"
    status = execute_delete_from_file(deleteFolder + deleteFile, (token,))
    return status


def deleteExpiredRegistrationTokens():
    """
    Deletes all expired registration tokens from the 'registration_tokens' table.
    """
    deleteFile = "delete_expired_registration_tokens.sql"
    status = execute_delete_from_file(deleteFolder + deleteFile)
    return status
