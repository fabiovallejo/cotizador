from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.core.permissions import require_roles
from app.core.database import SessionLocal
from app.services.cliente_service import listar_clientes, crear_cliente
from app.serializers.cliente_serializer import cliente_to_dict

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/v1/clientes")

@clientes_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def listar():
    db = SessionLocal()
    try:
        claims = get_jwt()
        id_empresa = claims["id_empresa"]
        items = listar_clientes(db, id_empresa)
        data = [cliente_to_dict(p) for p in items]
        return jsonify({"success": True, "data": data}), 200
    finally:
        db.close()

@clientes_bp.route("/", methods=["POST"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def crear():
    claims = get_jwt()
    id_empresa = claims["id_empresa"]
    payload = request.get_json()

    if not payload:
        return jsonify({
            "success": False,
            "message": "Payload requerido"
        }), 400

    db = SessionLocal()
    try:
        cliente = crear_cliente(db, payload, id_empresa)

        if not cliente:
            return jsonify({
                "success": False,
                "message": "Documento ya existe para esta empresa"
            }), 409

        return jsonify({
            "success": True,
            "data": {
                "id_cliente": cliente.id_cliente
            }
        }), 201
    finally:
        db.close()
