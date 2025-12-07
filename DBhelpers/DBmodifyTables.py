"""
This module contains functions for modifying data in the database tables.

NOTE: The functions `getQuestionIDsForYear` and `getQuestionFromQid` appear
to be misplaced in this file. They are related to selecting quiz data and
use a function `getValueFromAnotherValue` which is not defined here, suggesting
they belong in a different module like `DBselectTables.py`.
"""
# import sqlite3
from DBselectTables import getUserIdFromEmail
from .DBbaseline import get_mysql_connection


def updateValue(email, tableName, tableColumn, newValue=None):
    """
    Updates a specific field in the database for a given user.

    This function provides a controlled way to update a single value in the
    database. It includes a security measure, using a whitelist of allowed
    table and column names to prevent SQL injection vulnerabilities.

    It has special logic for handling updates to the 'thisloginip' column in the
    'connection' table, which also updates login timestamps and history in
    both the 'connection' and 'iplist' tables.

    Args:
        email (str): The email of the user whose data is to be updated.
        tableName (str): The name of the table to update.
        tableColumn (str): The name of the column to update.
        newValue (any, optional): The new value to be set. Defaults to None.

    Returns:
        str: A status message indicating the success or failure of the update.

    Raises:
        ValueError: If the `tableName` or `tableColumn` is not in the allowed list.
        ConnectionError: If the database connection fails.
    """
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
    """
    Retrieves a list of question IDs for a given academic year for a quiz.

    This function determines the number of questions to fetch from the specified
    year and from previous years. It has a special case for year 5, where all
    questions are from that year. It relies on an external function,
    `getValueFromAnotherValue`, to execute the database query.

    Args:
        year (int): The academic year for which to retrieve question IDs.

    Returns:
        list | None: A list of question IDs, or None if an error occurs.
    """
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
    """
    Retrieves a full quiz question from the database by its row ID.

    This function fetches all data for a single quiz question using its unique
    identifier (`qid`). It relies on an external function, `getValueFromAnotherValue`,
    to perform the database lookup.

    Args:
        qid (int): The unique row ID of the question to retrieve.

    Returns:
        dict | None: A dictionary containing the question's data, or None if the
                     question is not found or an error occurs.
    """
    retVal = getValueFromAnotherValue( selectFolder + "get_question_from_rowID.sql", value1=qid,dbName='quiz.db')
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal