import db_connection
import os


def update_audit_log(user, updated_object, action_type, details):
    """Adds entry to the audit log

    Args:
        user (CurrentUser): Current user object
        updated_object (String): Username or item name of the thing being edited
        action_type (String): Action "ADD", "UPDATE", "DELETE", "LOGIN", or "LOGOUT"
        details (String): Details regarding the action
    """

    if action_type == "ADD" or "UPDATE" or "DELETE" or "LOGIN" or "LOGOUT":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "INSERT INTO audit_log (username, updated_object, action_type, details) VALUES (%s, %s, %s, %s)"
        query_list = [user.username, updated_object, action_type, details]
        cursor.execute(query, query_list)

        print("Audit log updated")

        connection.commit()
        cursor.close()

    else:
        print("Action type for audit log " + action_type + " not valid")


def pull_audit_log(user, number_of_entries):
    """Pulls the last ___ number of entries to the audit log

    Args:
        user (CurrentUser): Current user object
        number_of_entries (int): Number of entries to pull
    """

    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()
        cursor.callproc("GetLastAuditEntries", [number_of_entries])

        for result in cursor.stored_results():
            audit_entries = result.fetchall()

        print(audit_entries)

    else:
        print("You do not have access to this function")
        print("User permissions: " + user.role)


def export_to_txt(user, file_path="audit_log_export.txt"):
    """Exports audit log to .txt file

    Args:
        user (CurrentUser): Current user object
        file_path (str, optional): Local output file name. Defaults to "audit_log_export.txt".
    """

    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "SELECT log_id, username, updated_object, action_type, details, action_timestamp FROM audit_log ORDER BY action_timestamp DESC"
        cursor.execute(query)
        log = cursor.fetchall()

        with open(os.path.join(os.path.dirname(__file__), file_path), "w") as file:
            file.write(
                "Log ID | User ID | Updated Object | Action Type | Timestamp | Details\n"
            )
            file.write("-" * 80 + "\n")

            for entry in log:
                file.write(
                    f"{entry[0]} | {entry[1]} | {entry[2]} | {entry[3]} | "
                    f"{entry[4]} | {entry[5]}\n"
                )

        cursor.close()

    else:
        print("You do not have access to this file")
