# import sqlite3
from DBselectTables import getUserIdFromEmail
from .DBbaseline import get_mysql_connection


def updateValue(email, tableName, tableColumn, newValue=None):
    # Connect to database
    
    # Choose backend
    conn = get_mysql_connection()
    if not conn:
        raise ConnectionError("Could not connect to MySQL database")

    cursor = conn.cursor()

    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    
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
            sql = "UPDATE connection SET lastlogindt = thislogindt       WHERE user_id = %s;"
            cursor.execute(sql, (user_id,))
            sql = "UPDATE connection SET lastloginip = thisloginip       WHERE user_id = %s;"
            cursor.execute(sql, (user_id,))
            sql = "UPDATE connection SET thislogindt = CURRENT_TIMESTAMP WHERE user_id = %s;"
            cursor.execute(sql, (user_id,))
            sql = "UPDATE connection SET thisloginip = %s                WHERE user_id = %s;"
            cursor.execute(sql, (newValue,user_id))
            sql = "UPDATE connection SET logincount = logincount + 1     WHERE user_id = %s;"
            cursor.execute(sql, (user_id,))
            sql = """
            INSERT INTO iplist (user_id, ipValue)
            VALUES (%s, %s)
            ON CONFLICT(user_id, ipValue) DO UPDATE SET
                logincount = logincount + 1;
            """
            
            cursor.execute(sql, (user_id, newValue))
        else:
            sql = "UPDATE {tableName} SET {tableColumn} = %s WHERE user_id = %s;"
            cursor.execute(sql, (newValue, user_id))
        conn.commit()
    except Exception as e:
        status = f"Error updating table {tableName} field {tableColumn} with {newValue}: {e}."
    finally:
        conn.close()
    return status
    


def getQuestionIDsForYear(year):
    nQuestionYear = 15
    nQuestionPrev = 15
    if year == 5:
        nQuestionYear = 30
        nQuestionPrev = 0
    arguments = [year,nQuestionYear,year,nQuestionPrev]

    retVal = getValueFromAnotherValue( selectFolder + "get_questionIDs_from_year.sql", value1=arguments,dbName='quiz.db')
    if isinstance(retVal,str) and "Error" in retVal:
        print(retVal,arguments)
        return None
    return retVal


def getQuestionFromQid(qid):
    retVal = getValueFromAnotherValue( selectFolder + "get_question_from_rowID.sql", value1=qid,dbName='quiz.db')
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

