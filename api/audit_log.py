import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection


def update_audit_log(current_user, updated_object, action_type, details):
    """Adds entry to the audit log

    Args:
        current_user (CurrentUser): Current user object
        updated_object (String): Username or item name of the thing being edited
        action_type (String): Action "ADD", "UPDATE", "DELETE", "LOGIN", or "LOGOUT"
        details (String): Details regarding the action
    """

    if action_type in {"ADD", "UPDATE", "DELETE", "LOGIN", "LOGOUT"}:
        try:
            db_connection.execute_query(
                "INSERT INTO audit_log (username, updated_object, action_type, details) VALUES (%s, %s, %s, %s)",
                [current_user.username, updated_object, action_type, details],
            )

            print("Audit log updated")

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("Action type for audit log " + action_type + " not valid")


def pull_audit_log(current_user, number_of_entries):
    """Pulls the last ___ number of entries to the audit log

    Args:
        user (CurrentUser): Current user object
        number_of_entries (int): Number of entries to pull
    """

    if current_user.role == "Admin":
        try:
            connection = db_connection.connect_to_database()
            cursor = connection.cursor()
            cursor.callproc("GetLastAuditEntries", [number_of_entries])

            results = cursor.stored_results()

            for item in results:
                entry = item.fetchall()

            return entry

        except Exception as e:
            print(f"Database error: {e}")

            return

    else:
        print("You do not have access to this function")

        return


def export_to_txt(current_user, file_path="audit_log_export.txt"):
    """Exports audit log to .txt file

    Args:
        user (CurrentUser): Current user object
        file_path (str, optional): Local output file name. Defaults to "audit_log_export.txt".
    """

    if current_user.role == "Admin":
        try:
            log = db_connection.execute_query(
                "SELECT log_id, username, updated_object, action_type, details, action_timestamp FROM audit_log ORDER BY action_timestamp DESC",
                None,
                False,
            )

            with open(os.path.join(os.path.dirname(__file__), file_path), "w") as file:
                for entry in log:
                    file.write(
                        f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | Action: {entry[3]} | Details: {entry[5]} | Time: {entry[4]}\n"
                    )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this file")
