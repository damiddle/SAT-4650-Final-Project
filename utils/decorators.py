"""
Module for role-based access control decorators.

Provides a decorator to restrict access to functions based on the current user's role.
"""

import api.audit_log as audit_log
from functools import wraps


def roles_required(allowed_roles):
    """Decorator to enforce role-based access to a function.

    Args:
        allowed_roles (list): A list of roles allowed to access the function.

    Returns:
        function: A wrapped function that only executes if the user's role is allowed.

    Raises:
        PermissionError: If no user is provided, if the user lacks a 'role' attribute,
                         or if the user's role is not permitted.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(current_user, *args, **kwargs):
            if current_user is None:
                print("Access denied: No user provided.")
                raise PermissionError("Access denied: No user provided.")

            if not hasattr(current_user, "role"):
                print("Access denied: Provided user object lacks 'role' attribute.")
                raise PermissionError("Access denied: Invalid user object.")

            if current_user.role not in allowed_roles:
                audit_log.update_audit_log(
                    current_user, func.__name__, "ACCESS", "Unauthorized access by user"
                )
                raise PermissionError(
                    f"Unauthorized access. Allowed roles: {allowed_roles}"
                )

            return func(current_user, *args, **kwargs)

        return wrapper

    return decorator
