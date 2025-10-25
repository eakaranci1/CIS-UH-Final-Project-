import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query, params=None):   # ← 3rd arg here
    cur = connection.cursor()
    try:
        cur.execute(query, params or ())             # ← use params
        connection.commit()
        return True, cur.lastrowid, cur.rowcount
    except Error as e:
        print(f"The error '{e}' occurred")
        return False, None, 0

def execute_read_query(connection, query, params=None):
    cur = connection.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        return cur.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
