import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_connection


def search_for_expiration():
    """Creates a list of expired inventory items

    Returns:
        List of tuples: Returns a list of each item that is expired, each item is displayed in a tuple with its name, current quantity, and expiration date
    """
    try:
        expired_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, expiration_date FROM inventory WHERE expiration_date IS NOT NULL AND expiration_date < CURDATE() ORDER BY expiration_date ASC",
            None,
            False,
        )
        return expired_inventory
    except Exception as e:
        print(f"An error occurred while searching for expired inventory: {e}")
        return


def search_for_low_quantity():
    """Creates a list of all inventory that is less than the minimum threshold

    Returns:
        List of tuples: Returns a list of each low inventory item, which is created as a tuple with its name, current quantity, and minimum threshold value
    """
    try:
        low_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, min_threshold FROM inventory WHERE min_threshold IS NOT NULL AND quantity < min_threshold ORDER BY quantity ASC",
            None,
            False,
        )
        return low_inventory
    except Exception as e:
        print(f"An error occurred while searching for low inventory: {e}")
        return
