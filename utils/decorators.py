from functools import wraps


def admin_required(func):
    @wraps(func)
    def wrapper(current_user, *args, **kwargs):
        if current_user.role != "Admin":
            print("Unauthorized access. Admins only.")
            return None
        return func(current_user, *args, **kwargs)

    return wrapper


def admin_or_user_required(func):
    @wraps(func)
    def wrapper(current_user, *args, **kwargs):
        if current_user.role not in ["Admin", "User"]:
            print("Unauthorized access. Admins or user only.")
            return None
        return func(current_user, *args, **kwargs)

    return wrapper
