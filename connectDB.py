import os
from dotenv import load_dotenv
load_dotenv()

from pprint import pprint

import psycopg2
from psycopg2.extras import RealDictCursor

from datetime import datetime, time, timedelta
from suntime import Sun
import pytz

def get_lisbon_greeting():
    latitude, longitude = 38.7169, -9.1399
    lisbon_tz = pytz.timezone('Europe/Lisbon')
    sun = Sun(latitude, longitude)

    now = datetime.now(lisbon_tz)
    today_datetime = datetime.combine(now.date(), time.min)

    # Get sunrise and sunset for today
    sunrise_utc = sun.get_sunrise_time(today_datetime)
    sunset_utc = sun.get_sunset_time(today_datetime)

    sunrise = sunrise_utc.astimezone(lisbon_tz)
    sunset = sunset_utc.astimezone(lisbon_tz)

    # If now is past today's sunset, get sunset for tomorrow
    if now > sunset:
        tomorrow_datetime = today_datetime + timedelta(days=1)
        sunset_utc = sun.get_sunset_time(tomorrow_datetime)
        sunset = sunset_utc.astimezone(lisbon_tz)

    # If now is earlier than today's sunrise, get sunrise for yesterday
    if now < sunrise:
        yesterday_datetime = today_datetime - timedelta(days=1)
        sunrise_utc = sun.get_sunrise_time(yesterday_datetime)
        sunrise = sunrise_utc.astimezone(lisbon_tz)

    noon = now.replace(hour=12, minute=0, second=0, microsecond=0)

    if sunrise <= now < noon:
        return "Bom dia"
    elif noon <= now < sunset:
        return "Boa tarde"
    else:
        return "Boa noite"

def dictify_real_dict_row(row):
    def convert_value(val):
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, list):
            return [convert_value(i) for i in val]
        if isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val

    return {k: convert_value(v) for k, v in row.items()}

