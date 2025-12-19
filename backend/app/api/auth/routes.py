from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.services.auth_service import authenticate_user
from app.core.database import SessionLocal

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth"
)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email y password son requeridos"
        }), 400

    db = SessionLocal()

    try:
        user_data = authenticate_user(db, email, password)

        if not user_data:
            return jsonify({
                "success": False,
                "message": "Credenciales inválidas"
            }), 401

        access_token = create_access_token(identity=user_data)

        return jsonify({
            "success": True,
            "access_token": access_token
        }), 200

    finally:
        db.close()
