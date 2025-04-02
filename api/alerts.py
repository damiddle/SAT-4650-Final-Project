import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection


def search_for_expiration():
    try:
        expired_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, expiration_date FROM inventory WHERE expiration_date IS NOT NULL AND expiration_date < CURDATE() ORDER BY expiration_date ASC",
            None,
            False,
        )

        print(
            f"Item: {expired_inventory[0][0]} | Quantity: {expired_inventory[0][1]} | Expiration date: {expired_inventory[0][2]}"
        )

    except Exception as e:
        print(f"Database error: {e}")


def search_for_low_quantity():
    try:
        low_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, min_threshold FROM inventory WHERE min_threshold IS NOT NULL AND quantity < min_threshold ORDER BY quantity ASC",
            None,
            False,
        )

        print(
            f"Item: {low_inventory[0][0]} | Quantity: {low_inventory[0][1]} | Minimum threshold: {low_inventory[0][2]}"
        )

    except Exception as e:
        print(f"Database error: {e}")
