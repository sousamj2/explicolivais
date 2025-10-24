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

