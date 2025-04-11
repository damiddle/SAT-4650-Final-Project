"""
Module for inventory management operations.

Provides functions for adding, updating, and deleting inventory items, as well as
viewing inventory details. All database changes are also logged in the audit log.
"""

import os
import sys

# Append the parent directory to the system path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection
import api.audit_log as audit_log
import utils.validators as validators
from utils.decorators import roles_required
from mysql.connector import Error as MySQLError


def perform_inventory_update(
    current_user, item_name, query, params, success_message, audit_message
):
    """Performs a generic inventory update with logging.

    Executes a database update query, prints a success message if the operation
    is successful, and updates the audit log.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the inventory item.
        query (str): The SQL query to execute.
        params (list): Parameters for the SQL query.
        success_message (str): Message to display on success.
        audit_message (str): Message to record in the audit log.

    Returns:
        object: The result of the database query if successful; otherwise, None.
    """

    try:
        result = db_connection.execute_query(query, params)

        if result is None:
            raise Exception("Database operation failed.")

        print(success_message)
        audit_log.update_audit_log(current_user, item_name, "UPDATE", audit_message)

        return result
    except Exception as e:
        print(f"Error: {e}")

        return None


@roles_required(["Admin"])
def add_inventory_item(
    current_user,
    item_name,
    item_category,
    description,
    initial_quantity,
    expiration_date,
    minimum_threshold,
):
    """Adds a new inventory item to the database.

    Checks for uniqueness of the item by name and validates input before insertion.
    Also updates the audit log upon success.

    Args:
        current_user (CurrentUser): The admin performing the operation.
        item_name (str): The name of the item.
        item_category (str): The category of the item.
        description (str): The description of the item.
        initial_quantity (int): The starting quantity.
        expiration_date (str): Expiration date in YYYY-MM-DD format.
        minimum_threshold (int): The minimum threshold for the item.

    Raises:
        TypeError: If any input is invalid.
        Exception: If a database error occurs.
    """

    try:
        result = db_connection.execute_query(
            "SELECT COUNT(*) AS num_rows FROM inventory WHERE item_name = %s",
            [item_name],
        )
        count = result[0][0] if result and len(result) > 0 else 0

        if count == 0:
            if not validators.is_non_empty_string(item_name):
                raise TypeError("Item name must be a non-empty string")

            if not validators.is_positive_int(initial_quantity):
                raise TypeError("Initial quantity must be a positive integer")

            if not validators.is_valid_date(expiration_date):
                raise TypeError("Expiration date must be formatted YYYY-MM-DD")

            if not validators.is_positive_int(minimum_threshold):
                raise TypeError("Minimum threshold must be a positive integer")

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

            print(f"{item_name} added to inventory database")
            audit_log.update_audit_log(
                current_user, item_name, "ADD", "Added item to inventory"
            )
        else:
            print(f"Item {item_name} already exists, please update item instead")
    except (MySQLError, Exception) as e:
        print(f"An error occurred while adding inventory item: {e}")


@roles_required(["Admin", "Leadership"])
def increase_item(current_user, item_name, quantity):
    """Increases the quantity of an inventory item.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        quantity (int): The quantity to increase by.

    Raises:
        TypeError: If parameters are invalid.
        Exception: If an error occurs during the update.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")

        query = "UPDATE inventory SET quantity = quantity + %s WHERE item_name = %s"
        perform_inventory_update(
            current_user,
            item_name,
            query,
            [quantity, item_name],
            f"Quantity of {item_name} increased",
            f"Quantity increased by {quantity}",
        )
    except Exception as e:
        print(f"An error occurred while increasing item quantity: {e}")


@roles_required(["Admin", "Leadership"])
def decrease_item(current_user, item_name, quantity):
    """Decreases the quantity of an inventory item.

    Ensures that the quantity does not fall below zero.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        quantity (int): The quantity to decrease by.

    Raises:
        TypeError: If parameters are invalid.
        ValueError: If quantity reduction would result in a negative quantity.
        Exception: If an error occurs during the update.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")

        current = db_connection.execute_query(
            "SELECT quantity FROM inventory WHERE item_name = %s", [item_name], False
        )

        if not current or len(current) == 0:
            raise Exception("Item not found")

        current_qty = current[0][0]
        if current_qty - quantity < 0:
            raise ValueError("Insufficient quantity: cannot decrease below 0")

        query = "UPDATE inventory SET quantity = quantity - %s WHERE item_name = %s"
        perform_inventory_update(
            current_user,
            item_name,
            query,
            [quantity, item_name],
            f"Quantity of {item_name} decreased",
            f"Quantity decreased by {quantity}",
        )
    except Exception as e:
        print(f"An error occurred while decreasing item quantity: {e}")