def convert_datetimes(obj):
    if isinstance(obj, dict):
        return {k: convert_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj
    

# def get_user_profile(email):
#     conn = get_db_connection()
#     if not conn:
#         print("No DB connection")
#         return None
    
#     pprint(f"Retrieving profile data for {email}.")

#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 SELECT nome, email, lastlogin, morada, codigopostal, telemovel, vpn_check, first_contact_complete, first_session_complete,
#                     documents->'files' AS files
#                 FROM users
#                 WHERE email = %s
#                 LIMIT 1;
#             """
#             cursor.execute(sql, (email,))
#             result = cursor.fetchone()


#             if not result:
#                 return None

#             return dictify_real_dict_row(result)
            
#     except Exception as e:
#         print(f"Error retrieving user profile: {e}")
#         return None
#     finally:
#         conn.close()


def insert_user(name, email, address, zip_code, cell_phone, register_ip):
    conn = get_db_connection()
    if conn is None:
        print("No DB connection")
        return False
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO users (
                nome, email, morada, codigopostal, telemovel,
                ipcreated, thislogin, lastlogin, createdat, iplastlogin,
                documents, logincount,
                vpn_check, vpn_valid, first_contact_complete, first_session_complete
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, NOW(), NOW(), NOW(), %s,
                '{"files": [], "know_ip": [], "block_ip": {}, "preferences": {}}'::jsonb,
                1,
                FALSE, FALSE, FALSE, FALSE
            )
            """
            cursor.execute(sql, (
                name, email, address, zip_code, cell_phone,
                register_ip, register_ip
            ))
            conn.commit()

            # Add register_ip to the know_ip array in documents
            sql_update = """
            UPDATE users
            SET documents = jsonb_set(
                documents,
                '{know_ip}',
                CASE
                    WHEN %s = ANY (SELECT jsonb_array_elements_text(documents->'know_ip'))
                    THEN documents->'know_ip'
                    ELSE documents->'know_ip' || to_jsonb(%s::text)
                END,
                true
            )
            WHERE email = %s;
            """
            cursor.execute(sql_update, (register_ip, register_ip, email))
            conn.commit()


        return True
    except Exception as e:
        print(f"Error inserting user: {e}")
        return False
    finally:
        conn.close()

# def check_existing_user(register_ip, cell_phone):
#     conn = get_db_connection()
#     if not conn:
#         return None
#     try:
#         cur = conn.cursor()
#         query = """
#         SELECT email, createdat FROM users WHERE ipcreated = %s OR telemovel = %s LIMIT 1
#         """
#         cur.execute(query, (register_ip, cell_phone))
#         user = cur.fetchone()
#         cur.close()
#         return user
#     finally:
#         conn.close()

def mask_email(email):
    # Mask email username partially e.g. ma***@email.com
    parts = email.split('@')
    if len(parts[0]) <= 2:
        return "***@" + parts[1]
    return parts[0][:2] + "*****@" + parts[1]


def check_ip_in_portugal(ip):
    import requests
    try:
        # No token used here, but recommended to add your token as ?token=YOUR_TOKEN if needed
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("bogon", True):
                pprint(f"Bogon IP detected: {ip}")
                return True  # Bogon IPs are treated as local/trusted

            country_code = data.get("country", "").upper()
            region = data.get("region", "").lower()
            # Check country PT and region Lisboa or Lisbon (case insensitive)
            if country_code == "PT" and region in ["lisboa", "lisbon"]:
                return True
    except Exception as e:
        print(f"IP geolocation failed: {e}")
    return False

# def get_db_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv('POSTGRES_DB'),
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             host=os.getenv('POSTGRES_HOST'),
#             port=os.getenv('POSTGRES_PORT'),
#             cursor_factory=RealDictCursor
#         )
#         return conn
#     except Exception as e:
#         print(f"Error connecting to the database: {e}")
#         return None
    
# def submit_query(query, params=None):
    conn = get_db_connection()
    if conn is None:
        return "Error connecting to the database."
    try:
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

# def fetch_user_by_email(email):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()

# if __name__ == "__main__":
#     # Example usage
#     insert_user("John Doe", "john.doe2@example.com", "123 Main St", "12345", "556-1234", "123.57.89.0")

def results_to_html_table(results):
    if not results or not isinstance(results, list):
        return "<p>No data found.</p>"
    
    if isinstance(results[0],str):
        return results

    # Extract columns from keys of the first row dict
    columns = results[0].keys()
    
    table_html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    
    # Header row
    table_html += '<thead><tr>'
    for col in columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead>'
    
    # Data rows
    table_html += '<tbody>'
    for row in results:
        table_html += '<tr>'
        for col in columns:
            val = row[col]
            table_html += f'<td>{val if val is not None else ""}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    return table_html


# def check_and_create_users_table():
    conn = get_db_connection()
    if not conn:
        print("Database connection failed.")
        return False

    pprint("Database connection established.")

    pprint("Checking/Creating users table...")

    try:
        cur = conn.cursor()

        # Create table only if it does not exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL DEFAULT 'Unknown',
            email VARCHAR(255) NOT NULL UNIQUE,
            morada VARCHAR(255) NOT NULL DEFAULT 'Unknown',
            codigopostal VARCHAR(10) NOT NULL DEFAULT '0000-000',
            telemovel BIGINT NOT NULL UNIQUE DEFAULT floor(random() * 100000000) + 900000000,
            nif BIGINT NOT NULL UNIQUE DEFAULT floor(random() * 1000000000) + 9000000000,
            ipcreated INET NOT NULL,
            thislogin TIMESTAMP DEFAULT NOW(),
            lastlogin TIMESTAMP DEFAULT NOW(),
            createdat TIMESTAMP DEFAULT NOW(),
            iplastlogin INET NOT NULL,
            documents JSONB NOT NULL DEFAULT '{"files": [], "knowip": [], "blockip": {}, "preferences": {}}',
            logincount INTEGER NOT NULL DEFAULT 1,
            vpn_check boolean NOT NULL DEFAULT false,
            vpn_valid boolean NOT NULL DEFAULT false,
            first_contact_complete boolean NOT NULL DEFAULT false,
            first_session_complete boolean NOT NULL DEFAULT false
        );
        """)
        conn.commit()
        cur.close()
        print("Users table is ready.")
        return True

    except Exception as e:
        print(f"Error creating users table: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


# def refresh_last_login_and_ip(email, current_ip):
    conn = get_db_connection()
    if conn is None:
        print("No DB connection")
        return False

    try:
        with conn.cursor() as cursor:
            now = datetime.now()
            cursor.execute("""
                UPDATE users SET
                    lastlogin = thislogin,
                    iplastlogin = ipcreated,
                    thislogin = %s,
                    ipcreated = %s
                WHERE email = %s
            """, (now, current_ip, email))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error refreshing last login info: {e}")
        return False
    finally:
        conn.close()
