import mysql.connector
from mysql.connector import Error
from datetime import datetime
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

# Database connection details
HOST = "0.tcp.in.ngrok.io"  # Replace with your ngrok host
PORT = 12908  # Replace with your ngrok port
USER = "root"  # Replace with your MySQL username
PASSWORD = ""  # Replace with your MySQL password
DATABASE = "inventory_system"

userid=0
role = None  # Initialize role as None
list = []
ih = []

def list_all_users():
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

            # Select query to fetch all users
            select_query = "SELECT username, full_name, password_hash FROM users"
            cursor.execute(select_query)
            results = cursor.fetchall()  # Fetch all rows

            # Print user details
            if results:
                print("Listing all users:")
                for row in results:
                    users = {}
                    username, full_name, password = row
                    users['Username'] = username
                    users['Full_Name'] = full_name
                    users['Password'] = password
                    # print(users)
                    list.append(users)
                return list
            else:
                print("No users found in the database.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")



def authenticate_user(username, password):
    global userid
    userid = None  # Initialize user ID as None
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

            # Query to authenticate user
            auth_query = """
            SELECT user_id FROM Users WHERE username = %s AND password_hash = %s
            """
            cursor.execute(auth_query, (username, password))
            result = cursor.fetchone()

            if result:

                userid = result[0]  # Extract user ID
                # print(f"Authentication successful! User ID: {userid}")
            else:
                print("Authentication failed! Invalid username or password.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            # print("Database connection closed.")

    return userid  # Return the user ID

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

def insert_user(username, full_name, password, role):
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

            # Insert query
            insert_query = """
            INSERT INTO users (username, full_name, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, full_name, password, role))
            connection.commit()  # Commit the transaction

            print(f"User '{username}' added successfully!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

def routine_check(user_id, scanned_codes_list):
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

            # Fetch all items with "Inventory" status
            fetch_query = """
            SELECT item_id, item_name, scanned_code FROM Items WHERE current_status = 'Inventory'
            """
            cursor.execute(fetch_query)
            inventory_items = cursor.fetchall()

            if not inventory_items:
                print("No items in inventory to check.")
                return {}

            # Create a dictionary from inventory items for easy lookup
            inventory_dict = {
                item[2]: (item[0], item[1])  # Key: scanned_code, Value: (item_id, item_name)
                for item in inventory_items
            }

            # Convert the input list to a set for comparison
            scanned_codes = set(scanned_codes_list)

            # Identify missing items
            missing_items_codes = set(inventory_dict.keys()) - scanned_codes
            missing_items = {}

            if missing_items_codes:
                for missing_code in missing_items_codes:
                    missing_items[missing_code] = {
                        "item_id": inventory_dict[missing_code][0],
                        "item_name": inventory_dict[missing_code][1]
                    }

                    # Log missing item in Audit table
                    log_query = """
                    INSERT INTO Audit (item_id, user_id, action_performed, comments)
                    VALUES (%s, %s, %s, %s)
                    """
                    log_data = (
                        inventory_dict[missing_code][0],
                        user_id,
                        'Missing',
                        'Item not scanned during routine check.'
                    )
                    cursor.execute(log_query, log_data)
                    connection.commit()

            # Return the dictionary of missing items
            return missing_items

    except Error as e:
        print(f"Error: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")


def format_datetime(dt):
    """
    Convert a datetime object into a readable string format.

    Args:
        dt (datetime): The datetime object to format.

    Returns:
        str: Formatted datetime string in "YYYY-MM-DD HH:MM:SS" format.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def fetch_users_by_scanned_code(scanned_code):
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Get item_id using scanned_code
            select_item_query = "SELECT item_id FROM Items WHERE scanned_code = %s"
            cursor.execute(select_item_query, (scanned_code,))
            result = cursor.fetchone()

            if result:
                item_id = result[0]

                # Fetch user interactions from the Audit table
                interaction_query = """
                SELECT a.user_id, u.username, a.action_performed, a.previous_status, a.new_status, a.comments, a.action_date
                FROM Audit a
                INNER JOIN Users u ON a.user_id = u.user_id
                WHERE a.item_id = %s
                ORDER BY a.action_date DESC
                """
                cursor.execute(interaction_query, (item_id,))
                interactions = cursor.fetchall()
                ih = []
                if interactions:
                    print(f"Users who interacted with item (scanned_code: {scanned_code}):\n")
                    for interaction in interactions:
                        i = {}
                        user_id, username, action, prev_status, new_status, comments, timestamp = interaction
                        i['User ID'] = user_id
                        i['Username'] = username
                        i['Action'] = action
                        i['Previous Status'] = prev_status
                        i['New Status'] = new_status
                        i['Comments'] = comments
                        i['Timestamp'] = format_datetime(timestamp)
                        ih.append(i)

                else:
                    print(f"No interactions found for item with scanned_code: {scanned_code}")
            else:
                print(f"No item found with scanned_code: {scanned_code}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
        print(ih)
        return ih


def decode(img):
    if img is None:
        print("Failed to load image. Check the file path and try again.")
    else:
        code = decode(img)
        return code[0].data.decode('utf-8')


def calculate_warranty_end_date(start_date: str, warranty_period_months: int) -> str:
    """
    Calculate the warranty end date.

    :param start_date: The start date in 'YYYY-MM-DD' format.
    :param warranty_period_months: The warranty period in months.
    :return: The warranty end date in 'YYYY-MM-DD' format.
    """
    # Parse the start date
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    # Add the warranty period
    end_date_obj = start_date_obj + relativedelta(months=warranty_period_months)
    # Return the end date in the same format
    return end_date_obj.strftime("%Y-%m-%d")

def get_inventory_status():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query to count total inventory items
            inventory_items_query = """
                        SELECT COUNT(*) FROM Items WHERE current_status = 'Inventory';
                        """
            cursor.execute(inventory_items_query)
            total_items = cursor.fetchone()[0]

            # Query to count total rented items
            rented_items_query = """
            SELECT COUNT(*) FROM Items WHERE current_status = 'Rented';
            """
            cursor.execute(rented_items_query)
            total_rented = cursor.fetchone()[0]

            # Query to count total sold items
            sold_items_query = """
            SELECT COUNT(*) FROM Items WHERE current_status = 'Sold';
            """
            cursor.execute(sold_items_query)
            total_sold = cursor.fetchone()[0]

            # Query to count unique item_id where action_performed is 'Missing'
            missing_count = """
            SELECT COUNT(DISTINCT item_id) 
            FROM Audit 
            WHERE action_performed = 'Missing';
            """
            cursor.execute(missing_count)
            missing = cursor.fetchone()[0]

            # Calculate current date and date 7 days from now
            today = datetime.now().date()
            next_week = today + timedelta(days=7)

            # Query to count items with warranty_end within the next 7 days
            query = """
            SELECT COUNT(*)
            FROM Items
            WHERE warranty_end BETWEEN %s AND %s;
            """
            cursor.execute(query, (today, next_week))
            result = cursor.fetchone()[0]

            return {
                "total_items": total_items,
                "total_rented": total_rented,
                "total_sold": total_sold,
                "missing_count" : missing,
                "warranty_count" : result
            }

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_inventory_items():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT item_name, scanned_code, warranty_end FROM Items WHERE current_status = 'Inventory'"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_rented_items():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT item_name, scanned_code, warranty_end FROM Items WHERE current_status = 'Rented'"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_sold_items():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT item_name, scanned_code, warranty_end FROM Items WHERE current_status = 'Sold'"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_missing_items_details():
    results = {}  # Dictionary to hold the latest record for each item_id

    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query to retrieve all records where action_performed is 'Missing'
            query = """
            SELECT DISTINCT(item_id), new_status, action_date, user_id
            FROM Audit
            WHERE action_performed = 'Missing'
            ORDER BY action_date DESC;
            """
            cursor.execute(query)
            audit_results = cursor.fetchall()

            for audit_result in audit_results:
                item_id = audit_result[0]

                # Skip if the item_id is already processed (we want only the latest unique entry)
                if item_id in results:
                    continue

                item_details = {}
                item_details['item_id'] = item_id
                item_details['current_status'] = audit_result[1]
                item_details['action_date'] = audit_result[2].strftime("%Y-%m-%d %H:%M:%S")
                item_details['user_id_checked'] = audit_result[3]

                # Query to retrieve item_name and scanned_code for the current item_id
                query_2 = """
                SELECT item_name, scanned_code
                FROM items
                WHERE item_id = {id};
                """.format(id=item_id)
                cursor.execute(query_2)
                items_result = cursor.fetchone()
                if items_result:
                    item_details['item_name'] = items_result[0]
                    item_details['scanned_code'] = items_result[1]

                # Query to retrieve the user_id and action_date of the latest action NOT 'Missing'
                query_latest_user = """
                            SELECT user_id, action_date
                            FROM Audit
                            WHERE action_performed != 'Missing' AND item_id = {id}
                            ORDER BY action_date DESC
                            LIMIT 1;
                            """.format(id=item_id)
                cursor.execute(query_latest_user)
                latest_user_result = cursor.fetchone()
                if latest_user_result:
                    item_details['last_action_user_id'] = latest_user_result[0]
                    last_action_user_id = latest_user_result[0]

                    # Query to retrieve the username for the last_action_user_id
                    query_latest_user_name = """
                    SELECT username
                    FROM users
                    WHERE user_id = {id};
                    """.format(id=last_action_user_id)
                    cursor.execute(query_latest_user_name)
                    latest_user_name_result = cursor.fetchone()
                    if latest_user_name_result:
                        item_details['last_action_user_name'] = latest_user_name_result[0]

                # Add to results using item_id as a key
                results[item_id] = item_details

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    # Return the values of the results dictionary as a list
    return results.values()

def get_items_details_with_expiring_warranty():
    """Returns the details of items with warranty_end within the next 7 days."""
    try:
        # Establish connection to the database
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # Use dictionary=True to fetch results as dictionaries

            # Calculate current date and date 7 days from now
            today = datetime.now().date()
            next_week = today + timedelta(days=7)

            # Query to fetch items with warranty_end within the next 7 days
            query = """
            SELECT warranty_start, warranty_end, warranty_months, item_name, scanned_code
            FROM Items
            WHERE warranty_end BETWEEN %s AND %s;
            """

            cursor.execute(query, (today, next_week))
            result = cursor.fetchall()  # Fetch all rows matching the query

            result[0]['warranty_start'] = result[0]['warranty_start'].strftime("%Y-%m-%d")
            result[0]['warranty_end'] = result[0]['warranty_end'].strftime("%Y-%m-%d")
            return result

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

