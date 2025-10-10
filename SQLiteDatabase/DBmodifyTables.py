import sqlite3
from DBbaseline import * 

def updateValue(email, tableName, tableColumn, newValue=None):
    conn,c = dbConnect()
    user_id = getUserIdFromEmail(email)
    status = f"Correctly updated the new value {newValue} into table {tableName} and field {tableColumn} for email {email}."

    # Validate or whitelist tableName and tableColumn to avoid SQL injection.
    allowed_tables = {"personal", "classes", "iplist", "documents", "connection"}  # Example allowed
    allowed_columns = {
        "personal"  : {"morada", "numero", "andar", "porta", "cpostal1", "cpostal2", "telemovel"},
        "classes"   : {"year", "childName", "disciplina", "firstClass", "firstContact"},
        "iplist"    : {"ipValid"},
        "documents" : {"visible"},
        "connection": {"thisloginip","vpn_check","vpn_valid"},
    }

    if tableName not in allowed_tables:
        raise ValueError("Table name not allowed")

    if tableColumn not in allowed_columns.get(tableName, set()):
        raise ValueError("Column name not allowed")

    try:
        if "thisloginip" == tableColumn:
            sql = "UPDATE connection SET lastlogindt = thislogindt       WHERE user_id = ?;"
            c.execute(sql, (user_id,))
            sql = "UPDATE connection SET lastloginip = thisloginip       WHERE user_id = ?;"
            c.execute(sql, (user_id,))
            sql = "UPDATE connection SET thislogindt = CURRENT_TIMESTAMP WHERE user_id = ?;"
            c.execute(sql, (user_id,))
            sql = "UPDATE connection SET thisloginip = ?                 WHERE user_id = ?;"
            c.execute(sql, (newValue,user_id))
            sql = "UPDATE connection SET logincount = logincount + 1     WHERE user_id = ?;"
            c.execute(sql, (user_id,))
            sql = """
            INSERT INTO iplist (user_id, ipValue)
            VALUES (?, ?)
            ON CONFLICT(user_id, ipValue) DO UPDATE SET
                logincount = logincount + 1;
            """
            c.execute(sql, (user_id, newValue))
        else:
            sql = "UPDATE {tableName} SET {tableColumn} = ? WHERE user_id = ?;"
            c.execute(sql, (newValue, user_id))
        conn.commit()
    except Exception as e:
        status = f"Error updating table {tableName} field {tableColumn} with {newValue}: {e}."
    finally:
        conn.close()
    return status
    