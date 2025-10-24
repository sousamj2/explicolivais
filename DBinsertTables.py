import sqlite3
from DBbaseline import getUserIdFromEmail
insertFolder = "SQLiteQueries/insertHandler/"

def execute_insert_from_file(sql_file_path, params_dict):
    """
    Executes an INSERT query from the SQL file at sql_file_path,
    using the values in params_dict as parameters.
    The dictionary keys should match the expected parameter order.
    """
    print(sql_file_path)

    try:
        # Read SQL code from file
        with open(sql_file_path, 'r') as file:
            sql_code = file.read()

        # Connect to database
        conn = sqlite3.connect('explicolivais.db')  # Adjust your DB path
        cursor = conn.cursor()

        # Prepare parameters tuple in the order matching the SQL placeholders
        # Assuming params_dict is an OrderedDict or that order is known
        params = tuple(params_dict[key] for key in params_dict)

        # Execute the SQL INSERT
        cursor.execute(sql_code, params)
        conn.commit()

        status = "Insert successful"
    except Exception as e:
        status = f"Error inserting data: {e}"
        print(status)
    finally:
        conn.close()

    return status

def insertNewUser(first,last,email):
    print(f"Inserting user with email {email}")

    insertFile = "insert_newUser.sql"
    insertDict = {"first": first, "last": last, "email": email}
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    print("Insert user:",status)
    return status
        
def insertNewPersonalData(email, address, number, floor, door, notes, zip_code1,zip_code2,cell_phone,nif):
    insertFile = "insert_newPersonalData.sql"
    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    insertDict = {"user_id": user_id,
                #    "email": email,
                   "address": address,
                   "number": number,
                   "floor": floor,
                   "door": door,
                   "notes": notes,
                   "zip_code1": zip_code1,
                   "zip_code2": zip_code2,
                   "cell_phone":cell_phone,
                   "nfiscal":nif}
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    print("Insert personal:",status)
    return status


def insertNewIP(email,ipaddress):
    insertFile = "insert_newIPaddress.sql"
    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    insertDict = {"user_id": user_id,
                  "ipvalue": ipaddress}
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    return status

def insertNewConnectionData(email,ipaddress):
    insertFile = "insert_newConnection.sql"
    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    insertDict = {"user_id": user_id,
                  "createdatip": ipaddress,
                  "lastloginip": ipaddress,
                  "thisloginip": ipaddress
                  }
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    return status, insertNewIP(email,ipaddress) + " " + status

def insertNewDocument(email,docname, docurl):
    insertFile = "insert_newDocument.sql"
    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    insertDict = {"user_id": user_id,
                  "docname": docname,
                  "docurl": docurl
                }
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    return status

def insertNewClass(email, year, childName, disciplina="Matemática" ):
    insertFile = "insert_newClass.sql"
    user_id = getUserIdFromEmail(email)
    if not user_id:
        return "ERROR: There is no user with this email: {email}."
    insertDict = {"user_id": user_id,
                  "year": year,
                  "childName": childName,
                  "disciplica": disciplina
    }
    status = execute_insert_from_file(insertFolder+insertFile,insertDict)
    return status

