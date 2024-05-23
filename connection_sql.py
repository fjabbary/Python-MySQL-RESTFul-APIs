import mysql.connector
from mysql.connector import Error
from variables import password

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            database="fitness_center",
            user="root",
            password=password,
            host="localhost"
        )

        if conn.is_connected():
            print("Connected to db succesfully")
            return conn
        
    except Error as e:
        print(f"Error: {e}")
        return None