from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt


def role_required(*roles):

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            payload = get_jwt()
            user_role = payload.get("role")

            if user_role not in roles:
                return (
                    jsonify(
                        {
                            "error": "Forbidden",
                            "message": f"This action requires one of these roles: {list(roles)}",
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
