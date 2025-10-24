import sqlite3
from datetime import datetime
selectFolder = "SQLiteQueries/selectHandler/"

def dictify_real_dict_row(row):
    def convert_value(val):
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, list):
            return [convert_value(i) for i in val]
        if isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val

    print(row)

    return {k: convert_value(v) for k, v in row.items()}


def get_user_profile(email):
   
    # print(f"---------------------{email}")
    result = None
    try:
        # Read SQL code from file
        with open(selectFolder + "get_profile.sql", 'r') as file:
            sql_code = file.read()

        # print(sql_code)
        # Connect to database
        conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
        conn.row_factory = sqlite3.Row
        print(conn)
        cursor = conn.cursor()

        print(cursor)
        cursor.execute(sql_code, (email,))
        result = dict(cursor.fetchone())

        # print("-------------------------------------")
        # print(result)
        # print("-------------------------------------")
        # print()
        # print()

        status = "User get successful"
    except Exception as e:
        status = f"-------------------------------------- Error retrieving data data: {e}"
        print(status)
        conn.close()
        if result is None: 
            return None

    finally:
        conn.close()

    return dictify_real_dict_row(result)




# def get_user_profile(email):
#     result = None
#     try:
#         # Read SQL code from file
#         with open(selectFolder + "get_user_by_email.sql", 'r') as file:
#             sql_code = file.read()

#         # Connect to database
#         conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
#         cursor = conn.cursor()

#         cursor.execute(sql_code, (email,))
#         result = cursor.fetchone()

#         print("-------------------------------------")
#         print(result)
#         print("-------------------------------------")
#         print()
#         print()

#         if result is None: 
#             return None

#         status = "Insert successful"
#     except Exception as e:
#         status = f"Error inserting data: {e}"
#     finally:
#         conn.close()

#     return dictify_real_dict_row(result)

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


