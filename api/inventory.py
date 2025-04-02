import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection
import api.audit_log as audit_log


def add_inventory_item(
    current_user,
    item_name,
    item_category,
    description,
    initial_quantity,
    expiration_date,
    minimum_threshold,
):
    """Adds new items, admin use only

    Args:
        current_user (CurrentUser): Current user object
        item_name (String): Item name
        item_category (String): Category of the item
        description (String): Description of the item
        initial_quantity (int): Starting quantity of item
        expiration_date (String): dateString in YYYY-MM-DD format
        minimum_threshold (int): Minimum threshold before alert
    """

    if current_user.role == "Admin":
        num_item = db_connection.execute_query(
            "SELECT COUNT(*) AS num_rows FROM inventory WHERE item_name = %s",
            [item_name],
        )
        num_item = num_item[0][0]

        if num_item == 0:
            db_connection.execute_query(
                "INSERT INTO inventory (item_name, category, description, quantity, expiration_date, min_threshold) VALUES(%s, %s, %s, %s, %s, %s)",
                [
                    item_name,
                    item_category,
                    description,
                    initial_quantity,
                    expiration_date,
                    minimum_threshold,
                ],
            )
            print(item_name + " added to inventory database")

            audit_log.update_audit_log(
                current_user, item_name, "ADD", "Added item to inventory"
            )

        else:
            print("Item " + item_name + " already exists, please update item instead")

    else:
        print("You do not have access to this function")


def increase_item(current_user, item_name, quantity):
    if current_user.role == "Admin" or "User":
        try:
            updated_quantity = db_connection.execute_query(
                "SELECT quantity FROM inventory WHERE item_name = %s",
                [item_name],
                False,
            )
            updated_quantity = updated_quantity[0][0] + quantity

            db_connection.execute_query(
                "UPDATE inventory SET quantity = %s WHERE item_name = %s",
                [updated_quantity, item_name],
            )

            print("Quantity of " + item_name + " increased to " + str(updated_quantity))
            audit_log.update_audit_log(
                current_user,
                item_name,
                "UPDATE",
                "Quantity increased by " + str(quantity),
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def decrease_item(current_user, item_name, quantity):
    if current_user.role == "Admin" or "User":
        try:
            updated_quantity = db_connection.execute_query(
                "SELECT quantity FROM inventory WHERE item_name = %s",
                [item_name],
                False,
            )
            updated_quantity = updated_quantity[0][0] - quantity

            db_connection.execute_query(
                "UPDATE inventory SET quantity = %s WHERE item_name = %s",
                [updated_quantity, item_name],
            )

            print("Quantity of " + item_name + " decreased to " + str(updated_quantity))
            audit_log.update_audit_log(
                current_user,
                item_name,
                "UPDATE",
                "Quantity decreased by " + str(quantity),
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def set_quantity(current_user, item_name, quantity):
    if current_user.role == "Admin" or "User":
        try:
            db_connection.execute_query(
                "UPDATE inventory SET quantity = %s WHERE item_name = %s",
                [quantity, item_name],
            )
            print("Quantity of " + item_name + " set to " + str(quantity))
            audit_log.update_audit_log(
                current_user, item_name, "UPDATE", "Quantity set to " + str(quantity)
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def set_expiration(current_user, item_name, new_expiration):
    if current_user.role == "Admin" or "User":
        try:
            db_connection.execute_query(
                "UPDATE inventory SET expiration_date = %s WHERE item_name = %s",
                [new_expiration, item_name],
            )
            print("Expiration date of " + item_name + " set to " + str(new_expiration))
            audit_log.update_audit_log(
                current_user,
                item_name,
                "UPDATE",
                "Expiration date set to " + new_expiration,
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def set_description(current_user, item_name, new_description):
    if current_user.role == "Admin" or "User":
        try:
            db_connection.execute_query(
                "UPDATE inventory SET description = %s WHERE item_name = %s",
                [new_description, item_name],
            )
            print("Description of " + item_name + " set to " + str(new_description))
            audit_log.update_audit_log(
                current_user,
                item_name,
                "UPDATE",
                "Description set to " + new_description,
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def set_minimum_threshold(current_user, item_name, new_minimum_threshold):
    if current_user.role == "Admin" or "User":
        try:
            db_connection.execute_query(
                "UPDATE inventory SET min_threshold = %s WHERE item_name = %s",
                [new_minimum_threshold, item_name],
            )
            print(
                "Minimum threshold of "
                + item_name
                + " set to "
                + str(new_minimum_threshold)
            )
            audit_log.update_audit_log(
                current_user,
                item_name,
                "UPDATE",
                "Minimum threshold set to " + str(new_minimum_threshold),
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def show_item(current_user, item_name):
    """Views an item, admin or user use

    Args:
        user (CurrentUser): Current user object
        item_name (String): Item to view
    """

    if current_user.role == "Admin" or "User":
        try:
            print(
                db_connection.execute_query(
                    "SELECT * FROM inventory WHERE item_name = %s", [item_name], False
                )
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def delete_item(current_user, item_name):
    """Deletes an item, admin use only

    Args:
        user (CurrentUser): Current user object
        item_name (String): Item to delete
    """

    if current_user.role == "Admin":
        try:
            db_connection.execute_query(
                "DELETE FROM inventory WHERE item_name = %s", [item_name]
            )
            print(item_name + " deleted")

            audit_log.update_audit_log(
                current_user, item_name, "DELETE", "Deleted item"
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def show_all_inventory(current_user):
    if current_user.role == "Admin":
        try:
            table_contents = db_connection.execute_query(
                "SELECT item_name, category, description, quantity, expiration_date, min_threshold, last_updated FROM inventory",
                None,
                False,
            )

            return table_contents

        except Exception as e:
            print(f"Database error: {e}")
