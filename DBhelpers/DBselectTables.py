import sqlite3
from datetime import datetime
import inspect
selectFolder = "SQLiteQueries/selectHandler/"

def print_caller():
    # Get the name of the caller (one level up the call stack)
    caller_name = inspect.stack()[1].function
    print("Called by function:", caller_name)

def getValueFromAnotherValue(sql_file_path, value1=None , dbName ='explicolivais.db'):
    retVal = None
    caller_function = inspect.stack()[1].function
    try:
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()

        # Connect to database
        conn = sqlite3.connect(dbName)

        if caller_function == "get_user_profile" or "getDataFrom" in caller_function  or 'getQuestionFromQid' == caller_function:
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        def ensure_sequence_params(param):
                # Normalize parameters:
                # - None => no parameters
                # - non-sequence scalar => single-element tuple
                # - list/tuple => pass through (flatten one level)
                if param is None:
                    return None
                if isinstance(param, (list, tuple)):
                    return tuple(param)
                return (param,)
        value1 = ensure_sequence_params(value1)
        # print("sql_file_path,value1,sql_code",sql_file_path,value1,'\n',sql_code)

        if value1 is not None:
            cursor.execute(sql_code,value1)
        else:
            cursor.execute(sql_code)


        if caller_function == "get_user_profile" or "getDataFrom" in caller_function:
            retVal = dict(cursor.fetchone())
        else:
            output = cursor.fetchall()
            if output:
                retVal = output[0][0]
            if 'getQuestionFromQid' == caller_function:
                retVal = output[0]
            if 'getQuestionIDsForYear' == caller_function:
                retVal = output




    except Exception as e:
        retVal = f"Error retrieving data: {e}"
        print(retVal)
    finally:
        conn.close()
    if 'getQuestionIDsForYear' == caller_function:
        return retVal


    if not isinstance(retVal,str) or "Error" not in retVal:
        # print("----------------------------------------------------",retVal)
        retVal = dictify_real_dict_row(retVal)
        # print("----------------------------------------------------",retVal)

    return retVal

def getUserIdFromEmail(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_user_from_email.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getHashFromEmail(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_hash_from_email.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getEmailFromUsername(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_email_from_username.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def get_user_quiz(email):
    return False

def get_user_profile(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_profile_from_email.sql", email)
    # print("---------------------------------",retVal)
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
    # print(row)

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


def getDataFromNIF(nif):
    retVal = getValueFromAnotherValue( selectFolder + "get_data_from_nif.sql", nif)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getDataFromEmail(email):
    retVal = getValueFromAnotherValue( selectFolder + "get_data_from_email.sql", email)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getDataFromCellNumber(cellNumber):
    retVal = getValueFromAnotherValue( selectFolder + "get_data_from_cellNumber.sql", cellNumber)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getDataFromIPcreated(ip_value):
    retVal = getValueFromAnotherValue( selectFolder + "get_data_from_ip_value.sql", ip_value)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def getQuestionIDsForYear(year):
    nQuestionYear = 15
    nQuestionPrev = 15
    nskip = 0
    if year == 5:
        nQuestionYear = 20
        nQuestionPrev = 0
        nskip = 0
    arguments = [year,nQuestionYear,nskip,year,nQuestionPrev]

    retVal = getValueFromAnotherValue( selectFolder + "get_questionIDs_from_year.sql", value1=arguments,dbName='quiz.db')
    if isinstance(retVal,str) and "Error" in retVal:
        # print("------------------- getQuestionIDsForYear",retVal,arguments)
        return None
    return retVal


def getQuestionFromQid(qid):
    retVal = getValueFromAnotherValue( selectFolder + "get_question_from_rowID.sql", value1=qid,dbName='quiz.db')
    if isinstance(retVal,str) and "Error" in retVal:
        # print("getQuestionFromQid",retVal,qid)
        return None
    return retVal

