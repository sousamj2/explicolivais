import sqlite3
from datetime import datetime
import inspect
selectFolder = "SQLiteQueries/selectHandler/"

def print_caller():
    # Get the name of the caller (one level up the call stack)
    caller_name = inspect.stack()[1].function
    print("Called by function:", caller_name)

def getValueFromAnotherValue(sql_file_path, value1=None ):
    retVal = None
    caller_function = inspect.stack()[1].function
    try:
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()

        # Connect to database
        conn = sqlite3.connect('explicolivais.db')

        if caller_function == "get_user_profile":
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        if value1 is not None:
            cursor.execute(sql_code,(value1,))
        else:
            cursor.execute(sql_code)


        if caller_function == "get_user_profile":
            retVal = dict(cursor.fetchone())
        else:
            output = cursor.fetchall()
            if output:
                retVal = output[0][0]

    except Exception as e:
        retVal = f"Error retrieving data: {e}"
        print(retVal)
    finally:
        conn.close()

    if not isinstance(retVal,str) or "Error" not in retVal:
        # print("----------------------------------------------------",retVal)
        retVal = dictify_real_dict_row(retVal)

    return retVal

def getUserIdFromEmail(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_user_from_email.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getDataFromNIF(nif):
    return getValueFromAnotherValue( selectFolder + "get_data_from_nif.sql", nif)

def getDataFromCellNumber(cellNumber):
    return getValueFromAnotherValue( selectFolder + "cet_data_from_cellNumber.sql", cellNumber)

def get_user_profile(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_profile_from_email.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal


def dictify_real_dict_row(row):
    def convert_value(val):
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, list):
            return [convert_value(i) for i in val]
        if isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val
    if not isinstance(row, (dict, list, datetime)):
        return row
    print(row)

    return {k: convert_value(v) for k, v in row.items()}



def submit_query(query, params=None):
    result = None
    try:
        # Connect to database
        conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
        # cursor = conn.cursor()

        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description : # Check if there are results to fetch
                result = cursor.fetchall()
                # Detect if result is a 1-column result and convert to simple list
                if len(cursor.description) == 1:
                    # Flatten 1-column records into list
                    # result = [row[0] for row in result]
                    result = [list(row.values())[0] for row in result]
                    # pprint(result)

                elif len(result) == 1:
                    # Potentially flatten 1-row multiple columns into dict or list 
                    # (You can customize based on preference, here we keep as dict)
                    # pprint(result)
                    result = result[0]
            else:
                result = {'rowcount': cursor.rowcount}
            conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        return f"Error executing query: {e}"
    finally:
        conn.close()


