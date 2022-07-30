from flask_jwt_extended import get_jwt


def admin_group_required(func):
    """To add an administrator group to the user"""
    def wrapper(*args, **kwargs):
        jwt = get_jwt()

        if "admin" in jwt.get("groups", []):
            result = func(*args, **kwargs)
            return result

        else:
            return {"message": "Forbidden"}, 403

    wrapper.__name__ = func.__name__
    return wrapper
