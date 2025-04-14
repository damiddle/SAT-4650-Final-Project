"""
Module for inventory alerts.

Provides functions to search for expired inventory items and items with low quantities.
"""

from utils.decorators import roles_required
import logging
import db_connection

logger = logging.getLogger(__name__)


@roles_required(["Admin", "Leadership", "General Responder"])
def search_for_expiration(self):
    """Searches for inventory items whose expiration date has passed.

    Returns:
        list: A list of tuples containing item name, quantity, and expiration date.
              Returns an empty list if no expired items are found or an error occurs.
    """

    try:
        expired_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, expiration_date FROM inventory WHERE expiration_date IS NOT NULL AND expiration_date < CURDATE() ORDER BY expiration_date ASC",
            None,
            False,
        )

        return expired_inventory if expired_inventory is not None else []
    except Exception as e:
        logger.error(f"Expired inventory search error: {e}")

        return []


@roles_required(["Admin", "Leadership", "General Responder"])
def search_for_low_quantity(self):
    """Searches for inventory items with quantity below their minimum threshold.

    Returns:
        list: A list of tuples containing item name, current quantity, and minimum threshold.
              Returns an empty list if no such items are found or an error occurs.
    """

    try:
        low_inventory = db_connection.execute_query(
            "SELECT item_name, quantity, min_threshold FROM inventory WHERE min_threshold IS NOT NULL AND quantity < min_threshold ORDER BY quantity ASC",
            None,
            False,
        )

        return low_inventory if low_inventory is not None else []
    except Exception as e:
        logger.error(f"Low inventory search error: {e}")

        return []
