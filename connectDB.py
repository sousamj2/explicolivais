import os
from dotenv import load_dotenv
load_dotenv()

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
    
def insert_user(name, email, address, zip_code, cell_phone, register_ip):
    conn = get_db_connection()
    if conn is None:
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