from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.core.permissions import require_roles
from app.core.database import SessionLocal
from app.services.cotizacion_service import listar_cotizaciones, crear_cotizacion, obtener_cotizacion, cerrar_cotizacion
from app.services.cotizacion_item_service import actualizar_item, eliminar_item
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
        item, error = agregar_item(db, id_cotizacion, payload)

        if error == "COTIZACION_CERRADA":
            return jsonify({
                "success": False,
                "message": "La cotización está cerrada y no se puede modificar"
            }), 409
        
        if error == "NO_EXISTE":
            return jsonify({
                "success": False,
                "message": "Cotización no encontrada"
            }), 404

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

@cotizaciones_bp.route("/<int:id_cotizacion>/cerrar", methods=["PUT"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def cerrar(id_cotizacion):
    db = SessionLocal()
    try:
        claims = get_jwt()
        id_empresa = claims["id_empresa"]

        cotizacion, error = cerrar_cotizacion(db, id_cotizacion, id_empresa)

        if error == "NO_EXISTE":
            return jsonify({
                "success": False,
                "message": "Cotización no encontrada"
            }), 404

        if error == "YA_CERRADA":
            return jsonify({
                "success": False,
                "message": "La cotización ya está cerrada"
            }), 409

        if error == "SIN_ITEMS":
            return jsonify({
                "success": False,
                "message": "No se puede cerrar una cotización sin items"
            }), 400

        return jsonify({
            "success": True,
            "message": "Cotización cerrada correctamente"
        }), 200

    finally:
        db.close()

@cotizaciones_bp.route("/<int:id_cotizacion>/items/<int:id_item>", methods=["PUT"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def actualizar_item_route(id_cotizacion, id_item):
    payload = request.get_json()

    if not payload or "cantidad" not in payload:
        return jsonify({
            "success": False,
            "message": "cantidad es requerida"
        }), 400

    db = SessionLocal()
    try:
        item, error = actualizar_item(
            db,
            id_cotizacion,
            id_item,
            payload["cantidad"]
        )

        if error == "CANTIDAD_INVALIDA":
            return jsonify({"success": False, "message": "Cantidad inválida"}), 400
        if error == "COTIZACION_CERRADA":
            return jsonify({"success": False, "message": "Cotización cerrada"}), 409
        if error in ["NO_EXISTE", "ITEM_NO_EXISTE"]:
            return jsonify({"success": False, "message": "No encontrado"}), 404

        return jsonify({
            "success": True,
            "message": "Item actualizado correctamente"
        }), 200
    finally:
        db.close()

@cotizaciones_bp.route("/<int:id_cotizacion>/items/<int:id_item>", methods=["DELETE"])
@jwt_required()
@require_roles("Owner", "Cotizador")
def eliminar_item_route(id_cotizacion, id_item):
    db = SessionLocal()
    try:
        error = eliminar_item(db, id_cotizacion, id_item)

        if error == "COTIZACION_CERRADA":
            return jsonify({"success": False, "message": "Cotización cerrada"}), 409
        if error in ["NO_EXISTE", "ITEM_NO_EXISTE"]:
            return jsonify({"success": False, "message": "No encontrado"}), 404

        return jsonify({
            "success": True,
            "message": "Item eliminado correctamente"
        }), 200
    finally:
        db.close()
