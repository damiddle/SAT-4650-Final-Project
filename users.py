import db_connection
import encryption
import audit_log


def add_user(user, username, password, role, email):
    """Registers a new user, admin use only

    Args:
        user (CurrentUser): Current user object
        username (String): Username of the user being registered
        password (String): Unencrypted password
        role (String): Different permission levels, "Admin", "User", or "Viewer"
        email (String): Email address of user being registered
    """

    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    if user.role == "Admin":
        query = "SELECT COUNT(*) AS user_rows FROM users WHERE username = %s"
        query_list = [username]
        cursor.execute(query, query_list)
        user_name_count = cursor.fetchall()
        user_name_count = user_name_count[0][0]

        if user_name_count == 0:
            query = "INSERT INTO users (username, role, email, password_encrypted) VALUES(%s, %s, %s, %s)"
            query_list = [username, role, email, encryption.encrypt_password(password)]

            cursor.execute(query, query_list)
            print(username + " added to user database")

            connection.commit()

        else:
            print("User " + username + " already exists, please update user instead")

        cursor.close()

        audit_log.update_audit_log(user, username, "ADD", "New user added")

    else:
        print("You do not have access to this function")


def change_user_role(user, username, new_role):
    """Edit user role, admin use only

    Args:
        user (CurrentUser): Current user object
        username (String): Username of the user being edited
        new_role (String): New role, "Admin", "User", or "Viewer"
    """

    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "UPDATE users SET role = %s WHERE username = %s"
        query_list = [new_role, username]
        cursor.execute(query, query_list)
        print("Updated role to " + new_role)
        audit_log.update_audit_log(
            user, username, "UPDATE", "Set user role to " + new_role
        )

        connection.commit()
        cursor.close()

    else:
        print("Role must be 'Admin', 'User', or 'Viewer'")


def delete_user(user, username):
    """Deletes user, admin use only

    Args:
        user (CurrentUser): Current user object
        username (String): User to be deleted
    """

    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()

        query = "DELETE FROM users WHERE username = %s"
        query_list = [username]
        cursor.execute(query, query_list)
        print("User deleted")
        audit_log.update_audit_log(user, username, "DELETE", "Deleted user")

        connection.commit()
        cursor.close()

    else:
        print("You do not have access to this function")


def get_user(user):
    """Retrieves user for login, after password verification

    Args:
        user (String): Username

    Returns:
        List: User properties
    """

    connection = db_connection.connect_to_database()
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    query_list = [user]

    cursor.execute(query, query_list)
    user_list = cursor.fetchall()

    return user_list


def view_user(user, username):
    """Retrieves user view, admin use only

    Args:
        user (CurrentUser): Current user object
        username (String): Username to view

    Returns:
        List: User properties
    """

    if user.role == "Admin":
        connection = db_connection.connect_to_database()
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        query_list = [username]

        cursor.execute(query, query_list)
        user_list = cursor.fetchall()

        return user_list

    else:
        print("You don't have access to this function")
