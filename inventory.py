import db_connection
import users
import audit_log


def add_inventory_item(
    user,
    item_name,
    item_category,
    description,
    initial_quantity,
    expiration_date,
    minimum_threshold,
):
    """Adds new items, admin use only

    Args:
        user (CurrentUser): Current user object
        item_name (String): Item name
        item_category (String): Category of the item
        description (String): Description of the item
        initial_quantity (int): Starting quantity of item
        expiration_date (String): dateString in YYYY-MM-DD format
        minimum_threshold (int): Minimum threshold before alert
    """

    connection = db_connection.connect_to_database()

    if user.role == "Admin":
        cursor = connection.cursor()
        query = "SELECT COUNT(*) AS num_rows FROM inventory WHERE item_name = %s"
        query_list = [item_name]
        cursor.execute(query, query_list)

        num_item = cursor.fetchall()
        num_item = num_item[0][0]

        if num_item == 0:
            query = "INSERT INTO inventory (item_name, category, description, quantity, expiration_date, min_threshold) VALUES(%s, %s, %s, %s, %s, %s)"
            query_list = [
                item_name,
                item_category,
                description,
                initial_quantity,
                expiration_date,
                minimum_threshold,
            ]

            cursor.execute(query, query_list)
            print(item_name + " added to inventory database")

            audit_log.update_audit_log(
                user, item_name, "ADD", "Added item to inventory"
            )

            connection.commit()

        else:
            print("Item " + item_name + " already exists, please update item instead")

        cursor.close()

    else:
        print("You do not have access to this function")


def update_inventory_item(user, item, action):
    """Modify an existing inventory item properties, admin or user use

    Args:
        user (CurrentUser): Current user object
        item (String): Name of item being updated
        action (String): Allows admins or users to "increase", "decrease", "update quantity", "update expiration", "update description" or "update minimum threshold"
    """

    if user.role == "Admin" or "User":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        if action == "increase":
            quantity = input("Increase quantity by: ")

            query = "SELECT quantity FROM inventory WHERE item_name = %s"
            query_list = [item]
            cursor.execute(query, query_list)
            updated_quantity = cursor.fetchone()[0] + int(quantity)

            query = "UPDATE inventory SET quantity = %s WHERE item_name = %s"
            query_list = [updated_quantity, item]
            cursor.execute(query, query_list)

            print("Quantity of " + item + " increased to " + str(updated_quantity))
            audit_log.update_audit_log(
                user, item, "UPDATE", "Quantity increased by " + quantity
            )

        elif action == "decrease":
            quantity = input("Decrease quantity by: ")

            query = "SELECT quantity FROM inventory WHERE item_name = %s"
            query_list = [item]
            cursor.execute(query, query_list)
            updated_quantity = cursor.fetchone()[0] - int(quantity)

            query = "UPDATE inventory SET quantity = %s WHERE item_name = %s"
            query_list = [updated_quantity, item]
            cursor.execute(query, query_list)

            print("Quantity of " + item + " decreased to " + str(updated_quantity))
            audit_log.update_audit_log(
                user, item, "UPDATE", "Quantity decreased by " + quantity
            )

        elif action == "update quantity":
            quantity = input("New quantity of item: ")

            query = "UPDATE inventory SET quantity = %s WHERE item_name = %s"
            query_list = [quantity, item]
            cursor.execute(query, query_list)
            updated_quantity = cursor.fetchone()[0]

            print("Quantity of " + item + " set to " + str(updated_quantity))
            audit_log.update_audit_log(
                user, item, "UPDATE", "Quantity set to " + quantity
            )

        elif action == "update expiration":
            new_expiration = input("New expiration date: ")

            query = "UPDATE inventory SET expiration_date = %s WHERE item_name = %s"
            query_list = [new_expiration, item]
            cursor.execute(query, query_list)

            print("Expiration date of " + item + " set to " + str(new_expiration))
            audit_log.update_audit_log(
                user, item, "UPDATE", "Expiration set to " + new_expiration
            )

        elif action == "update description":
            new_description = input("New description: ")

            query = "UPDATE inventory SET description = %s WHERE item_name = %s"
            query_list = [new_description, item]
            cursor.execute(query, query_list)

            print("Description of " + item + " set to " + str(new_description))
            audit_log.update_audit_log(
                user, item, "UPDATE", "Description set to " + new_description
            )

        elif action == "update minimum threshold":
            new_minimum_threshold = input("New minimum threshold: ")

            query = "UPDATE inventory SET min_threshold = %s WHERE item_name = %s"
            query_list = [int(new_minimum_threshold), item]
            cursor.execute(query, query_list)

            print("Minimum threshold of " + item + " set to " + new_minimum_threshold)
            audit_log.update_audit_log(
                user,
                item,
                "UPDATE",
                "Minimum threshold set to " + new_minimum_threshold,
            )

        else:
            print("Action not valid")

        connection.commit()
        cursor.close()

    else:
        print("You do not have access to this function")


def delete_item(user, item_name):
    """Deletes an item, admin use only

    Args:
        user (CurrentUser): Current user object
        item_name (String): Item to delete
    """
    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "DELETE FROM inventory WHERE item_name = %s"
        query_list = [item_name]
        cursor.execute(query, query_list)
        print(item_name + " deleted")
        audit_log.update_audit_log(user, item_name, "DELETE", "Deleted item")

        connection.commit()
        cursor.close()

    else:
        print("You do not have access to this function")


def show_item(user, item_name):
    """Views an item, admin or user use

    Args:
        user (CurrentUser): Current user object
        item_name (String): Item to view
    """
    if user.role == "Admin" or "User":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "SELECT * FROM inventory WHERE item_name = %s"
        query_list = [item_name]
        cursor.execute(query, query_list)

        print(cursor.fetchall())

        cursor.close()

    else:
        print("You do not have access to this function")
