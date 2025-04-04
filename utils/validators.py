import re
import os
import ast
from dotenv import load_dotenv
from datetime import datetime

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)
VALID_ROLES = ast.literal_eval(os.getenv("VALID_USER_ROLES"))


def is_non_empty_string(value):
    """Checks for non-empty string

    Args:
        value (str): String to check

    Returns:
        Boolean: False if empty string
    """
    return isinstance(value, str) and value.strip() != ""


def is_positive_int(value):
    """Checks for a positive integer

    Args:
        value (int): Integer to check

    Returns:
        bool: False if not integer or positive
    """
    try:
        return int(value) >= 0
    except (TypeError, ValueError):
        return False


def is_valid_email(email):
    """Checks email is in correct format

    Args:
        email (str): Email address

    Returns:
        bool: False if email is not valid
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_role(role):
    """Checks if role is valid

    Args:
        role (str): Role to check

    Returns:
        bool: False if not a valid role
    """
    return role in VALID_ROLES


def is_valid_date(date_string):
    """Checks if date is valid format

    Args:
        date_string (str): Date to check

    Returns:
        bool: False if not string or in correct format
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False
