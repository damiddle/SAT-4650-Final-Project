import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_connection
from utils.decorators import roles_required
import utils.validators as validators
from mysql.connector import Error as MySQLError


def update_audit_log(current_user, updated_object, action_type, details):
    """Updates the audit log

    Args:
        current_user (CurrentUser): Current user
        updated_object (String): Object that is being updated (item or user)
        action_type (String): ADD, UPDATE, DELETE, LOGIN, or LOGOUT
        details (String): Additional details

    Raises:
        TypeError: Action type is not ADD, UPDATE, DELETE, LOGIN, or LOGOUT
        TypeError: Updated object is empty string
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
        print("Audit log updated")
    except MySQLError as e:
        print(f"Database error occurred while updating the audit log: {e}")


@roles_required(["Admin"])
def pull_audit_log(current_user, number_of_entries):
    """Retrieves ___ number of recent entries to the audit log

    Args:
        current_user (CurrentUser): Current user
        number_of_entries (int): Number of recent entries to pull

    Raises:
        TypeError: Number of entries is non-positive integer

    Returns:
        List of tuples: List of audit log entries in tuples
    """
    if not validators.is_positive_int(number_of_entries):
        raise TypeError("Number of entries must be a positive integer")
    try:
        connection = db_connection.get_connection()
        if connection is None:
            print("Unable to establish a database connection.")
            return []
        cursor = connection.cursor()
        cursor.callproc("GetLastAuditEntries", [number_of_entries])

        result_set = []
        for item in cursor.stored_results():
            result_set = item.fetchall()
            break
        return result_set
    except MySQLError as e:
        print(f"Error occurred while pulling results from audit log: {e}")
        return
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@roles_required(["Admin"])
def export_to_txt(current_user, file_path="audit_log_export.txt"):
    """Exports audit log to .txt file

    Args:
        user (CurrentUser): Current user object
        file_path (str, optional): Local output file name. Defaults to "audit_log_export.txt".
    """
    try:
        log_entries = db_connection.execute_query(
            "SELECT log_id, username, updated_object, action_type, details, action_timestamp FROM audit_log ORDER BY action_timestamp DESC",
            None,
            False,
        )
        if log_entries is None:
            print("No audit log entries retrieved")
            return
        export_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(export_path, "w") as file:
            for entry in log_entries:
                file.write(
                    f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | Action: {entry[3]} | Details: {entry[5]} | Time: {entry[4]}\n"
                )
    except (MySQLError, IOError) as e:
        print(f"Error occurred while exporting audit log to .txt file: {e}")
