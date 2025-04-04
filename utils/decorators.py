from functools import wraps
import api.audit_log as audit_log


def roles_required(allowed_roles):
    """
    A dynamic decorator that restricts access to functions based on allowed user roles.

    Args:
        allowed_roles (list or tuple): Allowed roles for accessing the decorated function.

    Raises:
        PermissionError: If current_user is None, missing a 'role' attribute, or if the role is not allowed.
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
