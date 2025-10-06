import os
from dotenv import load_dotenv
load_dotenv()

from pprint import pprint

import psycopg2
from psycopg2.extras import RealDictCursor



conn_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

# print("Connection parameters:", conn_params )

def get_db_connection():
    try:
        conn = psycopg2.connect(**conn_params, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def submit_query(query, params=None):
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




def insert_user(name, email, address, zip_code, cell_phone, register_ip):
    conn = get_db_connection()
    pprint(f"DB Connection: {conn}")
    if conn is None:
        pprint("No DB connection")
        return False
    try:
        with conn.cursor() as cursor:
            sql="""
                INSERT INTO users (name, email, address, zip_code, cell_phone, register_ip, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    address = EXCLUDED.address,
                    zip_code = EXCLUDED.zip_code,
                    cell_phone = EXCLUDED.cell_phone;
            """
            cursor.execute(sql, (name, email, address, zip_code, cell_phone, register_ip))
            conn.commit()
            cursor.close()
            conn.close()
        return True
    except Exception as e:
        print(f"Error inserting user: {e}")
        return False
    finally:
        conn.close()

def fetch_user_by_email(email):
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
