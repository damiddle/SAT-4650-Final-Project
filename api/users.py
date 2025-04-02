import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection
import utils.encryption as encryption
import api.audit_log as audit_log


class CurrentUser:
    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


def add_user(current_user, target_user, password, role, email):
    """Registers a new user, admin use only

    Args:
        current_user (CurrentUser): Current user object
        target_user (String): Username of the user being registered
        password (String): Unencrypted password
        role (String): Different permission levels, "Admin", "User", or "Viewer"
        email (String): Email address of user being registered
    """

    if current_user.role == "Admin":
        try:
            user_name_count = db_connection.execute_query(
                "SELECT COUNT(*) AS user_rows FROM users WHERE username = %s",
                [target_user],
                False,
            )
            user_name_count = user_name_count[0][0]

            if user_name_count == 0:
                db_connection.execute_query(
                    "INSERT INTO users (username, role, email, password_encrypted) VALUES(%s, %s, %s, %s)",
                    [
                        target_user,
                        role,
                        email,
                        encryption.encrypt_data(password),
                    ],
                )
                print(target_user + " added to user database")

            else:
                print(
                    "User "
                    + target_user
                    + " already exists, please update user instead"
                )

            audit_log.update_audit_log(
                current_user, target_user, "ADD", "New user added"
            )

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def change_user_role(current_user, target_user, new_role):
    """Edit user role, admin use only

    Args:
        current_user (CurrentUser): Current user object
        target_user (String): Username of the user being edited
        new_role (String): New role, "Admin", "User", or "Viewer"
    """

    if current_user.role == "Admin":
        try:
            if new_role not in db_connection.VALID_USER_ROLES:
                db_connection.execute_query(
                    "UPDATE users SET role = %s WHERE username = %s",
                    [new_role, target_user],
                )
                print("Updated role to " + new_role)
                audit_log.update_audit_log(
                    current_user, target_user, "UPDATE", "Set user role to " + new_role
                )

            else:
                print(new_role + " is not a valid role")

        except Exception as e:
            print(f"Database error: {e}")

    else:
        print("You do not have access to this function")


def delete_user(current_user, target_user):
    """Deletes user, admin use only

    Args:
        current_user (CurrentUser): Current user object
        target_user (String): User to be deleted
    """

    if current_user.role == "Admin":
        try:
            db_connection.execute_query(
                "DELETE FROM users WHERE username = %s", [target_user]
            )
            print("User deleted")

            audit_log.update_audit_log(
                current_user, target_user, "DELETE", "Deleted user"
            )
        except Exception as e:
            print(f"Database error: {e}")

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
    try:
        ref_pass = db_connection.execute_query(
            "SELECT password_encrypted FROM users WHERE username = %s",
            [username],
            False,
        )

        if ref_pass is not None:
            if encryption.decrypt_data(ref_pass[0][0]) == password:
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

    except Exception as e:
        print(f"Database error: {e}")

        return False


def get_user(username):
    """Retrieves user for login to form the CurrentUser object after password verification

    Args:
        username (String): Username

    Returns:
        List: User properties
    """

    try:
        user_list = db_connection.execute_query(
            "SELECT * FROM users WHERE username = %s", [username], False
        )

        return user_list

    except Exception as e:
        print(f"Database error: {e}")

        return


def view_user(current_user, target_user):
    """Retrieves user view, admin use only

    Args:
        current_user (CurrentUser): Current user object
        target_user (String): Username to view

    Returns:
        List: User properties
    """

    if current_user.role == "Admin":
        try:
            user_list = db_connection.execute_query(
                "SELECT * FROM users WHERE username = %s", [target_user], False
            )

            return user_list

        except Exception as e:
            print(f"Database error: {e}")

            return

    else:
        print("You don't have access to this function")

        return


def change_user_password(current_user):
    """Updates a users password

    Args:
        current_user (CurrentUser): Current user object
    """

    current_password = input("Verify your current password: ")
    login_check = login(current_user.username, current_password)
    if (login_check is not None) and (login_check is not False):
        new_password = input("Please enter your new password: ")

        if new_password == input("Reenter your password: "):
            try:
                db_connection.execute_query(
                    "UPDATE users SET password_encrypted = %s WHERE username = %s",
                    [
                        encryption.encrypt_data(new_password),
                        current_user.username,
                    ],
                )
                print("Password has been updated")
                audit_log.update_audit_log(
                    current_user, current_user.username, "UPDATE", "Changed password"
                )

            except Exception as e:
                print(f"Database error: {e}")

        else:
            print("Passwords did not match")

    else:
        print("Password was not valid")


def change_user_username(current_user):
    """Changes a users username

    Args:
        current_user (CurrentUser): Current user object
    """

    current_password = input("Verify your current password: ")
    login_check = login(current_user.username, current_password)

    if (login_check is not None) and (login_check is not False):
        new_username = input("Please enter your new username: ")

        if new_username == input("Reenter your username: "):
            try:
                db_connection.execute_query(
                    "UPDATE users SET username = %s WHERE username = %s",
                    [new_username, current_user.username],
                )
                print("Username has been updated")
                audit_log.update_audit_log(
                    current_user,
                    current_user.username,
                    "UPDATE",
                    "Changed username to " + new_username,
                )

            except Exception as e:
                print(f"Database error: {e}")

        else:
            print("Usernames did not match")

    else:
        print("Password was not valid")


def change_user_email(current_user):
    """Changes a users email

    Args:
        current_user (CurrentUser): Current user object
    """

    current_password = input("Verify your current password: ")
    login_check = login(current_user.username, current_password)

    if (login_check is not None) and (login_check is not False):
        new_email = input("Please enter your new email: ")

        if new_email == input("Reenter your email: "):
            try:
                db_connection.execute_query(
                    "UPDATE users SET email = %s WHERE username = %s",
                    [new_email, current_user.username],
                )
                print("Email has been updated")
                audit_log.update_audit_log(
                    current_user,
                    current_user.username,
                    "UPDATE",
                    "Changed email to " + new_email,
                )

            except Exception as e:
                print(f"Database error: {e}")

        else:
            print("Emails did not match")

    else:
        print("Password was not valid")


def show_all_users(current_user):
    if current_user.role == "Admin":
        try:
            table_contents = db_connection.execute_query(
                "SELECT username, role, email, created_at, updated_at FROM users",
                None,
                False,
            )

            return table_contents

        except Exception as e:
            print(f"Database error: {e}")
