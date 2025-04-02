import db_connection
import utils.encryption as encryption
import api.audit_log as audit_log


class CurrentUser:
    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


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


def login(username, password):
    """Logs in a user

    Args:
        username (String): Username to verify
        password (String): Password

    Returns:
        CurrentUser or boolean: Returns a CurrentUser object if login is valid, or False if it is not
    """

    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    query = "SELECT password_encrypted FROM users WHERE username = %s"
    query_list = [username]
    cursor.execute(query, query_list)

    ref_pass = cursor.fetchone()

    if ref_pass is not None:
        if encryption.decrypt_password(ref_pass[0]) == password:
            print("Successfully logged in!")

            current_user = get_user(username)[0]

            current_user = CurrentUser(
                current_user[1], current_user[3], current_user[4]
            )

            print("Welcome " + current_user.username)
            print("Permission level: " + current_user.role)

            audit_log.update_audit_log(
                current_user, current_user.username, "LOGIN", "Logged in"
            )

            return current_user

        else:
            print("Login not valid, try again")

            return False

    else:
        print("Login not valid, try again")

        return False


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


def change_user_password(user):
    """Updates a users password

    Args:
        user (CurrentUser): Current user object
    """

    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    current_password = input("Verify your current password: ")

    if login(user.username, current_password) is not None or False:
        new_password = input("Please enter your new password: ")

        if new_password == input("Reenter your password: "):
            query = "UPDATE users SET password_encrypted = %s WHERE username = %s"
            query_list = [encryption.encrypt_password(new_password), user.username]

            cursor.execute(query, query_list)
            print("Password has been updated")
            audit_log.update_audit_log(
                user, user.username, "UPDATE", "Changed password to " + new_password
            )
            connection.commit()
            cursor.close()

        else:
            print("Passwords did not match")

    else:
        print("Password was not valid")


def change_user_username(user):
    """Changes a users username

    Args:
        user (CurrentUser): Current user object
    """
    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    current_password = input("Verify your current password: ")

    if login(user.username, current_password) is not None or False:
        new_username = input("Please enter your new username: ")

        if new_username == input("Reenter your username: "):
            query = "UPDATE users SET username = %s WHERE username = %s"
            query_list = [new_username, user.username]

            cursor.execute(query, query_list)
            print("Username has been updated")
            audit_log.update_audit_log(
                user, user.username, "UPDATE", "Changed username to " + new_username
            )
            connection.commit()
            cursor.close()

        else:
            print("Usernames did not match")

    else:
        print("Password was not valid")


def change_user_email(user):
    """Changes a users email

    Args:
        user (CurrentUser): Current user object
    """
    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    current_password = input("Verify your current password: ")

    if login(user.username, current_password) is not None or False:
        new_email = input("Please enter your new email: ")

        if new_email == input("Reenter your email: "):
            query = "UPDATE users SET email = %s WHERE username = %s"
            query_list = [new_email, user.username]

            cursor.execute(query, query_list)
            print("Email has been updated")
            audit_log.update_audit_log(
                user, user.username, "UPDATE", "Changed username to " + new_email
            )
            connection.commit()
            cursor.close()

        else:
            print("Emails did not match")

    else:
        print("Password was not valid")
