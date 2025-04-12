"""
Module for user management operations.

This module provides functions for user authentication and administration,
including adding, updating, and deleting users. It also handles audit log updates.
"""

import os
import sys

# Append the parent directory to the system path for module resolution.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_connection
import utils.encryption as encryption
import api.audit_log as audit_log
import utils.validators as validators
from utils.decorators import roles_required
from mysql.connector import Error as MySQLError


class CurrentUser:
    """Represents a currently logged-in user.

    Attributes:
        username (str): The username of the current user.
        role (str): The role (e.g., Admin, User, Viewer) of the current user.
        email (str): The email address of the current user.
    """

    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


@roles_required(["Admin"])
def add_user(current_user, target_user, password, role, email):
    """Adds a new user to the system.

    Checks if the target username is unique and valid, then adds the user with
    the provided password (encrypted) and role. Also updates the audit log.

    Args:
        current_user (CurrentUser): The user performing the operation.
        target_user (str): The username of the new user.
        password (str): The plain-text password for the new user.
        role (str): The role to assign to the new user.
        email (str): The email address of the new user.

    Raises:
        TypeError: If any of the parameters are invalid.
        Exception: If an error occurs during database operations.
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

        else:
            print("User " + target_user + " already exists, please update user instead")
        audit_log.update_audit_log(current_user, target_user, "ADD", "New user added")
    except (MySQLError, Exception) as e:
        print(f"An error occurred while entering user {e}")


@roles_required(["Admin"])
def change_user_role(current_user, target_user, new_role):
    """Changes the role of an existing user.

    Args:
        current_user (CurrentUser): The admin performing the operation.
        target_user (str): The username of the target user.
        new_role (str): The new role to assign.

    Raises:
        TypeError: If target_user or new_role is invalid.
        Exception: If an error occurs during database operations.
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

        audit_log.update_audit_log(
            current_user, target_user, "UPDATE", "Set user role to " + new_role
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while changing user role: {e}")


@roles_required(["Admin"])
def delete_user(current_user, target_user):
    """Deletes a user from the system.

    Args:
        current_user (CurrentUser): The admin executing the deletion.
        target_user (str): The username of the user to delete.

    Raises:
        TypeError: If target_user is not a non-empty string.
        Exception: If an error occurs during database operations.
    """

    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Target user must be non-empty string")

        db_connection.execute_query(
            "DELETE FROM users WHERE username = %s", [target_user]
        )

        audit_log.update_audit_log(current_user, target_user, "DELETE", "Deleted user")
    except (MySQLError, Exception) as e:
        print(f"An error occurred while deleting user: {e}")


def login(username, password):
    """Authenticates a user using username and password.

    Retrieves user details from the database, verifies the password by decrypting
    the stored password, and returns a CurrentUser instance on successful login.

    Args:
        username (str): The username for login.
        password (str): The plain-text password for login.

    Returns:
        CurrentUser: The logged-in user's object if credentials are valid.
        bool: False if authentication fails.

    Raises:
        TypeError: If username or password is invalid.
        Exception: If an error occurs during the authentication process.
    """

    try:
        if not validators.is_non_empty_string(username):
            raise TypeError("Username must be non-empty string")

        if not validators.is_non_empty_string(password):
            raise TypeError("Password must be non-empty string")

        user_details = db_connection.execute_query(
            "SELECT password_encrypted FROM users WHERE username = %s",
            [username],
            False,
        )

        if user_details and len(user_details) > 0:
            if encryption.decrypt_data(user_details[0][0]) == password:
                current_user = get_user(username)[0]
                current_user = CurrentUser(
                    current_user[1], current_user[3], current_user[4]
                )
                audit_log.update_audit_log(
                    current_user, current_user.username, "LOGIN", "Logged in"
                )

                return current_user

            else:
                return False
        else:
            return False
    except (MySQLError, Exception) as e:
        print(f"An error occurred while logging in: {e}")

        return False


def get_user(username):
    """Retrieves user details from the database for a given username.

    Args:
        username (str): The username to retrieve.

    Returns:
        list: A list containing user details or an empty list if not found.

    Raises:
        TypeError: If username is not a non-empty string.
        Exception: If a database error occurs.
    """

    try:
        if not validators.is_non_empty_string(username):
            raise TypeError("Username must be non-empty string")

        user_list = db_connection.execute_query(
            "SELECT * FROM users WHERE username = %s", [username], False
        )

        return user_list
    except (MySQLError, Exception) as e:
        print(f"An error occurred while retrieving user: {e}")

        return []


@roles_required(["Admin"])
def view_user(current_user, target_user):
    """Retrieves details of a user by username.

    Args:
        current_user (CurrentUser): The admin performing the operation.
        target_user (str): The username of the user to view.

    Returns:
        list: A list of details for the specified user.
              Returns an empty list if any error occurs.

    Raises:
        TypeError: If target_user is invalid.
        Exception: For errors during database access.
    """

    try:
        if not validators.is_non_empty_string(target_user):
            raise TypeError("Target user must be non-empty string")

        user_list = db_connection.execute_query(
            "SELECT user_id, username, role, email, created_at, updated_at FROM users WHERE username = %s",
            [target_user],
            False,
        )

        return user_list
    except (MySQLError, Exception) as e:
        print(f"An error occurred while retrieving user data: {e}")

        return []


def change_user_password(current_user, new_password):
    """Changes the password of the current user.

    Args:
        current_user (CurrentUser): The user who requests the password change.
        new_password (str): The new password (plain text).

    Raises:
        TypeError: If new_password is not a non-empty string.
        Exception: If an error occurs during the database update.
    """

    try:
        if not validators.is_non_empty_string(new_password):
            raise TypeError("Password must be non-empty string")

        db_connection.execute_query(
            "UPDATE users SET password_encrypted = %s WHERE username = %s",
            [encryption.encrypt_data(new_password), current_user.username],
        )

        audit_log.update_audit_log(
            current_user,
            current_user.username,
            "UPDATE",
            "Changed password to " + new_password,
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while changing password: {e}")


def change_user_username(current_user, new_username):
    """Changes the username of the current user.

    Args:
        current_user (CurrentUser): The user requesting the change.
        new_username (str): The new username.

    Raises:
        TypeError: If new_username is not a non-empty string.
        Exception: If an error occurs during the database update.
    """

    try:
        if not validators.is_non_empty_string(new_username):
            raise TypeError("Username must be non-empty string")

        db_connection.execute_query(
            "UPDATE users SET username = %s WHERE username = %s",
            [new_username, current_user.username],
        )

        audit_log.update_audit_log(
            current_user,
            current_user.username,
            "UPDATE",
            "Changed username to " + new_username,
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while changing username: {e}")


def change_user_email(current_user, new_email):
    """Changes the email address of the current user.

    Args:
        current_user (CurrentUser): The user requesting the change.
        new_email (str): The new email address.

    Raises:
        TypeError: If new_email is not valid.
        Exception: If an error occurs during the database update.
    """

    try:
        if not validators.is_valid_email(new_email):
            raise TypeError("Username must be non-empty string")

        db_connection.execute_query(
            "UPDATE users SET email = %s WHERE username = %s",
            [new_email, current_user.username],
        )

        audit_log.update_audit_log(
            current_user,
            current_user.username,
            "UPDATE",
            "Changed email to " + new_email,
        )
    except (MySQLError, Exception) as e:
        print(f"An error occurred while changing email: {e}")


@roles_required(["Admin"])
def show_all_users(current_user):
    """Retrieves the details of all users in the system.

    Args:
        current_user (CurrentUser): The admin requesting this list.

    Returns:
        list: A list containing the details of all users.
              Returns an empty list if any error occurs.
    """

    try:
        table_contents = db_connection.execute_query(
            "SELECT user_id, username, role, email, created_at, updated_at FROM users",
            None,
            False,
        )

        return table_contents
    except (MySQLError, Exception) as e:
        print(f"Database error: {e}")

        return []
