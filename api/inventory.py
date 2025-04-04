import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_connection
import api.audit_log as audit_log
from utils.decorators import roles_required
import utils.validators as validators
from mysql.connector import Error as MySQLError


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
    """Adds an inventory item

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        item_category (String): Category of item
        description (String): Description of item
        initial_quantity (int): Initial quantity of item
        expiration_date (date): Nearest date of expiration
        minimum_threshold (int): Smallest quantity of item before alert

    Raises:
        TypeError: Item is empty string
        TypeError: Quantity is a non-positive integer
        TypeError: Incorrectly formatted expiration date
        TypeError: Minimum threshold is a non-positive integer
    """
    try:
        # Check if the item already exists
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


@roles_required(["Admin", "User"])
def increase_item(current_user, item_name, quantity):
    """Increases item quantity

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        quantity (int): Quantity to increase item by

    Raises:
        TypeError: Item name is an empty string
        TypeError: Quantity is not a positive integer
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")
        db_connection.execute_query(
            "UPDATE inventory SET quantity = quantity + %s WHERE item_name = %s",
            [quantity, item_name],
        )
        print("Quantity of " + item_name + " increased")
        audit_log.update_audit_log(
            current_user,
            item_name,
            "UPDATE",
            "Quantity increased by " + str(quantity),
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while increasing item quantity: {e}")


@roles_required(["Admin", "User"])
def decrease_item(current_user, item_name, quantity):
    """Decreases inventory item quantity

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        quantity (int): Quantity to increase item by

    Raises:
        TypeError: Item name is an empty string
        TypeError: Quantity is not a positive integer
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")
        db_connection.execute_query(
            "UPDATE inventory SET quantity = quantity - %s WHERE item_name = %s",
            [quantity, item_name],
        )
        print("Quantity of " + item_name + " decreased")
        audit_log.update_audit_log(
            current_user,
            item_name,
            "UPDATE",
            "Quantity decreased by " + str(quantity),
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while decreasing item quantity: {e}")


@roles_required(["Admin", "User"])
def set_quantity(current_user, item_name, quantity):
    """Sets inventory item quantity

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        quantity (int): Quantity to increase item by

    Raises:
        TypeError: Item name is an empty string
        TypeError: Quantity is not a positive integer
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
        if not validators.is_positive_int(quantity):
            raise TypeError("Quantity must be a positive integer")
        db_connection.execute_query(
            "UPDATE inventory SET quantity = %s WHERE item_name = %s",
            [quantity, item_name],
        )
        print("Quantity of " + item_name + " set to " + str(quantity))
        audit_log.update_audit_log(
            current_user, item_name, "UPDATE", "Quantity set to " + str(quantity)
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while setting item quantity: {e}")


@roles_required(["Admin", "User"])
def set_expiration(current_user, item_name, new_expiration):
    """Sets new item expiration date

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        new_expiration (String): New expiration date (YYYY-MM-DD)

    Raises:
        TypeError: Item name is an empty string
        TypeError: Expiration date is not formatted YYYY-MM-DD
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
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


@roles_required(["Admin", "User"])
def set_description(current_user, item_name, new_description):
    """Sets new description of item

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        new_description (String): New description

    Raises:
        TypeError: Item name is an empty string
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
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


@roles_required(["Admin", "User"])
def set_minimum_threshold(current_user, item_name, new_minimum_threshold):
    """Sets new minimum threshold

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item
        new_minimum_threshold (int): New minimum threshold value

    Raises:
        TypeError: Item name is an empty string
        TypeError: Minimum threshold is not a positive integer
    """
    try:
        if not validators.is_non_empty_string(item_name):
            raise TypeError("Item name must be non-empty string")
        if not validators.is_positive_int(new_minimum_threshold):
            raise TypeError("New minimum threshold must be positive integer")
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


@roles_required(["Admin", "User"])
def show_item(current_user, item_name):
    """Retrieves an item

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item

    Raises:
        TypeError: Item name is an empty string
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
    """Deletes an item

    Args:
        current_user (CurrentUser): Current user
        item_name (String): Name of item

    Raises:
        TypeError: Item name is an empty string
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


@roles_required(["Admin", "User"])
def show_all_inventory(current_user):
    """Shows all inventory items

    Args:
        current_user (CurrentUser): Current user

    Returns:
        List: List of all inventory items
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
