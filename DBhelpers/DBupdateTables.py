# import sqlite3
from datetime import datetime
from DBhelpers.DBselectTables import getUserIdFromEmail
from DBhelpers.DBbaseline import get_mysql_connection
selectFolder = "SQLiteQueries/updateHandler/"

def refresh_last_login_and_ip(email, current_ip):
    conn = get_mysql_connection()
    if not conn:
        raise ConnectionError("Could not connect to MySQL database")

    try:
        # Read SQL code from file
        with open(selectFolder + "update_last_login_and_ip.sql", 'r') as file:
            sql_code = file.read()
            sql_code = sql_code.replace("?","%s")

        cursor = conn.cursor()
        now = datetime.now()

        user_id = getUserIdFromEmail(email)

        cursor.execute(sql_code, (now, current_ip, user_id,))
        conn.commit()

        status = "Time stamps and IP updated."
    except Exception as e:
        status = f"Error updating data: {e}"
    finally:
        conn.close()

    print(status)