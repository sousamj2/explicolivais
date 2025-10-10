import sqlite3

def dbConnect():
    # Create the connection
    conn = sqlite3.connect("olivaisplica.db")
    # Create cursor instance
    cursor = conn.cursor()
    return conn, cursor

def getAllUsers():
    conn,c = dbConnect()
    sqlCode = """
    SELECT * FROM users;
    """
    c.execute(sqlCode)
    output = c.fetchall()
    conn.close()
    return output

def getUserIdFromEmail(email):
    conn,c = dbConnect()
    sqlCode = """
    SELECT user_id FROM users WHERE email = ?;
    """
    c.execute(sqlCode,(email,))
    output = c.fetchall()
    conn.close()
    if output:
        return output[0][0]
    else:
        return None

# # documents    JSONB NOT NULL DEFAULT '{"files": [], "knowip": [], "blockip": {}, "preferences": {}}',
