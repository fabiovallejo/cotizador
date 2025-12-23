from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.core.permissions import require_roles
from app.core.database import SessionLocal
from app.services.cotizacion_service import listar_cotizaciones, crear_cotizacion, obtener_cotizacion
from app.serializers.cotizacion_serializer import cotizacion_to_dict
from app.services.cotizacion_item_service import agregar_item


cotizaciones_bp = Blueprint(
    "cotizaciones",
    __name__,
    url_prefix="/api/v1/cotizaciones"
)

@cotizaciones_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def listar():
    db = SessionLocal()
    try:
        claims = get_jwt()
        id_empresa = claims["id_empresa"]

        items = listar_cotizaciones(db, id_empresa)
        data = [cotizacion_to_dict(c) for c in items]

        return jsonify({"success": True, "data": data}), 200
    finally:
        db.close()

@cotizaciones_bp.route("/", methods=["POST"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def crear():
    payload = request.get_json()

    if not payload or "id_cliente" not in payload:
        return jsonify({
            "success": False,
            "message": "id_cliente es requerido"
        }), 400

    db = SessionLocal()
    try:
        claims = get_jwt()
        id_empresa = claims["id_empresa"]
        id_usuario = int(get_jwt_identity())

        cotizacion = crear_cotizacion(
            db,
            id_empresa=id_empresa,
            id_usuario=id_usuario,
            id_cliente=payload["id_cliente"]
        )

        return jsonify({
            "success": True,
            "data": {
                "id_cotizacion": cotizacion.id_cotizacion
            }
        }), 201
    finally:
        db.close()

@cotizaciones_bp.route("/<int:id_cotizacion>/items", methods=["POST"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def agregar_item_a_cotizacion(id_cotizacion):
    payload = request.get_json()

    if not payload:
        return jsonify({
            "success": False,
            "message": "Payload requerido"
        }), 400

    db = SessionLocal()
    try:
        item = agregar_item(db, id_cotizacion, payload)

        if not item:
            return jsonify({
                "success": False,
                "message": "Cotización o producto inválido"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id_cotizacionitem": item.id_cotizacionitem
            }
        }), 201
    
    finally:
        db.close()


@cotizaciones_bp.route("/<int:id_cotizacion>", methods=["GET"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def obtener(id_cotizacion):
    db = SessionLocal()
    try:
        claims = get_jwt()
        id_empresa = claims["id_empresa"]

        cotizacion = obtener_cotizacion(db, id_cotizacion, id_empresa)

        if not cotizacion:
            return jsonify({
                "success": False,
                "message": "Cotización no encontrada"
            }), 404

        return jsonify({
            "success": True,
            "data": cotizacion_to_dict(cotizacion)
        }), 200
    finally:
        db.close()