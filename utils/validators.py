"""
Module for validating input data.

Provides helper functions to validate strings, integers, emails, roles, and dates.
"""

import re
import os
import ast
from dotenv import load_dotenv
from datetime import datetime

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)
VALID_ROLES = ast.literal_eval(os.getenv("VALID_USER_ROLES"))


def is_non_empty_string(value):
    """Checks if the given value is a non-empty string.

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if value is a non-empty string, False otherwise.
    """

    return isinstance(value, str) and value.strip() != ""


def is_positive_int(value):
    """Checks if the value is a positive integer (zero or greater).

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if value is a positive integer, False otherwise.
    """

    try:
        return int(value) >= 0
    except (TypeError, ValueError):
        return False


def is_valid_email(email):
    """Validates whether an email address is in the proper format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email matches the expected pattern, False otherwise.
    """

    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_role(role):
    """Checks if the role is one of the allowed roles.

    Args:
        role (str): The role to validate.

    Returns:
        bool: True if role is in the VALID_ROLES list, False otherwise.
    """

    return role in VALID_ROLES


def is_valid_date(date_string):
    """Validates a date string against the YYYY-MM-DD format.

    Args:
        date_string (str): The date string to validate.

    Returns:
        bool: True if date_string is valid, False otherwise.
    """

    try:
        datetime.strptime(date_string, "%Y-%m-%d")

        return True
    except (ValueError, TypeError):
        return False
