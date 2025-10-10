import sqlite3
from DBbaseline import *

def insertNewUser(first,last,email):
    conn,c = dbConnect()
    status = "Return correctly performed."
    sqlCode = """
    INSERT INTO users (primeiro, apelido, email) VALUES (?,?,?);
    """
    try:
        c.execute(sqlCode,(first,last,email))
        conn.commit()
    except Exception as e:
        status = f"Error inserting to users: {e}."
    
    conn.close()
    return status
        
def insertNewPersonalData(email,morada,cpostal1,cpostal2,telemovel,nfiscal):
    conn,c = dbConnect()
    status = "Return correctly performed."
    user_id = getUserIdFromEmail(email)
    sqlCode = """
    INSERT INTO personal
    ( user_id, morada,cpostal1,cpostal2,telemovel,nfiscal )
    VALUES (?,?,?,?,?,?)
    """
    try:
        c.execute(sqlCode, user_id, morada,cpostal1,cpostal2,telemovel,nfiscal)
        conn.commit()
    except Exception as e:
        status = f"Error inserting to personal: {e}."

    conn.close()
    return status


def insertNewIP(email,ipaddress):
    conn,c = dbConnect()
    status = "Return correctly performed."
    user_id = getUserIdFromEmail(email)
    sqlCode = """
    INSERT INTO iplist
    ( user_id, ipValue)
    VALUES (?,?)
    """
    try:
        c.execute(sqlCode, user_id, ipaddress)
        conn.commit()
    except Exception as e:
        status = f"Error inserting to IP list: {e}."

    conn.close()
    return status

def insertNewConnectionData(email,ipaddress):
    conn,c = dbConnect()
    status = "Return correctly performed."
    user_id = getUserIdFromEmail(email)
    sqlCode = """
    INSERT INTO personal
    ( user_id, createdatip, lastloginip, thisloginip)
    VALUES (?,?,?,?)
    """
    try:
        c.execute(sqlCode, user_id, ipaddress,ipaddress,ipaddress)
        conn.commit()
        
    except Exception as e:
        status = f"Error inserting to personal: {e}."

    conn.close()
    return " ".join( status, insertNewIP(email,ipaddress) )


def insertNewDocument(email,docname, docurl):
    conn,c = dbConnect()
    status = "Return correctly performed."
    user_id = getUserIdFromEmail(email)
    sqlCode = """
    INSERT INTO documents
    ( user_id, docname, docurl)
    VALUES (?,?,?)
    """
    try:
        c.execute(sqlCode, user_id, docname, docurl)
        conn.commit()
    except Exception as e:
        status = f"Error inserting to documents list: {e}."

    conn.close()
    return status

def insertNewClass(email, year, childName, disciplina="Matemática" ):
    conn,c = dbConnect()
    status = "Return correctly performed."
    user_id = getUserIdFromEmail(email)
    sqlCode = """
    INSERT INTO classes
    ( user_id, year, childName, disciplina)
    VALUES (?,?,?,?)
    """
    try:
        c.execute(sqlCode, user_id, year, childName, disciplina)
        conn.commit()
    except Exception as e:
        status = f"Error inserting to classes list: {e}."

    conn.close()
    return status
