import sqlite3
from DBbaseline import * 

def createAllTables():
    newTableIPs()
    newTableUsers()
    newTableClass()
    newTableDocuments()
    newTablePersonalData()
    newTableConnectionData()

def deleteAllTable():
    conn,c = dbConnect()
    sqlCode = """
    DROP TABLE users;
    DROP TABLE iplist;
    DROP TABLE documents;
    DROP TABLE connection;
    DROP TABLE personal;
    DROP TABLE classes;
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTableClass():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS classes (
    classes_id   INTEGER PRIMARY KEY,
    user_id INTEGER,
    year INTEGER NOT NULL,
    childName TEXT NOT NULL,
    firstClass TEXT, -- date
    firstContact TEXT, -- date
    disciplina TEXT NOT NULL DEFAULT
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTableIPs():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS iplist (
    ip_id   INTEGER PRIMARY KEY,
    user_id INTEGER,
    ipValue TEXT,
    ipValid INTEGER DEFAULT TRUE,
    firstAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    logincount INTEGER NOT NULL DEFAULT 1
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTableDocuments():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS documents (
    docu_id   INTEGER PRIMARY KEY,
    user_id   INTEGER,
    visible   INTEGER DEFAULT FALSE,
    docname   TEXT,
    docurl    TEXT,
    createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTableConnectionData():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS connection (
    connection_id  INTEGER PRIMARY KEY,
    user_id  INTEGER,
    createdatts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    thislogints TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastlogints TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    createdatip TEXT NOT NULL, --> To UNIQUE
    lastloginip TEXT NOT NULL,
    thisloginip TEXT NOT NULL,
    logincount    INTEGER NOT NULL DEFAULT 1,
    vpn_check     INTEGER NOT NULL DEFAULT FALSE,
    vpn_valid     INTEGER NOT NULL DEFAULT FALSE
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTablePersonalData():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS personal (
    personal_id  INTEGER PRIMARY KEY,
    user_id   INTEGER,
    morada    TEXT NOT NULL DEFAULT 'Unknown',
    numero    TEXT NOT NULL DEFAULT 'NA',
    andar     TEXT NOT NULL DEFAULT 'NA',
    porta     TEXT NOT NULL DEFAULT 'NA',
    observacoes TEXT,
    cpostal1  INTEGER        CHECK (cpostal1  > 0 AND cpostal <= 9999),
    cpostal2  INTEGER        CHECK (cpostal1  > 0 AND cpostal <= 999),
    telemovel INTEGER UNIQUE CHECK (telemovel > 910000000 AND telemovel <= 999999999),
    nfiscal   INTEGER UNIQUE CHECK (nfiscal   > 100000000 AND nfiscal <= 999999999)
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()

def newTableUsers():
    conn,c = dbConnect()
    sqlCode = """
    CREATE TABLE IF NOT EXISTS users (
    user_id  INTEGER PRIMARY KEY,
    email    TEXT UNIQUE,
    primeiro TEXT,
    apelido  TEXT,
    valid    INTEGER DEFAULT TRUE
    );
    """
    c.execute(sqlCode)
    conn.commit()
    conn.close()
