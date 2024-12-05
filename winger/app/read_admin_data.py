import mysql.connector
from mysql.connector import Error

# Database connection details
HOST = "0.tcp.in.ngrok.io"  # Replace with your ngrok host
PORT = 14064  # Replace with your ngrok port
USER = "root"  # Replace with your MySQL username
PASSWORD = ""  # Replace with your MySQL password
DATABASE = "inventory_system"

userid = 0
role = None  # Initialize role as None

def authenticate_admin(username, password):
    global userid, role
    userid = None  # Reset user ID
    role = None    # Reset role
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query to authenticate user and fetch role
            auth_query = """
            SELECT user_id, role FROM Users WHERE username = %s AND password_hash = %s
            """
            cursor.execute(auth_query, (username, password))
            result = cursor.fetchone()

            if result:
                userid, role = result  # Extract user ID and role
                print(f"Authentication successful! User ID: {userid}, Role: {role}")
            else:
                print("Authentication failed! Invalid username or password.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

    return userid, role  # Return the user ID and role