@roles_required(["Admin", "Leadership"])
def set_quantity(current_user, item_name, quantity):
    """Sets the quantity of an inventory item to an exact value.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        quantity (int): The new quantity value.

    Raises:
        TypeError: If parameters are invalid.
        ValueError: If quantity is negative.
        Exception: If an error occurs during the update.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        query = "UPDATE inventory SET quantity = %s WHERE item_name = %s"
        perform_inventory_update(
            current_user,
            item_name,
            query,
            [quantity, item_name],
            f"Quantity of {item_name} set to {quantity}",
            f"Quantity set to {quantity}",
        )
    except Exception as e:
        print(f"An error occurred while setting item quantity: {e}")


@roles_required(["Admin", "Leadership"])
def set_expiration(current_user, item_name, new_expiration):
    """Sets a new expiration date for an inventory item.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        new_expiration (str): New expiration date in YYYY-MM-DD format.

    Raises:
        TypeError: If inputs are invalid.
        Exception: If a database error occurs.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

        if not validators.is_valid_date(new_expiration):
            raise TypeError("Expiration date must be formatted YYYY-MM-DD")

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
    except (MySQLError, Exception) as e:
        print(f"An error occurred while setting the new expiration date: {e}")


@roles_required(["Admin", "Leadership"])
def set_description(current_user, item_name, new_description):
    """Updates the description of an inventory item.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        new_description (str): The new description text.

    Raises:
        TypeError: If item_name is invalid.
        Exception: If a database error occurs.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

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
    except (MySQLError, Exception) as e:
        print(f"An error occurred while setting the new description: {e}")


@roles_required(["Admin", "Leadership"])
def set_minimum_threshold(current_user, item_name, new_minimum_threshold):
    """Sets the minimum threshold for an inventory item.

    Args:
        current_user (CurrentUser): The user performing the update.
        item_name (str): The name of the item.
        new_minimum_threshold (int): The new minimum threshold value.

    Raises:
        TypeError: If inputs are invalid.
        Exception: If a database error occurs.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be a non-empty string")

        if not validators.is_positive_int(new_minimum_threshold):
            raise TypeError("New minimum threshold must be a positive integer")

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
    except (MySQLError, Exception) as e:
        print(f"An error occurred while setting the new minimum threshold: {e}")


@roles_required(["Admin", "Leadership", "General Responder"])
def show_item(current_user, item_name):
    """Retrieves details for a specific inventory item.

    Args:
        current_user (CurrentUser): The user requesting the item details.
        item_name (str): The name of the item.

    Returns:
        list: A list of item details or an empty list if an error occurs.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")

        item_contents = db_connection.execute_query(
            "SELECT * FROM inventory WHERE item_name = %s", [item_name], False
        )

        return item_contents
    except (MySQLError, Exception) as e:
        print(f"An error occurred while retrieving an item: {e}")

        return []


@roles_required(["Admin"])
def delete_item(current_user, item_name):
    """Deletes an inventory item from the database.

    Args:
        current_user (CurrentUser): The admin performing the deletion.
        item_name (str): The name of the item to delete.

    Raises:
        TypeError: If item_name is not valid.
        Exception: If a database error occurs.
    """

    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")

        db_connection.execute_query(
            "DELETE FROM inventory WHERE item_name = %s", [item_name]
        )

        print(item_name + " deleted from inventory")
        audit_log.update_audit_log(current_user, item_name, "DELETE", "Deleted item")
    except (MySQLError, Exception) as e:
        print(f"An error occurred while deleting item: {e}")


@roles_required(["Admin", "Leadership", "General Responder"])
def show_all_inventory(current_user):
    """Retrieves all inventory items and their details.

    Args:
        current_user (CurrentUser): The user requesting the inventory list.

    Returns:
        list: A list of inventory items or an empty list if an error occurs.
    """

    try:
        table_contents = db_connection.execute_query(
            "SELECT item_name, category, description, quantity, expiration_date, min_threshold, last_updated FROM inventory",
            None,
            False,
        )

        return table_contents
    except (MySQLError, Exception) as e:
        print(f"Database error occurred while retrieving all inventory: {e}")

        return []
