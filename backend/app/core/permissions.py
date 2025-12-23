from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def require_roles(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            # Verifica que el JWT exista y sea válido
            verify_jwt_in_request()

            # Obtiene la identidad del token
            claims = get_jwt()
            roles_usuario = claims.get("roles", [])

            # Verifica si el usuario tiene al menos uno de los roles permitidos
            if not any(role in roles_usuario for role in allowed_roles):
                return jsonify({
                    "success": False,
                    "message": "No tienes permisos para esta acción"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
