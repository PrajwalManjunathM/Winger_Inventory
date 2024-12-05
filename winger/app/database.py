import mysql.connector
from mysql.connector import Error

# Database connection details
HOST = "0.tcp.in.ngrok.io"  # Update with ngrok host
PORT = 12908  # Update with ngrok port
USER = "root"  # Replace with your MySQL username
PASSWORD = ""  # Replace with your MySQL password
DATABASE = "inventory_system"

def insert_item(userid,item_name, item_specifications, scanned_code, current_status, comments, vendor_name, invoice_number, warranty_start, warranty_months, warranty_end):
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

            # Insert item into Items table
            insert_query = """
            INSERT INTO Items (item_name, item_specifications, scanned_code, current_status, comments, vendor_name, invoice_number, warranty_start, warranty_months, warranty_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (item_name, item_specifications, scanned_code, current_status, comments, vendor_name, invoice_number, warranty_start, warranty_months, warranty_end)
            cursor.execute(insert_query, data)
            connection.commit()

            # Get the inserted item_id
            item_id = cursor.lastrowid

            # Insert audit log
            audit_query = """
            INSERT INTO Audit (item_id, user_id, action_performed, previous_status, new_status, comments, vendor_name, invoice_number, warranty_start, warranty_months, warranty_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            audit_data = (item_id, userid, 'Inserted', 'Null',current_status, comments, vendor_name, invoice_number, warranty_start, warranty_months, warranty_end)
            cursor.execute(audit_query, audit_data)
            connection.commit()

            print(f"Item inserted successfully with item_id: {item_id} and audit log created.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_item_by_scanned_code(userid,scanned_code, new_status, comments, dc_number, wil_number):
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

            # Fetch the existing data using scanned_code
            select_query = "SELECT item_id, current_status, item_name FROM Items WHERE scanned_code = %s"
            cursor.execute(select_query, (scanned_code,))
            result = cursor.fetchone()

            if result:
                item_id, previous_status, item_name = result

                # Update item with new status, dc_number, and wil_number
                update_query = """
                UPDATE Items
                SET current_status = %s, comments = %s, dc_number = %s, wil_number = %s
                WHERE scanned_code = %s
                """
                cursor.execute(update_query, ("Rented", comments, dc_number, wil_number, scanned_code))
                connection.commit()

                # Insert audit log
                audit_query = """
                INSERT INTO Audit (item_id, user_id, action_performed, previous_status, new_status, comments,dc_number,wil_number)
                VALUES (%s, %s, %s, %s, %s, %s,%s,%s)
                """
                audit_data = (item_id, userid, 'Updated', previous_status, "Rented", comments,dc_number,wil_number)
                cursor.execute(audit_query, audit_data)
                connection.commit()

                print(f"Item with scanned_code: {scanned_code} updated successfully, and audit log created.")
            else:
                print(f"No item found with scanned_code: {scanned_code}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_item_by_scanned_code_sold(userid,scanned_code, new_status, comments, dc_number, wil_number):
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

            # Fetch the existing data using scanned_code
            select_query = "SELECT item_id, current_status, item_name FROM Items WHERE scanned_code = %s"
            cursor.execute(select_query, (scanned_code,))
            result = cursor.fetchone()

            if result:
                item_id, previous_status, item_name = result

                # Update item with new status, dc_number, and wil_number
                update_query = """
                UPDATE Items
                SET current_status = %s, comments = %s, dc_number = %s, wil_number = %s
                WHERE scanned_code = %s
                """
                cursor.execute(update_query, ("Sold", comments, dc_number, wil_number, scanned_code))
                connection.commit()

                # Insert audit log
                audit_query = """
                INSERT INTO Audit (item_id, user_id, action_performed, previous_status, new_status, comments,dc_number,wil_number)
                VALUES (%s, %s, %s, %s, %s, %s,%s,%s)
                """
                audit_data = (item_id, userid, 'Selling', previous_status, "Sold", comments,dc_number,wil_number)
                cursor.execute(audit_query, audit_data)
                connection.commit()

                print(f"Item with scanned_code: {scanned_code} updated successfully, and audit log created.")
            else:
                print(f"No item found with scanned_code: {scanned_code}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_item_by_scanned_code_back_to_inventory(userid,scanned_code, new_status, comments, rdc_number):
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

            # Fetch the existing data using scanned_code
            select_query = "SELECT item_id, current_status, item_name FROM Items WHERE scanned_code = %s"
            cursor.execute(select_query, (scanned_code,))
            result = cursor.fetchone()

            if result:
                item_id, previous_status, item_name = result

                # Update item with new status, dc_number, and wil_number
                update_query = """
                UPDATE Items
                SET current_status = %s, comments = %s, dc_number = %s, wil_number = %s, rdc_number = %s
                WHERE scanned_code = %s
                """
                cursor.execute(update_query, ("Inventory", comments, '', '', rdc_number, scanned_code))
                connection.commit()

                # Insert audit log
                audit_query = """
                INSERT INTO Audit (item_id, user_id, action_performed, previous_status, new_status, comments, dc_number, wil_number, rdc_number)
                VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)
                """
                audit_data = (item_id, userid, 'Back To Inventory', previous_status, "Inventory", comments,'NULL','NULL', rdc_number)
                cursor.execute(audit_query, audit_data)
                connection.commit()

                print(f"Item with scanned_code: {scanned_code} updated successfully, and audit log created.")
            else:
                print(f"No item found with scanned_code: {scanned_code}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# Example Usage:
# Insert a new item
# insert_item("Ram", "16GB RAM", "SCAN001", "Inventory",  "Initial entry")

# for rent
# update_item_by_scanned_code('SCAN001', 'Rented', 'Updating', 'DC-1234', 'WIL-1234')

# for selling
# update_item_by_scanned_code_sold('SCAN001', 'Sold', 'selling', 'DC-1234', 'WIL-1234')

#back to inventory
# update_item_by_scanned_code_back_to_inventory('9876543210', 'Inventory', 'back to inventory','212121')