import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_connection
import utils.encryption as encryption
import api.audit_log as audit_log
from utils.decorators import admin_required
import utils.validators as validators


class CurrentUser:
    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


@admin_required
def add_user(current_user, target_user, password, role, email):
    """Adds a new user

    Args:
        current_user (CurrentUser): Current user
        target_user (String): New username
        password (String): Password (unencrypted)
        role (String): New user role
        email (String): New user email address

    Raises:
        TypeError: Username is empty string
        TypeError: Password is empty string
        TypeError: Invalid role
        TypeError: Invalid email address
    """
    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Username must be non-empty string")
        if not validators.is_non_empty_string(password):
            raise TypeError("Password must be non-empty string")
        if not validators.is_valid_role(role):
            raise TypeError("Role is not valid")
        if not validators.is_valid_email(email):
            raise TypeError("Email is not valid")
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
            print("User " + target_user + " already exists, please update user instead")
        audit_log.update_audit_log(current_user, target_user, "ADD", "New user added")
    except Exception as e:
        print(f"An error occurred while entering user {e}")


@admin_required
def change_user_role(current_user, target_user, new_role):
    """Admin function to change a user's role

    Args:
        current_user (CurrentUser): Current user
        target_user (String): Target user name
        new_role (String): New role

    Raises:
        TypeError: Target user string is empty
        TypeError: Invalid role
    """
    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Target user must be non-empty string")
        if not validators.is_valid_role(new_role):
            raise TypeError("Role is not valid")
        db_connection.execute_query(
            "UPDATE users SET role = %s WHERE username = %s",
            [new_role, target_user],
        )
        print("Updated role to " + new_role)
        audit_log.update_audit_log(
            current_user, target_user, "UPDATE", "Set user role to " + new_role
        )
    except Exception as e:
        print(f"An error occurred while changing user role: {e}")


@admin_required
def delete_user(current_user, target_user):
    """Deletes a user

    Args:
        current_user (CurrentUser): Current user
        target_user (String): User to delete

    Raises:
        TypeError: Target user is empty string
    """
    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Target user must be non-empty string")
        db_connection.execute_query(
            "DELETE FROM users WHERE username = %s", [target_user]
        )
        print("User deleted")
        audit_log.update_audit_log(current_user, target_user, "DELETE", "Deleted user")
    except Exception as e:
        print(f"An error occurred while deleting user: {e}")


def login(username, password):
    """Checks for valid login, returns user object

    Args:
        username (String): Username
        password (String): Password

    Raises:
        TypeError: Username is empty string
        TypeError: Password is empty string

    Returns:
        CurrentUser or False: Returns user object if valid login, False otherwise
    """
    try:
        if not validators.is_non_empty_string(username):
            raise TypeError("Username must be non-empty string")
        if not validators.is_non_empty_string(password):
            raise TypeError("Password must be non-empty string")
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
        print(f"An error occurred while logging in: {e}")
        return False


def get_user(username):
    """Background function to get user attributes for password checking

    Args:
        username (String): User to retrieve

    Raises:
        TypeError: Username is empty string

    Returns:
        List of tuple: Returns a list with a tuple of user information
    """
    try:
        if not validators.is_non_empty_string(username):
            raise TypeError("Username must be non-empty string")
        user_list = db_connection.execute_query(
            "SELECT * FROM users WHERE username = %s", [username], False
        )
        return user_list
    except Exception as e:
        print(f"An error occurred while retrieving user: {e}")
        return


@admin_required
def view_user(current_user, target_user):
    """Admin function to view user attributes

    Args:
        current_user (CurrentUser): Current user
        target_user (String): Target user name

    Raises:
        TypeError: Target user is empty string

    Returns:
        List of tuples: Returns a list containing a tuple of user attributes
    """
    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Target user must be non-empty string")
        user_list = db_connection.execute_query(
            "SELECT * FROM users WHERE username = %s", [target_user], False
        )
        return user_list
    except Exception as e:
        print(f"An error occurred while retrieving user data: {e}")
        return


def change_user_password(current_user):
    """Changes user password

    Args:
        current_user (CurrentUser): Current user

    Raises:
        TypeError: New password is empty string
    """
    try:
        current_password = input("Verify your current password: ")
        login_check = login(current_user.username, current_password)
        if (login_check is not None) and (login_check is not False):
            new_password = input("Please enter your new password: ")
            if not validators.is_non_empty_string(new_password):
                raise TypeError("New password must be non-empty string")
            if new_password == input("Reenter your password: "):
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
            else:
                print("Passwords did not match")
        else:
            print("Password was not valid")
    except Exception as e:
        print(f"An error occurred while changing password: {e}")


def change_user_username(current_user):
    """Changes username

    Args:
        current_user (CurrentUser): Current user

    Raises:
        TypeError: New username is empty string

    Returns:
        str: New username
    """
    try:
        current_password = input("Verify your current password: ")
        login_check = login(current_user.username, current_password)
        if (login_check is not None) and (login_check is not False):
            new_username = input("Please enter your new username: ")
            if not validators.is_non_empty_string(new_username):
                raise TypeError("New username must be non-empty string")
            if new_username == input("Reenter your username: "):
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
                return new_username
            else:
                print("Usernames did not match")
                return
        else:
            print("Password was not valid")
            return
    except Exception as e:
        print(f"An error occurred while changing username: {e}")
        return


def change_user_email(current_user):
    """Changes user email address

    Args:
        current_user (CurrentUser): Current user

    Raises:
        TypeError: New email is empty string

    Returns:
        str: New username
    """
    try:
        current_password = input("Verify your current password: ")
        login_check = login(current_user.username, current_password)
        if (login_check is not None) and (login_check is not False):
            new_email = input("Please enter your new email: ")
            if not validators.is_valid_email(new_email):
                raise TypeError("Email was not valid")
            if new_email == input("Reenter your email: "):
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
                return new_email
            else:
                print("Emails did not match")
                return
        else:
            print("Password was not valid")
            return
    except Exception as e:
        print(f"An error occurred while changing email: {e}")
        return


@admin_required
def show_all_users(current_user):
    """Shows a list of all users

    Args:
        current_user (CurrentUser): Current user

    Returns:
        List of tuples: Returns a list that contains user attributes in tuples
    """
    try:
        table_contents = db_connection.execute_query(
            "SELECT username, role, email, created_at, updated_at FROM users",
            None,
            False,
        )
        return table_contents
    except Exception as e:
        print(f"Database error: {e}")
