import sqlite3
from datetime import datetime
import inspect
from .DBbaseline import get_mysql_connection
import pymysql
selectFolder = "SQLiteQueries/selectHandler/"

def print_caller():
    """
    Prints the name of the calling function.

    This is a simple debugging utility that inspects the call stack to
    determine which function called the current function and prints its
    name to the console.
    """
    # Get the name of the caller (one level up the call stack)
    caller_name = inspect.stack()[1].function
    # print("Called by function:", caller_name)

def getValueFromAnotherValue(sql_file_path, value1=None , dbName ='explicolivais.db'):
    """
    A highly versatile function for executing SQL SELECT queries from predefined .sql files.

    This function dynamically connects to either a MySQL database (using `pymysql`)
    or a SQLite database (using `sqlite3`), determined by the `dbName` parameter.
    It reads an SQL query from the specified `sql_file_path`, substitutes parameters,
    and executes the query.

    Key features include:
    -   **Dynamic Database Backend**: Connects to MySQL if `dbName` is 'explicolivais.db',
        otherwise to SQLite.
    -   **Flexible Parameter Handling**: Accepts a single value, a list, or a tuple for `value1`,
        which is then formatted correctly for `pymysql` (using '%s') or `sqlite3` (using '?').
    -   **Intelligent Result Formatting**:
        -   If the calling function's name suggests it's fetching a user profile (e.g.,
            'get_user_profile', 'getDataFrom'), it attempts to return the result as a dictionary
            (using `DictCursor` for MySQL or `row_factory` for SQLite).
        -   For other queries, it typically returns the first column of the first row fetched.
        -   Special handling for `get_quiz_history_for_user` (returns a list of dicts).
        -   Special handling for `getQuestionFromQid` (returns the full row) and
            `getQuestionIDsForYear` (returns the full list of fetched rows).
    -   **Error Handling**: Catches exceptions during execution and returns an error message string.

    Args:
        sql_file_path (str): The path to the .sql file containing the SELECT query.
        value1 (any, optional): The parameter(s) to be passed to the SQL query. Can be
                                a scalar, list, or tuple. Defaults to None.
        dbName (str, optional): The name of the database to connect to. 'explicolivais.db'
                                implies MySQL; otherwise, SQLite. Defaults to 'explicolivais.db'.

    Returns:
        dict | list | any | str: The fetched data (dictionary for profiles, list for
        multiple rows/IDs, scalar for single values), or a string containing an error message.
    """
    retVal = None
    caller_function = inspect.stack()[1].function

    # Choose backend
    use_mysql = (dbName == 'explicolivais.db')
    want_dict = use_mysql and ("get_user_profile" in caller_function or "getDataFrom" in caller_function or "get_quiz_history_for_user" in caller_function)
    
    if use_mysql:
        conn = get_mysql_connection(use_dict_cursor=want_dict)
        if not conn:
            raise ConnectionError("Could not connect to MySQL database")
    else:
        conn = sqlite3.connect(dbName)

    try:
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()
            if use_mysql:
                sql_code = sql_code.replace("?","%s")

        if not use_mysql and 'getQuestionFromQid' == caller_function:
            # SQLite: keep row_factory
            conn.row_factory = sqlite3.Row
        
        # Default tuple cursor for all
        cursor = conn.cursor()

        # if "get_user_profile" in caller_function or "getDataFrom" in caller_function  or 'getQuestionFromQid' == caller_function:
        #     conn.row_factory = sqlite3.Row
        # cursor = conn.cursor()

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
            # print(sql_code,value1)
        else:
            cursor.execute(sql_code)


        if "get_user_profile" in caller_function or "getDataFrom" in caller_function:
            output = cursor.fetchone()
            if output:
                retVal = dict(output)
                # print("dict output:",retVal)

        elif 'get_quiz_history_by_uuid' == caller_function or "get_quiz_history_for_user" in caller_function:
            retVal = cursor.fetchall()
        else:
            output = cursor.fetchall()
            # print("else output:",output)
            if output:
                retVal = output[0][0]
            if 'getQuestionFromQid' == caller_function:
                retVal = output[0]
            if 'getQuestionIDsForYear' == caller_function:
                retVal = output




    except Exception as e:
        retVal = f"Error retrieving data: {e}"
        # print(retVal)
    finally:
        conn.close()
    if 'getQuestionIDsForYear' == caller_function:
        return retVal


    if "get_quiz_history_for_user" in caller_function :
        return [dictify_real_dict_row(row) for row in retVal] if retVal else []
    
    if not isinstance(retVal,str) or "Error" not in retVal:
        # print("----------------------------------------------------",retVal)
        retVal = dictify_real_dict_row(retVal)
        # print("----------------------------------------------------",retVal)
    # print("retVal after dictify:",retVal)

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

