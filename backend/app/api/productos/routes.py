from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.core.permissions import require_roles
from app.core.database import SessionLocal
from app.services.producto_service import listar_productos, crear_producto
from app.serializers.producto_serializer import producto_to_dict

productos_bp = Blueprint("productos", __name__, url_prefix="/api/v1/productos")

@productos_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def get_all():
    db = SessionLocal()
    try:
        items = listar_productos(db)
        data = [producto_to_dict(p) for p in items]
        return jsonify({"success": True, "data": data}), 200
    finally:
        db.close()

@productos_bp.route("/", methods=["POST"])
@jwt_required()
@require_roles("Owner")
def crear():
    payload = request.get_json()

    if not payload:
        return jsonify({
            "success": False,
            "message": "Payload requerido"
        }), 400

    db = SessionLocal()
    try:
        producto = crear_producto(db, payload)

        if not producto:
            return jsonify({
                "success": False,
                "message": "SKU ya existe para esta empresa"
            }), 409

        return jsonify({
            "success": True,
            "data": {
                "id_producto": producto.id_producto
            }
        }), 201
    finally:
        db.close()
