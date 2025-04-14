"""
Module for audit logging.

Provides functions to update, retrieve, and export audit log entries. Audit
log operations help track user activities and database changes.
"""

import sys
import os

# Append the parent directory to the path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection
import logging
import utils.validators as validators
from utils.decorators import roles_required
from mysql.connector import Error as MySQLError

logger = logging.getLogger(__name__)


def update_audit_log(current_user, updated_object, action_type, details):
    """Updates the audit log with a new entry.

    Args:
        current_user (CurrentUser): The user performing the action.
        updated_object (str): The object or username that was updated.
        action_type (str): The type of action (ADD, UPDATE, DELETE, LOGIN, LOGOUT, ACCESS).
        details (str): Additional details about the action.

    Raises:
        TypeError: If action_type is not among the allowed types or if updated_object is empty.
        Exception: If a database error occurs.
    """

    if action_type not in {"ADD", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "ACCESS"}:
        raise TypeError(
            "Action type must be ADD, UPDATE, DELETE, LOGIN, LOGOUT, or ACCESS"
        )

    if not validators.is_non_empty_string(updated_object):
        raise TypeError("Updated object must be a non-empty string")

    try:
        db_connection.execute_query(
            "INSERT INTO audit_log (username, updated_object, action_type, details) VALUES (%s, %s, %s, %s)",
            [current_user.username, updated_object, action_type, details],
        )
    except MySQLError as e:
        logger.error(f"Database error updating audit log: {e}")
        raise


@roles_required(["Admin"])
def pull_audit_log(current_user, number_of_entries):
    """Retrieves the most recent audit log entries.

    Args:
        current_user (CurrentUser): The admin performing the operation.
        number_of_entries (int): The number of recent log entries to pull.

    Returns:
        list: A list of audit log entries.

    Raises:
        TypeError: If number_of_entries is not a positive integer.
        Exception: If a database error occurs.
    """

    connection = None
    cursor = None

    try:
        if not validators.is_positive_int(number_of_entries):
            raise TypeError("Number of entries must be a positive integer")

        connection = db_connection.get_connection()

        if connection is None:
            logger.error("Unable to establish a database connection.")
            return []

        cursor = connection.cursor()
        cursor.callproc("GetLastAuditEntries", [number_of_entries])

        result_set = []
        for item in cursor.stored_results():
            result_set = item.fetchall()

            break

        return result_set
    except MySQLError as e:
        logger.error(f"Error pulling audit log: {e}")

        return []
    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


@roles_required(["Admin"])
def export_to_txt(current_user, file_path="audit_log_export.txt"):
    """Exports the entire audit log to a text file.

    Args:
        current_user (CurrentUser): The admin performing the export.
        file_path (str, optional): The path (relative to the module) for the export file.
                                   Defaults to "audit_log_export.txt".

    Raises:
        Exception: If an error occurs during file or database operations.
    """

    try:
        log_entries = db_connection.execute_query(
            "SELECT log_id, username, updated_object, action_type, details, action_timestamp FROM audit_log ORDER BY action_timestamp DESC",
            None,
            False,
        )

        if log_entries is None:
            logger.info("No audit log entries retrieved")

            return

        export_path = os.path.join(os.path.dirname(__file__), file_path)

        with open(export_path, "w") as file:
            for entry in log_entries:
                file.write(
                    f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | Action: {entry[3]} | Details: {entry[4]} | Time: {entry[5]}\n"
                )
    except (MySQLError, IOError) as e:
        logger.error(f"Error exporting audit log: {e}")
        raise