def get_quiz_history_for_user(email):
    """Fetches all quiz history for a given user."""
    # The SQL query in get_quiz_history_from_email.sql has been updated
    # to calculate total_questions and score_perc directly.
    # - total_questions is the sum of correct, wrong, and skipped.
    # - score_perc is calculated from q_score and max_possible_points.
    #   (Assuming max_possible_points is n_correct * 5, which is a simplification
    #    but works if all correct answers are worth 5 points).
    # If scoring is more complex, this logic might need adjustment.
    retVal = getValueFromAnotherValue(selectFolder + "get_quiz_history_from_email.sql", email)
    if isinstance(retVal, str) and "Error" in retVal:
        return []
    return retVal


def get_quiz_history_by_uuid(email, quiz_uuid):
    """
    Args:
        email (str): The user's email address.
        quiz_uuid (str): The unique identifier for the quiz.

    """
    retVal = get_quiz_history_for_user(email)
    # print("get_quiz_history_by_uuid",retVal)
    if isinstance(retVal, str) and "Error" in retVal:
        return []
    for quiz in retVal:
        if 'q_uuid' in quiz.keys() and quiz.get('q_uuid') == quiz_uuid:
            return quiz
    return []
    

def get_user_profile_tier2(email):
    # print("---------------------------------",email)
    retVal = getValueFromAnotherValue( selectFolder + "get_T2profile_from_email.sql", email)
    # print("---------------------------------",retVal)
    if isinstance(retVal,str) and "Error" in retVal:
        return None
    return retVal

def get_user_profile_tier1(email):
    # print("---------------------------------",email)
    retVal = getValueFromAnotherValue( selectFolder + "get_T1profile_from_email.sql", email)
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
    conn = get_mysql_connection()
    if not conn:
        raise ConnectionError("Could not connect to MySQL database")

    try:
        # Connect to database
        # conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
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

def getQuestionIDsForYear(year,num_exercises=20,current_year_percent=50):
    debug=False
    # debug=True
    nQuestionYear = int(num_exercises*current_year_percent/100)
    nQuestionPrev = int(num_exercises*(1.-current_year_percent/100))
    sqlfile= "get_questionIDs_from_year_prod.sql"
    nskip = 0
    if year == 5: 
        nQuestionYear = num_exercises
        nQuestionPrev = 0
    if debug:
        sqlfile= "get_questionIDs_from_year_devel.sql"
        # year=6
        nQuestionYear = 2000
        nQuestionPrev = 0
        nskip = 0

    arguments = [year,nQuestionYear,nskip,year,nQuestionPrev]

    retVal = getValueFromAnotherValue( selectFolder + sqlfile, value1=arguments,dbName='quiz.db')
    # print(retVal)
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


def isEmailBlacklisted(email):
    """
    Checks if an email is in the 'blacklisted_emails' table.

    Args:
        email (str): The email to check.

    Returns:
        bool: True if the email is blacklisted, False otherwise.
    """
    retVal = getValueFromAnotherValue(selectFolder + "get_email_from_blacklisted_emails.sql", email)
    return retVal is not None and not (isinstance(retVal, str) and "Error" in retVal)


def getRegistrationToken(token):
    """
    Retrieves a registration token from the 'registration_tokens' table.

    Args:
        token (str): The token to retrieve.

    Returns:
        dict: A dictionary containing the token data, or None if not found.
    """
    retVal = getValueFromAnotherValue(selectFolder + "get_registration_token.sql", token)
    if isinstance(retVal, str) and "Error" in retVal:
        return None
    return retVal


def getRegistrationTokenByEmailOrIP(email, ip_address):
    """
    Retrieves a registration token by email or IP address.

    Args:
        email (str): The email to check.
        ip_address (str): The IP address to check.

    Returns:
        dict: A dictionary containing the token data, or None if not found.
    """
    retVal = getValueFromAnotherValue(
        selectFolder + "get_registration_token_by_email_or_ip.sql",
        (email, ip_address),
    )
    if isinstance(retVal, str) and "Error" in retVal:
        return None
    return retVal
