import sqlite3

def getAllUsers():
    # Connect to database
    conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
    cursor = conn.cursor()

    sqlCode = """
    SELECT * FROM users;
    """
    cursor.execute(sqlCode)
    output = cursor.fetchall()
    conn.close()
    return output

def getUserIdFromEmail(email):
    # Connect to database
    conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
    cursor = conn.cursor()
    sqlCode = """
    SELECT user_id FROM users WHERE email = ?;
    """
    cursor.execute(sqlCode,(email,))
    output = cursor.fetchall()
    conn.close()
    if output:
        return output[0][0]
    else:
        return None
