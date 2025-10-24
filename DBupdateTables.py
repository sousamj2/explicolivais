import sqlite3
from datetime import datetime
from DBbaseline import getUserIdFromEmail

selectFolder = "SQLiteQueries/updateHandler/"



def refresh_last_login_and_ip(email, current_ip):
    try:
        # Read SQL code from file
        with open(selectFolder + "update_last_login_and_ip.sql", 'r') as file:
            sql_code = file.read()

        # Connect to database
        conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
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