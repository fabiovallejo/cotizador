from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.core.permissions import require_roles

productos_bp = Blueprint(
    "productos",
    __name__,
    url_prefix="/api/v1/productos"
)

@productos_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def listar_productos():
    return jsonify({
        "success": True,
        "data": []
    })
